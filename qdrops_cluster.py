#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qdrops_cluster.py  --  Topic-cluster the QAnon "drops" for the dossier explorer page.

FIXED in this version
---------------------
The dataset's top level is an OBJECT with a single "posts" key whose value is the
array of drops:  {"posts": [ {...}, {...}, ... ]}.  The previous version iterated the
object directly (which yields the one key string "posts"), saw "1 record", kept 0
drops, and handed an empty list to BERTopic -> "iterable only contains strings".
We now read data["posts"] (with a robust fallback), parse the real flat fields
(author / post_id / time / text), and skip only image-only / empty posts.

Schema (per https://github.com/jkingsman/JSON-QAnon):
  each post: { "author", "author_id", "post_id", "tripcode"?, "source",
               "time" (epoch int), "text"? (str), "images"?[], "referenced_posts"?[] }
  `text` is optional (image-only drops have none); newlines are literal "\\n".

WHAT THIS DOES
--------------
1. Downloads the research-only Q-drops dataset (jkingsman/JSON-QAnon).
2. Reads data["posts"], normalises it, keeps the drops that contain text.
3. Embeds each drop, then lets the clusters form themselves.
4. Labels every cluster with its most distinctive words.
5. Writes `qdrops_clustered.json` (consumed by drops.html) + `*_topics_summary.csv`.

WHY NOT k-NN?  k-NN is a *supervised* classifier; it needs labels and cannot discover
topics. To let clusters self-form on short, cryptic text the modern approach is:
        sentence embeddings -> UMAP (reduce) -> HDBSCAN (density clustering)
HDBSCAN picks the topic count itself and puts true outliers in a noise bucket (-1).
BERTopic wraps this and names topics with class-based TF-IDF. (Default: --method bertopic.)
The only legitimate k-NN-for-clustering route is a k-NN graph + Leiden/Louvain community
detection; a plain TF-IDF + KMeans baseline (--method kmeans, no torch) is also included.

USAGE
-----
    pip install -r requirements.txt
    python qdrops_cluster.py --inspect          # just print the data structure & a sample
    python qdrops_cluster.py                     # recommended: BERTopic (auto-downloads)
    python qdrops_cluster.py --method hdbscan     # embeddings + UMAP + HDBSCAN, no BERTopic
    python qdrops_cluster.py --method kmeans -k 14 # quick baseline, no embedding model
Then copy qdrops_clustered.json next to drops.html and reload the page.

Dataset: Kingsman, J. (2025) JSON-QAnon, DOI 10.13140/RG.2.2.28778.32964 — research only.
"""

import argparse
import csv
import json
import os
import re
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timezone

RAW_URL = "https://raw.githubusercontent.com/jkingsman/JSON-QAnon/main/posts.json"
DEFAULT_INPUT = "posts.json"
DEFAULT_OUTPUT = "qdrops_clustered.json"
EMBED_MODEL = "all-MiniLM-L6-v2"   # small, fast, good for short text
SEED = 42


# --------------------------------------------------------------------------------------
# 1. ACQUIRE
# --------------------------------------------------------------------------------------
def download_dataset(path: str) -> None:
    if os.path.exists(path):
        print(f"[data] using cached {path}")
        return
    print(f"[data] downloading {RAW_URL}")
    req = urllib.request.Request(RAW_URL, headers={"User-Agent": "qdrops-research/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(path, "wb") as f:
        f.write(r.read())
    print(f"[data] saved -> {path} ({os.path.getsize(path)/1e6:.1f} MB)")


# --------------------------------------------------------------------------------------
# 2. LOAD + COERCE TO A LIST OF POSTS  (this is the part that was broken)
# --------------------------------------------------------------------------------------
def coerce_posts(data):
    """The canonical shape is {"posts": [...]}, but be robust to a few variants."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # 1) canonical / common wrapper keys
        for key in ("posts", "drops", "data", "records", "items"):
            if isinstance(data.get(key), list):
                return data[key]
        # 2) a dict whose values are post objects  ({id: {...}, ...})
        vals = list(data.values())
        if vals and all(isinstance(v, dict) for v in vals):
            return vals
        # 3) exactly one value that is a list
        list_vals = [v for v in data.values() if isinstance(v, list)]
        if len(list_vals) == 1:
            return list_vals[0]
    raise ValueError(
        "Could not locate the list of posts. Run with --inspect to see the structure."
    )


def inspect_structure(data):
    print("---- DATA STRUCTURE ----")
    print("top-level type:", type(data).__name__)
    if isinstance(data, dict):
        print("top-level keys:", list(data.keys())[:25])
    try:
        posts = coerce_posts(data)
    except ValueError as e:
        print("!!", e)
        return
    print("posts found:", len(posts))
    if posts:
        p0 = posts[0]
        print("first post type:", type(p0).__name__)
        if isinstance(p0, dict):
            print("first post keys:", list(p0.keys()))
            print("  author   :", p0.get("author"))
            print("  post_id  :", p0.get("post_id") or p0.get("id"))
            print("  time     :", p0.get("time"))
            txt = (p0.get("text") or "")
            print("  text[:200]:", repr(txt[:200]))
    print("------------------------")


# --------------------------------------------------------------------------------------
# 3. NORMALISE  (fields are FLAT on each post; some helpers stay defensive)
# --------------------------------------------------------------------------------------
def _meta(post: dict) -> dict:
    # fields are flat in JSON-QAnon, but tolerate an older nested layout just in case
    return post.get("post_metadata") or post.get("metadata") or post


def _get_id(post: dict):
    m = _meta(post)
    for k in ("post_id", "id", "no", "n"):
        v = m.get(k, post.get(k))
        if v is not None:
            return v
    return None


def _get_author(post: dict) -> str:
    m = _meta(post)
    return str(m.get("author") or post.get("author") or "").strip()


def _get_time(post: dict):
    m = _meta(post)
    for k in ("time", "timestamp", "datetime", "date"):
        v = m.get(k, post.get(k))
        if v is None:
            continue
        if isinstance(v, (int, float)) or (isinstance(v, str) and v.strip().isdigit()):
            try:
                return datetime.fromtimestamp(int(float(v)), tz=timezone.utc)
            except (ValueError, OSError, OverflowError):
                pass
        if isinstance(v, str):
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    return datetime.strptime(v[:19], fmt).replace(tzinfo=timezone.utc)
                except ValueError:
                    continue
    return None


def _get_text(post: dict) -> str:
    t = post.get("text")
    if t is None:
        t = _meta(post).get("text")
    return t or ""


URL_RE = re.compile(r"https?://\S+")
WS_RE = re.compile(r"\s+")


def clean_for_embedding(text: str) -> str:
    """Light cleaning for the model; the *display* copy keeps the original text."""
    text = URL_RE.sub(" ", text)
    text = re.sub(r">>\d+", " ", text)               # board references like >>8251669
    text = re.sub(r"[>#*`~_]+", " ", text)            # imageboard / markdown noise
    text = re.sub(r"!{2,}\S+", " ", text)             # tripcodes like !!Hs1Jq13jV6
    text = WS_RE.sub(" ", text)
    return text.strip()


def normalise(posts: list, author_filter: str = None) -> list:
    """Keep every post that has usable text. The `.posts` array IS Q's drop set, so we
    do NOT filter by author by default (matching the dataset's own extraction).
    Pass author_filter='Q' to keep only author==Q if you want a stricter set."""
    rows, no_text, filtered = [], 0, 0
    for p in posts:
        if not isinstance(p, dict):
            continue
        author = _get_author(p)
        if author_filter and author.lower() != author_filter.lower():
            filtered += 1
            continue
        raw = _get_text(p).strip()
        clean = clean_for_embedding(raw)
        if len(clean) < 3:        # image-only / pure-reference drops can't be modelled
            no_text += 1
            continue
        dt = _get_time(p)
        rows.append({
            "id": _get_id(p),
            "author": author or None,
            "date": dt.strftime("%Y-%m-%d") if dt else None,
            "year": dt.year if dt else None,
            "text": raw,           # shown verbatim in the reader
            "_clean": clean,       # fed to the embedder only
        })
    msg = f"[norm] kept {len(rows)} text drops; skipped {no_text} (image-only / empty)"
    if author_filter:
        msg += f"; filtered {filtered} (author != {author_filter})"
    print(msg)
    return rows


# --------------------------------------------------------------------------------------
# 4a. CLUSTER -- BERTopic (recommended default)
# --------------------------------------------------------------------------------------
def run_bertopic(docs, min_cluster_size, model=EMBED_MODEL, reduce_outliers=False):
    from bertopic import BERTopic
    from bertopic.vectorizers import ClassTfidfTransformer
    from sentence_transformers import SentenceTransformer
    from sklearn.feature_extraction.text import CountVectorizer
    from umap import UMAP
    from hdbscan import HDBSCAN

    print(f"[embed] {model}  ({len(docs)} drops)")
    embedder = SentenceTransformer(model)
    embeddings = embedder.encode(docs, show_progress_bar=True, batch_size=64)

    umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0,
                      metric="cosine", random_state=SEED)
    hdbscan_model = HDBSCAN(min_cluster_size=min_cluster_size, metric="euclidean",
                            cluster_selection_method="eom", prediction_data=True)

    # IMPORTANT: BERTopic's default labeller keeps stopwords ("the, of, to"). Give it a
    # stopword-aware n-gram vectorizer + frequent-word-dampened c-TF-IDF so topic labels
    # are meaningful (e.g. "covid 19 virus lockdown" instead of "the to of is").
    vectorizer_model = CountVectorizer(stop_words="english", ngram_range=(1, 2), min_df=2)
    ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)

    topic_model = BERTopic(embedding_model=embedder, umap_model=umap_model,
                           hdbscan_model=hdbscan_model, vectorizer_model=vectorizer_model,
                           ctfidf_model=ctfidf_model, calculate_probabilities=False,
                           verbose=True)
    print("[cluster] BERTopic fit (clusters self-select via HDBSCAN)...")
    topics, _ = topic_model.fit_transform(docs, embeddings)
    topics = list(topics)

    if reduce_outliers:
        print("[cluster] reducing outliers (reassigning noise -> nearest topic)...")
        try:
            new_topics = topic_model.reduce_outliers(docs, topics, strategy="c-tf-idf")
            topic_model.update_topics(docs, topics=new_topics,
                                      vectorizer_model=vectorizer_model,
                                      ctfidf_model=ctfidf_model)
            topics = list(new_topics)
        except Exception as e:  # noqa: BLE001
            print("   [warn] reduce_outliers failed, keeping original topics:", e)

    labels, keywords = {}, {}
    for tid in set(topics):
        words = [w for w, _ in (topic_model.get_topic(tid) or []) if w][:8]
        keywords[tid] = words
        labels[tid] = "noise / outliers" if tid == -1 else (" · ".join(words[:3]) or f"topic {tid}")

    coords2d = _project_2d(embeddings)
    probs = getattr(topic_model.hdbscan_model, "probabilities_", None)
    conf = ([float(x) for x in probs] if probs is not None and len(probs) == len(docs)
            else [0.0] * len(docs))
    return topics, labels, keywords, coords2d, conf


# --------------------------------------------------------------------------------------
# 4b. CLUSTER -- embeddings + UMAP + HDBSCAN by hand (no BERTopic)
# --------------------------------------------------------------------------------------
def run_hdbscan(docs, min_cluster_size, model=EMBED_MODEL):
    from sentence_transformers import SentenceTransformer
    from umap import UMAP
    from hdbscan import HDBSCAN

    print(f"[embed] {model}  ({len(docs)} drops)")
    embedder = SentenceTransformer(model)
    embeddings = embedder.encode(docs, show_progress_bar=True, batch_size=64)

    print("[cluster] UMAP(5d) -> HDBSCAN ...")
    reduced = UMAP(n_neighbors=15, n_components=5, min_dist=0.0,
                   metric="cosine", random_state=SEED).fit_transform(embeddings)
    clusterer = HDBSCAN(min_cluster_size=min_cluster_size, metric="euclidean",
                        cluster_selection_method="eom")
    topics = list(clusterer.fit_predict(reduced))

    keywords = _ctfidf_keywords(docs, topics)
    labels = {tid: ("noise / outliers" if tid == -1 else " · ".join(kw[:3]))
              for tid, kw in keywords.items()}
    coords2d = _project_2d(embeddings)
    probs = getattr(clusterer, "probabilities_", None)
    conf = ([float(x) for x in probs] if probs is not None else [0.0] * len(docs))
    return topics, labels, keywords, coords2d, conf


# --------------------------------------------------------------------------------------
# 4c. CLUSTER -- TF-IDF + KMeans baseline (no embedding model / torch required)
# --------------------------------------------------------------------------------------
def run_kmeans(docs, k):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.decomposition import TruncatedSVD

    print(f"[cluster] TF-IDF -> KMeans(k={k}) on {len(docs)} drops ...")
    vec = TfidfVectorizer(max_features=20000, stop_words="english",
                          ngram_range=(1, 2), min_df=3)
    X = vec.fit_transform(docs)
    km = KMeans(n_clusters=k, random_state=SEED, n_init=10)
    topics = list(km.fit_predict(X))

    terms = vec.get_feature_names_out()
    order = km.cluster_centers_.argsort()[:, ::-1]
    keywords = {tid: [terms[i] for i in order[tid][:8]] for tid in range(k)}
    labels = {tid: " · ".join(kw[:3]) for tid, kw in keywords.items()}

    coords2d = TruncatedSVD(n_components=2, random_state=SEED).fit_transform(X).tolist()
    return topics, labels, keywords, coords2d, [0.0] * len(docs)


# --------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------
def _project_2d(embeddings):
    """A separate 2-D UMAP just for the scatter plot (clustering uses 5-D)."""
    from umap import UMAP
    print("[viz] UMAP(2d) for scatter ...")
    xy = UMAP(n_neighbors=15, n_components=2, min_dist=0.1,
              metric="cosine", random_state=SEED).fit_transform(embeddings)
    return xy.tolist()


def _ctfidf_keywords(docs, topics, top_n=8):
    """Class-based TF-IDF: which words are distinctive to each cluster."""
    from sklearn.feature_extraction.text import CountVectorizer
    import numpy as np

    groups = {}
    for d, t in zip(docs, topics):
        groups.setdefault(t, []).append(d)
    tids = sorted(groups)
    joined = [" ".join(groups[t]) for t in tids]

    cv = CountVectorizer(stop_words="english", ngram_range=(1, 2), min_df=2)
    counts = cv.fit_transform(joined).toarray().astype(float)
    words = cv.get_feature_names_out()

    tf = counts / counts.sum(axis=1, keepdims=True).clip(min=1)
    idf = np.log(1 + counts.shape[0] / (counts > 0).sum(axis=0).clip(min=1))
    ctfidf = tf * idf

    out = {}
    for i, t in enumerate(tids):
        top = ctfidf[i].argsort()[::-1][:top_n]
        out[t] = [words[j] for j in top]
    return out


# --------------------------------------------------------------------------------------
# 5. ASSEMBLE + WRITE
# --------------------------------------------------------------------------------------
def write_outputs(rows, topics, labels, keywords, coords2d, conf, out_path, method, embedding_model):
    drops = []
    for r, t, xy, c in zip(rows, topics, coords2d, conf):
        t = int(t)
        drops.append({
            "id": r["id"],
            "author": r.get("author"),
            "date": r["date"],
            "year": r["year"],
            "text": r["text"],
            "topic": t,
            "topic_label": labels.get(t, f"topic {t}"),
            "x": round(float(xy[0]), 4),
            "y": round(float(xy[1]), 4),
            "conf": round(float(c), 3),
        })

    counts = Counter(d["topic"] for d in drops)
    total = len(drops) or 1
    topics_summary = []
    for tid in sorted(counts, key=lambda k: (-counts[k], k)):
        topics_summary.append({
            "topic": tid,
            "label": labels.get(tid, f"topic {tid}"),
            "keywords": keywords.get(tid, []),
            "size": counts[tid],
            "share": round(100 * counts[tid] / total, 2),
        })

    payload = {
        "meta": {
            "source": "jkingsman/JSON-QAnon (research only)",
            "source_url": "https://github.com/jkingsman/JSON-QAnon",
            "doi": "10.13140/RG.2.2.28778.32964",
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "method": method,
            "n_drops": len(drops),
            "n_topics": len([t for t in counts if t != -1]),
            "embedding_model": embedding_model,
        },
        "topics": topics_summary,
        "drops": drops,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    print(f"[out] wrote {out_path}  ({len(drops)} drops, "
          f"{payload['meta']['n_topics']} topics + noise)")

    csv_path = os.path.splitext(out_path)[0].replace("_clustered", "") + "_topics_summary.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["topic", "label", "size", "share_%", "keywords"])
        for t in topics_summary:
            w.writerow([t["topic"], t["label"], t["size"], t["share"], ", ".join(t["keywords"])])
    print(f"[out] wrote {csv_path}")

    print("\n=== TOPIC BREAKDOWN ===")
    for t in topics_summary:
        tag = "noise" if t["topic"] == -1 else f"#{t['topic']:>2}"
        print(f"  {tag}  {t['size']:>4} ({t['share']:>5.1f}%)  {', '.join(t['keywords'][:6])}")


# --------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Topic-cluster the QAnon drops.")
    ap.add_argument("--method", choices=["bertopic", "hdbscan", "kmeans"],
                    default="bertopic", help="clustering technique (default: bertopic)")
    ap.add_argument("--min-cluster-size", type=int, default=15,
                    help="HDBSCAN: smallest topic to keep (smaller = more topics, less noise)")
    ap.add_argument("-k", type=int, default=14, help="KMeans: number of clusters")
    ap.add_argument("--model", default=EMBED_MODEL,
                    help="sentence-transformers model (e.g. all-mpnet-base-v2 = higher quality, slower)")
    ap.add_argument("--reduce-outliers", action="store_true",
                    help="BERTopic: reassign noise(-1) drops to nearest topic (smaller noise bucket)")
    ap.add_argument("--author-filter", default=None,
                    help="optional: keep only this author (e.g. Q). Default: keep all.")
    ap.add_argument("--input", default=DEFAULT_INPUT)
    ap.add_argument("--output", default=DEFAULT_OUTPUT)
    ap.add_argument("--no-download", action="store_true",
                    help="use a local posts.json and skip the network")
    ap.add_argument("--max-posts", type=int, default=0,
                    help="cap drops for a quick test run (0 = all)")
    ap.add_argument("--inspect", action="store_true",
                    help="print the data structure + a sample record, then exit")
    args = ap.parse_args()

    if not args.no_download:
        download_dataset(args.input)
    if not os.path.exists(args.input):
        sys.exit(f"ERROR: {args.input} not found. Download it from {RAW_URL}")

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)

    if args.inspect:
        inspect_structure(data)
        return

    posts = coerce_posts(data)
    print(f"[load] {len(posts)} posts from {args.input}")

    rows = normalise(posts, author_filter=args.author_filter)
    if not rows:
        sys.exit("ERROR: 0 drops after parsing. Run `python qdrops_cluster.py --inspect` "
                 "to see the structure; the loader may need adjusting for your file.")
    if args.max_posts:
        rows = rows[: args.max_posts]
        print(f"[load] capped to {len(rows)} drops for this run")

    docs = [r["_clean"] for r in rows]
    if args.method == "bertopic":
        topics, labels, keywords, coords2d, conf = run_bertopic(
            docs, args.min_cluster_size, model=args.model, reduce_outliers=args.reduce_outliers)
    elif args.method == "hdbscan":
        topics, labels, keywords, coords2d, conf = run_hdbscan(
            docs, args.min_cluster_size, model=args.model)
    else:
        topics, labels, keywords, coords2d, conf = run_kmeans(docs, args.k)

    embed_name = args.model if args.method != "kmeans" else "TF-IDF"
    write_outputs(rows, topics, labels, keywords, coords2d, conf,
                  args.output, args.method, embed_name)
    print("\nDone. Copy", args.output, "next to drops.html and reload the page.")


if __name__ == "__main__":
    main()