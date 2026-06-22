#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qdrops_cluster.py  --  Cluster the QAnon "drops" AND measure how trustworthy the result is.

This version adds the analytical layer:
  * VALIDITY  -- every run reports a silhouette score (cluster separation) and gensim
                 c_v topic coherence (mean + per-topic), so "good clustering" is measured.
  * METADATA  -- pulls the fields we used to throw away: images, referenced_posts,
                 tripcode, and source board/site. Exports per-drop flags + a corpus-level
                 composition + a board-migration breakdown (4chan -> 8chan -> 8kun).
  * ADMIN TAG -- heuristically flags operational drops ("test", "trip update", "comms",
                 "disregard spelling", "board/sniffer/config"...) so they can be filtered
                 or excluded (--drop-admin) to sharpen the thematic picture.
  * REUSABLE  -- the load/embed/cluster/validity functions are importable, so qdrops_sweep.py
                 can run many configs, embed once per model, and compare topic stability.

WHY NOT k-NN?  k-NN is supervised; it can't discover topics. Self-forming topics come from
embeddings -> UMAP -> HDBSCAN (wrapped by BERTopic with class-based TF-IDF labels). A k-NN
*graph* + community detection is the only legitimate k-NN-for-clustering route; a plain
TF-IDF + KMeans baseline (--method kmeans) is also included.

USAGE
-----
    pip install -r requirements.txt
    python qdrops_cluster.py --inspect                 # print data shape + a sample, then exit
    python qdrops_cluster.py                            # BERTopic + validity (recommended)
    python qdrops_cluster.py --reduce-outliers          # shrink the noise bucket
    python qdrops_cluster.py --drop-admin               # exclude operational drops first
    python qdrops_cluster.py --model all-mpnet-base-v2   # stronger embeddings (slower)
    python qdrops_cluster.py --no-coherence             # skip gensim c_v (faster)
    python qdrops_cluster.py --method kmeans -k 14       # quick baseline, no torch
Then copy qdrops_clustered.json next to drops.html and reload.
To compare several configurations, use:  python qdrops_sweep.py

Dataset: Kingsman, J. (2025) JSON-QAnon, DOI 10.13140/RG.2.2.28778.32964 -- research only.
"""

import argparse
import csv
import json
import os
import re
import sys
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone

RAW_URL = "https://raw.githubusercontent.com/jkingsman/JSON-QAnon/main/posts.json"
DEFAULT_INPUT = "posts.json"
DEFAULT_OUTPUT = "qdrops_clustered.json"
EMBED_MODEL = "all-MiniLM-L6-v2"
SEED = 42


# ============================ ACQUIRE / LOAD =====================================
def download_dataset(path):
    if os.path.exists(path):
        print(f"[data] using cached {path}"); return
    print(f"[data] downloading {RAW_URL}")
    req = urllib.request.Request(RAW_URL, headers={"User-Agent": "qdrops-research/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(path, "wb") as f:
        f.write(r.read())
    print(f"[data] saved -> {path} ({os.path.getsize(path)/1e6:.1f} MB)")


def coerce_posts(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("posts", "drops", "data", "records", "items"):
            if isinstance(data.get(key), list):
                return data[key]
        vals = list(data.values())
        if vals and all(isinstance(v, dict) for v in vals):
            return vals
        lv = [v for v in data.values() if isinstance(v, list)]
        if len(lv) == 1:
            return lv[0]
    raise ValueError("Could not locate the list of posts. Run with --inspect.")


def inspect_structure(data):
    print("---- DATA STRUCTURE ----")
    print("top-level type:", type(data).__name__)
    if isinstance(data, dict):
        print("top-level keys:", list(data.keys())[:25])
    try:
        posts = coerce_posts(data)
    except ValueError as e:
        print("!!", e); return
    print("posts found:", len(posts))
    if posts and isinstance(posts[0], dict):
        p0 = posts[0]
        print("first post keys:", list(p0.keys()))
        meta0 = _meta(p0)
        if meta0 is not p0:
            print("post_metadata keys:", list(meta0.keys()))
        print("  author/id/time (via _meta):", _get_author(p0), "/", _get_id(p0), "/", _get_time(p0))
        print("  source (via _meta):", meta0.get("source") if isinstance(meta0, dict) else None)
        print("  text[:140]:", repr((_get_text(p0))[:140]))
        # corpus-wide scan: where do tripcodes live?
        trips, authors = {}, []
        has_trip_field = 0
        for p in posts:
            if not isinstance(p, dict):
                continue
            mm = _meta(p)
            a = str(mm.get("author") or p.get("author") or "")
            if a and a not in authors and len(authors) < 8:
                authors.append(a)
            if (mm.get("tripcode") or p.get("tripcode") or "").strip():
                has_trip_field += 1
            tc = _get_tripcode(p)
            if tc:
                trips[tc] = trips.get(tc, 0) + 1
        print("  distinct authors (sample):", authors)
        print(f"  posts with explicit 'tripcode' field: {has_trip_field}")
        print(f"  tripcodes detected (field OR parsed from author): {len(trips)} distinct ->",
              dict(list(trips.items())[:8]))
    print("------------------------")


# ============================ FIELD EXTRACTION ===================================
def _meta(p):
    return p.get("post_metadata") or p.get("metadata") or p


def _get_id(p):
    m = _meta(p)
    for k in ("post_id", "id", "no", "n"):
        v = m.get(k, p.get(k))
        if v is not None:
            return v
    return None


def _get_author(p):
    return str(_meta(p).get("author") or p.get("author") or "").strip()


def _get_time(p):
    m = _meta(p)
    for k in ("time", "timestamp", "datetime", "date"):
        v = m.get(k, p.get(k))
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


def _get_text(p):
    t = p.get("text")
    if t is None:
        t = _meta(p).get("text")
    return t or ""


def _get_images(p):
    im = p.get("images") or _meta(p).get("images") or []
    return im if isinstance(im, list) else []


def _get_refs(p):
    r = p.get("referenced_posts") or _meta(p).get("referenced_posts") or []
    return r if isinstance(r, list) else []


TRIP_RE = re.compile(r"(!{1,2}[A-Za-z0-9+/.]{8,15})")


def _get_tripcode(p):
    m = _meta(p)
    t = (m.get("tripcode") or p.get("tripcode") or "").strip()
    if t:
        return t
    # chan archives often fold the tripcode into the author string, e.g. "Q !!Hs1Jq13jV6"
    author = str(m.get("author") or p.get("author") or "")
    mt = TRIP_RE.search(author)
    return mt.group(1) if mt else ""


def _get_board(p):
    src = p.get("source") or _meta(p).get("source") or {}
    if isinstance(src, dict):
        return str(src.get("site") or src.get("board") or src.get("name") or "unknown").strip() or "unknown"
    if isinstance(src, str) and src.strip():
        return src.strip()
    return "unknown"


URL_RE = re.compile(r"https?://\S+")
WS_RE = re.compile(r"\s+")


def clean_for_embedding(text):
    text = URL_RE.sub(" ", text)
    text = re.sub(r">>\d+", " ", text)
    text = re.sub(r"[>#*`~_]+", " ", text)
    text = re.sub(r"!{2,}\S+", " ", text)
    return WS_RE.sub(" ", text).strip()


# ---- administrative / operational drop detection (heuristic) --------------------
ADMIN_RE = [
    re.compile(r"\btest\b", re.I),
    re.compile(r"\btrip(code)?\b.*\b(code|update|confirm|compromis|new|change)\b", re.I),
    re.compile(r"\bnew\s+trip", re.I),
    re.compile(r"\bcomm?s\b", re.I),
    re.compile(r"\bsniffer\b", re.I),
    re.compile(r"\bdisregard\b", re.I),
    re.compile(r"\bspelling\b", re.I),
    re.compile(r"\bcorrection\b", re.I),
    re.compile(r"\bpassword\b", re.I),
    re.compile(r"\bconfig(uration)?\b", re.I),
    re.compile(r"\b(board|bo|cm)\b.*\b(access|owner|control|created|down|migrat)\b", re.I),
    re.compile(r"\b(offline|online)\b", re.I),
    re.compile(r"\bstations?\b", re.I),
    re.compile(r"\binput\s+error\b", re.I),
    re.compile(r"\bdevice\b", re.I),
    re.compile(r"\bre-?post(ing)?\b", re.I),
]
ADMIN_STRONG = [
    re.compile(r"disregard\s+(last|prev)", re.I),
    re.compile(r"spelling\s+error", re.I),
    re.compile(r"trip(code)?\s+(update|confirmed|compromised)", re.I),
    re.compile(r"^\s*test\s*\.?\s*$", re.I),
]


def is_admin(clean_text):
    """Operational/administrative drop (not ideological content). Heuristic."""
    if not clean_text:
        return False
    for rx in ADMIN_STRONG:
        if rx.search(clean_text):
            return True
    words = len(clean_text.split())
    if words <= 15:
        for rx in ADMIN_RE:
            if rx.search(clean_text):
                return True
    return False


# ============================ NORMALISE ==========================================
def normalise(posts, author_filter=None, drop_admin=False):
    rows = []
    comp = {"total": 0, "text": 0, "image_only": 0, "empty": 0,
            "with_images": 0, "with_refs": 0, "admin": 0}
    boards = Counter()
    board_year = defaultdict(Counter)
    trip_count = Counter()
    trip_first, trip_last = {}, {}
    no_text = filtered = admin_excluded = 0

    for p in posts:
        if not isinstance(p, dict):
            continue
        comp["total"] += 1
        author = _get_author(p)
        imgs = _get_images(p)
        refs = _get_refs(p)
        dt = _get_time(p)
        board = _get_board(p)
        trip = (_get_tripcode(p) or "").strip()
        if trip:
            trip_count[trip] += 1
            if dt:
                ts = int(dt.timestamp())
                ds = dt.strftime("%Y-%m-%d")
                if trip not in trip_first or ts < trip_first[trip][0]:
                    trip_first[trip] = (ts, ds)
                if trip not in trip_last or ts > trip_last[trip][0]:
                    trip_last[trip] = (ts, ds)
        if imgs:
            comp["with_images"] += 1
        if refs:
            comp["with_refs"] += 1
        boards[board] += 1
        if dt:
            board_year[board][dt.year] += 1

        raw = _get_text(p).strip()
        clean = clean_for_embedding(raw)
        admin = is_admin(clean)

        if len(clean) < 3:
            if imgs:
                comp["image_only"] += 1
            else:
                comp["empty"] += 1
            no_text += 1
            continue
        comp["text"] += 1
        if admin:
            comp["admin"] += 1

        if author_filter and author.lower() != author_filter.lower():
            filtered += 1
            continue
        if drop_admin and admin:
            admin_excluded += 1
            continue

        rows.append({
            "id": _get_id(p), "author": author or None,
            "date": dt.strftime("%Y-%m-%d") if dt else None,
            "year": dt.year if dt else None,
            "text": raw, "_clean": clean,
            "words": len(clean.split()),
            "has_image": bool(imgs), "n_refs": len(refs),
            "tripcode": _get_tripcode(p) or None, "board": board, "admin": admin,
        })

    comp["boards"] = dict(boards.most_common())
    comp["board_year"] = {b: dict(sorted(y.items())) for b, y in board_year.items()}
    trips = []
    for t, cnt in trip_count.items():
        f, l = trip_first.get(t), trip_last.get(t)
        trips.append({"trip": t, "count": cnt,
                      "first": f[1] if f else None, "last": l[1] if l else None,
                      "secure": t.startswith("!!"), "_t": f[0] if f else 0})
    trips.sort(key=lambda d: d["_t"])
    for d in trips:
        d.pop("_t", None)
    comp["tripcodes"] = trips
    msg = f"[norm] kept {len(rows)} drops; skipped {no_text} (image-only/empty)"
    if author_filter:
        msg += f"; filtered {filtered} (author!={author_filter})"
    if drop_admin:
        msg += f"; excluded {admin_excluded} administrative"
    print(msg)
    print(f"[norm] composition: {comp['text']} text · {comp['image_only']} image-only · "
          f"{comp['empty']} empty · {comp['admin']} admin(text) · boards={list(comp['boards'])[:6]}")
    if comp["tripcodes"]:
        print(f"[norm] tripcodes: {len(comp['tripcodes'])} distinct "
              f"({sum(1 for t in comp['tripcodes'] if t['secure'])} secure '!!')")
        for t in comp["tripcodes"]:
            sec = "secure" if t["secure"] else "single"
            print(f"        {t['trip']:<16} {t['count']:>4} drops  {t['first']} → {t['last']}  [{sec}]")
    return rows, comp


# ============================ EMBED + CLUSTER ====================================
def embed_docs(docs, model=EMBED_MODEL):
    from sentence_transformers import SentenceTransformer
    print(f"[embed] {model}  ({len(docs)} drops)")
    return SentenceTransformer(model).encode(docs, show_progress_bar=True, batch_size=64)


def project_2d(embeddings):
    from umap import UMAP
    print("[viz] UMAP(2d) for scatter ...")
    return UMAP(n_neighbors=15, n_components=2, min_dist=0.1, metric="cosine",
                random_state=SEED).fit_transform(embeddings).tolist()


def _labels_from_keywords(keywords):
    return {tid: ("noise / outliers" if tid == -1 else (" · ".join(kw[:3]) or f"topic {tid}"))
            for tid, kw in keywords.items()}


def run_bertopic_emb(docs, embeddings, min_cluster_size, reduce_outliers=False):
    from bertopic import BERTopic
    from bertopic.vectorizers import ClassTfidfTransformer
    from sklearn.feature_extraction.text import CountVectorizer
    from umap import UMAP
    from hdbscan import HDBSCAN

    umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric="cosine", random_state=SEED)
    hdbscan_model = HDBSCAN(min_cluster_size=min_cluster_size, metric="euclidean",
                            cluster_selection_method="eom", prediction_data=True)
    vectorizer_model = CountVectorizer(stop_words="english", ngram_range=(1, 2), min_df=2)
    ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)

    tm = BERTopic(umap_model=umap_model, hdbscan_model=hdbscan_model,
                  vectorizer_model=vectorizer_model, ctfidf_model=ctfidf_model,
                  calculate_probabilities=False, verbose=False)
    print(f"[cluster] BERTopic (min_cluster_size={min_cluster_size}) ...")
    topics, _ = tm.fit_transform(docs, embeddings)
    topics = list(topics)
    if reduce_outliers:
        print("[cluster] reducing outliers ...")
        try:
            topics = list(tm.reduce_outliers(docs, topics, strategy="c-tf-idf"))
            tm.update_topics(docs, topics=topics, vectorizer_model=vectorizer_model, ctfidf_model=ctfidf_model)
        except Exception as e:  # noqa: BLE001
            print("   [warn] reduce_outliers failed:", e)
    keywords = {tid: [w for w, _ in (tm.get_topic(tid) or []) if w][:10] for tid in set(topics)}
    space = getattr(tm.umap_model, "embedding_", None)
    probs = getattr(tm.hdbscan_model, "probabilities_", None)
    conf = ([float(x) for x in probs] if probs is not None and len(probs) == len(docs) else [0.0] * len(docs))
    return {"topics": topics, "labels": _labels_from_keywords(keywords),
            "keywords": keywords, "space": space, "conf": conf}


def run_hdbscan_emb(docs, embeddings, min_cluster_size):
    from umap import UMAP
    from hdbscan import HDBSCAN
    print(f"[cluster] UMAP(5d) -> HDBSCAN (min_cluster_size={min_cluster_size}) ...")
    reduced = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric="cosine",
                   random_state=SEED).fit_transform(embeddings)
    cl = HDBSCAN(min_cluster_size=min_cluster_size, metric="euclidean", cluster_selection_method="eom")
    topics = list(cl.fit_predict(reduced))
    keywords = ctfidf_keywords(docs, topics)
    probs = getattr(cl, "probabilities_", None)
    conf = ([float(x) for x in probs] if probs is not None else [0.0] * len(docs))
    return {"topics": topics, "labels": _labels_from_keywords(keywords),
            "keywords": keywords, "space": reduced, "conf": conf}


def run_kmeans(docs, k):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.decomposition import TruncatedSVD
    print(f"[cluster] TF-IDF -> KMeans(k={k}) ...")
    vec = TfidfVectorizer(max_features=20000, stop_words="english", ngram_range=(1, 2), min_df=3)
    X = vec.fit_transform(docs)
    km = KMeans(n_clusters=k, random_state=SEED, n_init=10)
    topics = list(km.fit_predict(X))
    terms = vec.get_feature_names_out()
    order = km.cluster_centers_.argsort()[:, ::-1]
    keywords = {tid: [terms[i] for i in order[tid][:10]] for tid in range(k)}
    coords2d = TruncatedSVD(n_components=2, random_state=SEED).fit_transform(X)
    return {"topics": topics, "labels": _labels_from_keywords(keywords),
            "keywords": keywords, "space": coords2d, "conf": [0.0] * len(docs),
            "coords2d": coords2d.tolist()}


def ctfidf_keywords(docs, topics, top_n=10):
    from sklearn.feature_extraction.text import CountVectorizer
    import numpy as np
    groups = defaultdict(list)
    for d, t in zip(docs, topics):
        groups[t].append(d)
    tids = sorted(groups)
    joined = [" ".join(groups[t]) for t in tids]
    cv = CountVectorizer(stop_words="english", ngram_range=(1, 2), min_df=2)
    counts = cv.fit_transform(joined).toarray().astype(float)
    words = cv.get_feature_names_out()
    tf = counts / counts.sum(axis=1, keepdims=True).clip(min=1)
    idf = np.log(1 + counts.shape[0] / (counts > 0).sum(axis=0).clip(min=1))
    ctf = tf * idf
    return {t: [words[j] for j in ctf[i].argsort()[::-1][:top_n]] for i, t in enumerate(tids)}


# ============================ VALIDITY ==========================================
def compute_validity(space, topics, docs, keywords, do_coherence=True):
    import numpy as np
    out = {"silhouette": None, "coherence_cv_mean": None, "per_topic_coherence": {}}

    # --- silhouette on the clustering space (excluding noise) ---
    try:
        from sklearn.metrics import silhouette_score
        t = np.array(topics)
        mask = t != -1
        labs = t[mask]
        if space is not None and mask.sum() >= 10 and len(set(labs.tolist())) >= 2:
            X = np.asarray(space)[mask]
            n = X.shape[0]
            ss = min(2500, n)
            out["silhouette"] = round(float(silhouette_score(X, labs, sample_size=ss, random_state=SEED)), 4)
    except Exception as e:  # noqa: BLE001
        print("   [warn] silhouette failed:", e)

    # --- gensim c_v topic coherence ---
    if do_coherence:
        try:
            from gensim.corpora import Dictionary
            from gensim.models import CoherenceModel
            tids = [t for t in sorted(keywords) if t != -1]
            topic_words = []
            for t in tids:
                toks, seen = [], set()
                for kw in keywords[t]:
                    for w in str(kw).lower().split():
                        if w not in seen:
                            seen.add(w); toks.append(w)
                topic_words.append(toks[:10])
            topic_words = [tw for tw in topic_words if len(tw) >= 2]
            if topic_words:
                texts = [d.lower().split() for d in docs]
                dictionary = Dictionary(texts)
                cm = CoherenceModel(topics=topic_words, texts=texts, dictionary=dictionary,
                                    coherence="c_v", topn=10)
                out["coherence_cv_mean"] = round(float(cm.get_coherence()), 4)
                per = cm.get_coherence_per_topic()
                valid_tids = [t for t in tids if len([w for w in
                              dict.fromkeys(" ".join(keywords[t]).lower().split())]) >= 2]
                for tid, c in zip(valid_tids, per):
                    out["per_topic_coherence"][str(tid)] = round(float(c), 4)
        except ImportError:
            print("   [info] gensim not installed -> skipping c_v coherence "
                  "(pip install gensim, or use --no-coherence)")
        except Exception as e:  # noqa: BLE001
            print("   [warn] coherence failed:", e)
    return out


# ============================ ASSEMBLE + WRITE ==================================
def build_payload(rows, result, coords2d, validity, composition, method, embedding_model, params):
    topics, labels, keywords, conf = (result["topics"], result["labels"],
                                      result["keywords"], result["conf"])
    drops = []
    for r, t, xy, c in zip(rows, topics, coords2d, conf):
        t = int(t)
        drops.append({
            "id": r["id"], "author": r.get("author"), "date": r["date"], "year": r["year"],
            "text": r["text"], "topic": t, "topic_label": labels.get(t, f"topic {t}"),
            "x": round(float(xy[0]), 4), "y": round(float(xy[1]), 4), "conf": round(float(c), 3),
            "words": r["words"], "has_image": r["has_image"], "n_refs": r["n_refs"],
            "tripcode": r["tripcode"], "board": r["board"], "admin": r["admin"],
        })
    counts = Counter(d["topic"] for d in drops)
    total = len(drops) or 1
    per_coh = validity.get("per_topic_coherence", {})
    topics_summary = []
    for tid in sorted(counts, key=lambda k: (-counts[k], k)):
        topics_summary.append({
            "topic": tid, "label": labels.get(tid, f"topic {tid}"),
            "keywords": keywords.get(tid, []), "size": counts[tid],
            "share": round(100 * counts[tid] / total, 2),
            "coherence": per_coh.get(str(tid)),
        })
    return {
        "meta": {
            "source": "jkingsman/JSON-QAnon (research only)",
            "source_url": "https://github.com/jkingsman/JSON-QAnon",
            "doi": "10.13140/RG.2.2.28778.32964",
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "method": method, "embedding_model": embedding_model, "params": params,
            "n_drops": len(drops), "n_topics": len([t for t in counts if t != -1]),
            "validity": {"silhouette": validity.get("silhouette"),
                         "coherence_cv_mean": validity.get("coherence_cv_mean")},
            "composition": composition,
        },
        "topics": topics_summary, "drops": drops,
    }


def write_payload(payload, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    m = payload["meta"]
    print(f"[out] {out_path}: {m['n_drops']} drops, {m['n_topics']} topics + noise "
          f"| silhouette={m['validity']['silhouette']} c_v={m['validity']['coherence_cv_mean']}")
    csv_path = os.path.splitext(out_path)[0].replace("_clustered", "") + "_topics_summary.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["topic", "label", "size", "share_%", "coherence_cv", "keywords"])
        for t in payload["topics"]:
            w.writerow([t["topic"], t["label"], t["size"], t["share"],
                        t.get("coherence"), ", ".join(t["keywords"])])
    print(f"[out] {csv_path}")
    print("\n=== TOPICS (size · c_v · keywords) ===")
    for t in payload["topics"]:
        tag = "noise" if t["topic"] == -1 else f"#{t['topic']:>2}"
        coh = "  n/a" if t.get("coherence") is None else f"{t['coherence']:>5.2f}"
        print(f"  {tag}  {t['size']:>4} ({t['share']:>5.1f}%)  c_v={coh}  {', '.join(t['keywords'][:6])}")


# ============================ HIGH-LEVEL ========================================
def cluster_once(docs, embeddings, method, min_cluster_size, k, reduce_outliers):
    """Cluster pre-embedded docs (embeddings unused for kmeans). Returns result dict + coords2d."""
    if method == "bertopic":
        res = run_bertopic_emb(docs, embeddings, min_cluster_size, reduce_outliers)
        return res, project_2d(embeddings)
    if method == "hdbscan":
        res = run_hdbscan_emb(docs, embeddings, min_cluster_size)
        return res, project_2d(embeddings)
    res = run_kmeans(docs, k)
    return res, res["coords2d"]


def main():
    ap = argparse.ArgumentParser(description="Cluster the QAnon drops with validity scoring.")
    ap.add_argument("--method", choices=["bertopic", "hdbscan", "kmeans"], default="bertopic")
    ap.add_argument("--min-cluster-size", type=int, default=15)
    ap.add_argument("-k", type=int, default=14, help="KMeans clusters")
    ap.add_argument("--model", default=EMBED_MODEL, help="sentence-transformers model")
    ap.add_argument("--reduce-outliers", action="store_true")
    ap.add_argument("--drop-admin", action="store_true", help="exclude administrative drops")
    ap.add_argument("--author-filter", default=None)
    ap.add_argument("--no-coherence", action="store_true", help="skip gensim c_v (faster)")
    ap.add_argument("--input", default=DEFAULT_INPUT)
    ap.add_argument("--output", default=DEFAULT_OUTPUT)
    ap.add_argument("--no-download", action="store_true")
    ap.add_argument("--max-posts", type=int, default=0)
    ap.add_argument("--inspect", action="store_true")
    args = ap.parse_args()

    if not args.no_download:
        download_dataset(args.input)
    if not os.path.exists(args.input):
        sys.exit(f"ERROR: {args.input} not found. Get it from {RAW_URL}")
    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)
    if args.inspect:
        inspect_structure(data); return

    posts = coerce_posts(data)
    print(f"[load] {len(posts)} posts")
    rows, comp = normalise(posts, author_filter=args.author_filter, drop_admin=args.drop_admin)
    if not rows:
        sys.exit("ERROR: 0 drops after parsing. Try `--inspect`.")
    if args.max_posts:
        rows = rows[: args.max_posts]; print(f"[load] capped to {len(rows)}")

    docs = [r["_clean"] for r in rows]
    embeddings = None if args.method == "kmeans" else embed_docs(docs, args.model)
    result, coords2d = cluster_once(docs, embeddings, args.method,
                                    args.min_cluster_size, args.k, args.reduce_outliers)
    validity = compute_validity(result["space"], result["topics"], docs,
                                result["keywords"], do_coherence=not args.no_coherence)
    print(f"[validity] silhouette={validity['silhouette']}  c_v_mean={validity['coherence_cv_mean']}")

    embed_name = args.model if args.method != "kmeans" else "TF-IDF"
    params = {"min_cluster_size": args.min_cluster_size, "k": args.k,
              "reduce_outliers": args.reduce_outliers, "drop_admin": args.drop_admin}
    payload = build_payload(rows, result, coords2d, validity, comp, args.method, embed_name, params)
    write_payload(payload, args.output)
    print("\nDone. Copy", args.output, "next to drops.html and reload.")


if __name__ == "__main__":
    main()
