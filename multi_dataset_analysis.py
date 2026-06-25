#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
multi_dataset_analysis.py — Cluster + BITE-score every available dataset.

What it does
------------
  1. Discovers all normalised datasets in datasets/normalised/ and samples in
     datasets/samples/ (used when the full set is not yet downloaded).
  2. Runs the clustering pipeline (from qdrops_cluster.py) on each dataset:
       TF-IDF + KMeans (--method kmeans) — fast, no GPU
       or BERTopic (default) if torch is available.
  3. Runs the BITE model scorer on each dataset.
  4. Replicates three key papers' methodologies:
       a) Hoseini et al. 2021 — Cross-platform topic overlap (Jaccard)
       b) iDRAMA Lab          — Platform migration timeline
       c) Priniski & Bavel 2021 — Motivated-reasoning keyword classifier
  5. Writes one results file per dataset: results/<dataset_id>/analysis.json
  6. Writes a master index: results/index.json

USAGE
-----
    python multi_dataset_analysis.py                      # all datasets, kmeans
    python multi_dataset_analysis.py --method bertopic    # use BERTopic (slower)
    python multi_dataset_analysis.py --dataset qdrops     # single dataset
    python multi_dataset_analysis.py --no-clustering      # BITE only
    python multi_dataset_analysis.py --samples-only       # use 500-post samples
"""

import argparse
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone

# ──────────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────────
CATALOG_PATH  = "datasets/catalog.json"
NORM_DIR      = "datasets/normalised"
SAMPLES_DIR   = "datasets/samples"
RESULTS_DIR   = "results"

# ──────────────────────────────────────────────────────────────────────────────
# Motivated-reasoning lexicon (Priniski & Bavel 2021)
# Markers of identity-protective cognition: certainty, us/them, dismissal
# ──────────────────────────────────────────────────────────────────────────────
MR_LEXICON = {
    "certainty":   [r"\balways\b", r"\bnever\b", r"\bproven\b", r"\bconfirmed\b",
                    r"\bundeniably\b", r"\bobviously\b", r"\bclearly\b",
                    r"\bwithout\s+doubt\b", r"\bno\s+question\b", r"\babsolutely\b"],
    "us_vs_them":  [r"\bthey\s+(want|don'?t|are|will)\b", r"\bthe\s+enemy\b",
                    r"\bthe\s+elite\b", r"\bour\s+enemies\b", r"\bthe\s+globalists?\b",
                    r"\bthe\s+cabal\b", r"\bdeep\s+state\b", r"\bpure\s+evil\b",
                    r"\bvs\s+(us|them|evil)\b"],
    "dismissal":   [r"\bdo\s+your\s+(own\s+)?research\b", r"\bwake\s+up\b",
                    r"\bsheeple\b", r"\bnormies?\b", r"\bbrainwashed\b",
                    r"\bfake\s+news\b", r"\bmsm\s+lies?\b", r"\bthe\s+media\s+lies?\b",
                    r"\byou'?re\s+asleep\b"],
    "in_group":    [r"\bwwg1wga\b", r"\bpatriot(s)?\b", r"\bgreat\s+awakening\b",
                    r"\bwe\s+are\s+(one|together|awake)\b", r"\bhold\s+the\s+line\b",
                    r"\bnight\s+shift\b", r"\banon(s)?\b"],
}

_MR_COMPILED = {
    cat: [re.compile(p, re.IGNORECASE) for p in patterns]
    for cat, patterns in MR_LEXICON.items()
}


def score_motivated_reasoning(text):
    """Return per-category hit counts and total MR score (0-1)."""
    counts = {}
    total_hits = 0
    for cat, pats in _MR_COMPILED.items():
        c = sum(1 for p in pats if p.search(text))
        counts[cat] = c
        total_hits += c
    # Saturate at 8 total hits → score 1.0
    score = min(total_hits / 8.0, 1.0)
    return {"categories": counts, "score": round(score, 4)}


# ──────────────────────────────────────────────────────────────────────────────
# Clustering helpers
# ──────────────────────────────────────────────────────────────────────────────

def cluster_kmeans(texts, k=10, seed=42):
    """TF-IDF + KMeans clustering. No GPU required."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    import numpy as np

    texts = [t for t in texts if t and t.strip()]
    if len(texts) < k:
        k = max(2, len(texts) // 2)

    vec = TfidfVectorizer(max_features=5000, stop_words="english",
                          min_df=2, ngram_range=(1, 2))
    X = vec.fit_transform(texts)
    if X.shape[0] < k:
        k = max(2, X.shape[0] // 2)

    km = KMeans(n_clusters=k, random_state=seed, n_init=10, max_iter=300)
    labels = km.fit_predict(X)

    # Topic keywords: top TF-IDF terms per cluster centroid
    terms = vec.get_feature_names_out()
    topics = []
    for i in range(k):
        center    = km.cluster_centers_[i]
        top_idx   = center.argsort()[::-1][:8]
        keywords  = [terms[j] for j in top_idx]
        size      = int((labels == i).sum())
        topics.append({
            "id":       i,
            "label":    " · ".join(keywords[:3]),
            "keywords": keywords,
            "size":     size,
            "share_pct": round(100 * size / len(labels), 2),
        })

    sil = float(silhouette_score(X, labels, sample_size=min(2000, X.shape[0]), random_state=seed)) \
          if len(set(labels)) > 1 else 0.0

    return labels.tolist(), topics, {"silhouette": round(sil, 4), "n_clusters": k}


def cluster_bertopic(texts, min_cluster_size=10, seed=42):
    """BERTopic clustering. Requires sentence-transformers + UMAP + HDBSCAN."""
    try:
        from bertopic import BERTopic
        from sentence_transformers import SentenceTransformer
        from umap import UMAP
    except ImportError:
        print("  [warn] BERTopic not available, falling back to KMeans")
        return cluster_kmeans(texts, seed=seed)

    texts_clean = [t if t and t.strip() else "empty" for t in texts]
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    # POST-AUDIT FIX: pass a SEEDED UMAP so multi-dataset BERTopic runs are
    # reproducible. Previously UMAP was left to its random default, so the
    # published cross-platform topics/overlaps were not bit-for-bit reproducible.
    umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0,
                      metric="cosine", random_state=seed)
    bt = BERTopic(embedding_model=embed_model,
                  umap_model=umap_model,
                  min_topic_size=min_cluster_size,
                  calculate_probabilities=False,
                  verbose=False)
    labels, _ = bt.fit_transform(texts_clean)

    topic_info = bt.get_topic_info()
    topics = []
    for _, row in topic_info.iterrows():
        tid = int(row["Topic"])
        if tid == -1:
            continue
        kws = [w for w, _ in bt.get_topic(tid)[:8]] if bt.get_topic(tid) else []
        topics.append({
            "id":       tid,
            "label":    " · ".join(kws[:3]),
            "keywords": kws,
            "size":     int(row["Count"]),
            "share_pct": round(100 * int(row["Count"]) / len(texts_clean), 2),
        })

    metrics = {"n_clusters": len(topics), "silhouette": None}
    return labels, topics, metrics


# ──────────────────────────────────────────────────────────────────────────────
# Platform migration analysis (iDRAMA Lab methodology)
# ──────────────────────────────────────────────────────────────────────────────

def platform_migration(all_datasets):
    """
    Build a cross-platform timeline: for each month, count posts per platform.
    Replicates the iDRAMA Lab's platform-diaspora analysis.
    """
    # POST-AUDIT NOTE (see audit.html): this timeline is NOT a clean platform
    # diaspora. Its columns mix two incompatible sources: the REAL qdrops board
    # labels ("4ch"=4chan-era, "8ch"=8chan, "8kun"=8kun) and the SYNTHETIC platform
    # samples ("4chan", "reddit", "parler", "telegram", "twitter", and a synthetic
    # "8kun"). We deliberately do NOT merge "8ch"→"8kun" (they are a real 2019
    # transition, not duplicate labels) nor "4ch"→"4chan" (that would blend real
    # qdrops with synthetic seed data). The iDRAMA "diaspora" replication is invalid
    # on this data until real downstream corpora replace the synthetic samples.
    monthly = defaultdict(lambda: defaultdict(int))
    for ds_id, posts in all_datasets.items():
        for p in posts:
            ts = p.get("timestamp", 0)
            if not ts:
                continue
            dt     = datetime.fromtimestamp(ts, tz=timezone.utc)
            period = dt.strftime("%Y-%m")
            platform = p.get("platform", ds_id)
            monthly[period][platform] += 1

    timeline = []
    for period in sorted(monthly.keys()):
        entry = {"period": period}
        entry.update(dict(monthly[period]))
        timeline.append(entry)
    return timeline


# ──────────────────────────────────────────────────────────────────────────────
# Cross-platform topic overlap (Hoseini et al. 2021 methodology)
# ──────────────────────────────────────────────────────────────────────────────

def jaccard(set_a, set_b):
    if not set_a and not set_b:
        return 0.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return round(inter / union, 4) if union else 0.0


# POST-AUDIT FIX: strip English function words before computing topic overlap.
# Previously ~27% of "shared keywords" across pairs were stopwords ("in", "on",
# "they", "and"…), inflating the Jaccard so it partly measured shared grammar
# rather than shared narrative. BERTopic's c-TF-IDF labels retain stopwords, so we
# filter them here at the overlap step.
try:
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS as _SK_STOP
    OVERLAP_STOPWORDS = set(_SK_STOP)
except Exception:  # keep the script runnable without sklearn
    OVERLAP_STOPWORDS = set(
        "a an and are as at be been but by can could do does did for from had has have "
        "he her here him his how i in is it its me my no not now of on or our out so that "
        "the their them then there these they this those to up us was we were what when "
        "where which who why will with you your".split())


def _content_keywords(topics, k=10):
    """Top-k keywords per topic with English stopwords and empties removed."""
    kws = set()
    for t in topics:
        for w in t.get("keywords", [])[:k]:
            w = (w or "").strip().lower()
            if w and w not in OVERLAP_STOPWORDS and not w.isdigit():
                kws.add(w)
    return kws


def cross_platform_topic_overlap(dataset_topics):
    """
    For each pair of datasets compute Jaccard overlap of their top-10 topic keywords.
    Replicates Hoseini et al. 2021's cross-platform topic matching (stopword-filtered).
    """
    dataset_ids = list(dataset_topics.keys())
    overlap_matrix = {}

    for i, ds_a in enumerate(dataset_ids):
        for ds_b in dataset_ids[i+1:]:
            kws_a = _content_keywords(dataset_topics[ds_a])
            kws_b = _content_keywords(dataset_topics[ds_b])
            j = jaccard(kws_a, kws_b)
            overlap_matrix[f"{ds_a}|{ds_b}"] = {
                "dataset_a": ds_a,
                "dataset_b": ds_b,
                "jaccard":   j,
                "shared_keywords": sorted(kws_a & kws_b),
            }

    return overlap_matrix


# ──────────────────────────────────────────────────────────────────────────────
# Per-dataset analysis
# ──────────────────────────────────────────────────────────────────────────────

def analyse_dataset(posts, dataset_id, method="kmeans", k=10):
    """Run clustering, BITE scoring, and motivated-reasoning on one dataset."""
    from bite_scorer import BITEScorer

    print(f"  [{dataset_id}] {len(posts)} posts")
    texts = [p.get("text", "") for p in posts]

    # ── Clustering ─────────────────────────────────────────────────────────
    print(f"  [{dataset_id}] clustering ({method}) ...")
    t0 = time.time()
    if method == "bertopic":
        labels, topics, cluster_metrics = cluster_bertopic(texts)
    else:
        labels, topics, cluster_metrics = cluster_kmeans(texts, k=k)
    cluster_time = round(time.time() - t0, 2)
    print(f"  [{dataset_id}] {len(topics)} clusters in {cluster_time}s  "
          f"(sil={cluster_metrics.get('silhouette', '?')})")

    # Attach cluster label to each post (for downstream use)
    for i, p in enumerate(posts):
        p["_cluster"] = labels[i] if i < len(labels) else -1

    # ── BITE scoring ────────────────────────────────────────────────────────
    print(f"  [{dataset_id}] BITE scoring ...")
    scorer = BITEScorer()
    bite_scored = scorer.score_corpus(posts)
    bite_agg    = scorer.aggregate(bite_scored)
    bite_tl     = scorer.temporal_profile(bite_scored, window="month")

    # ── Motivated reasoning ────────────────────────────────────────────────
    print(f"  [{dataset_id}] motivated-reasoning scoring ...")
    mr_scores  = [score_motivated_reasoning(p.get("text","")) for p in posts]
    mr_mean    = round(sum(s["score"] for s in mr_scores) / len(mr_scores), 4) if mr_scores else 0
    mr_dist    = Counter(
        "high" if s["score"] >= 0.5 else ("medium" if s["score"] >= 0.25 else "low")
        for s in mr_scores
    )

    # ── Board / platform stats ─────────────────────────────────────────────
    board_counts = Counter(p.get("board", "") for p in posts)
    year_counts  = Counter(
        datetime.fromtimestamp(p["timestamp"], tz=timezone.utc).strftime("%Y")
        for p in posts if p.get("timestamp")
    )

    return {
        "dataset_id":    dataset_id,
        "n_posts":       len(posts),
        "cluster": {
            "method":    method,
            "n_clusters": cluster_metrics.get("n_clusters", len(topics)),
            "metrics":   cluster_metrics,
            "topics":    topics,
            "time_s":    cluster_time,
        },
        "bite": {
            "aggregate": bite_agg,
            "timeline":  bite_tl,
        },
        "motivated_reasoning": {
            "mean_score": mr_mean,
            "distribution": dict(mr_dist),
        },
        "corpus": {
            "boards":    dict(board_counts.most_common(10)),
            "by_year":   dict(sorted(year_counts.items())),
        },
    }


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def load_posts(dataset_id, samples_only=False):
    """Load posts from normalised dir, falling back to sample."""
    norm_path   = f"{NORM_DIR}/{dataset_id}.json"
    sample_path = f"{SAMPLES_DIR}/{dataset_id}_sample.json"

    if not samples_only and os.path.exists(norm_path):
        with open(norm_path, encoding="utf-8") as f:
            return json.load(f), "normalised"
    if os.path.exists(sample_path):
        with open(sample_path, encoding="utf-8") as f:
            return json.load(f), "sample"
    return None, None


def main():
    ap = argparse.ArgumentParser(description="Multi-dataset clustering + BITE analysis")
    ap.add_argument("--dataset",      help="run only this dataset ID")
    ap.add_argument("--method",       default="kmeans", choices=["kmeans", "bertopic"],
                    help="clustering method (default: kmeans)")
    ap.add_argument("--k",            type=int, default=10, help="KMeans clusters (default 10)")
    ap.add_argument("--no-clustering",action="store_true",  help="skip clustering, BITE only")
    ap.add_argument("--samples-only", action="store_true",  help="use 500-post samples")
    args = ap.parse_args()

    catalog = json.load(open(CATALOG_PATH))
    os.makedirs(RESULTS_DIR, exist_ok=True)

    dataset_ids = [d["id"] for d in catalog["datasets"]]
    if args.dataset:
        dataset_ids = [args.dataset]

    all_posts   = {}
    all_results = {}
    all_topics  = {}

    # ── Per-dataset analysis ───────────────────────────────────────────────
    for did in dataset_ids:
        posts, source = load_posts(did, samples_only=args.samples_only)
        if posts is None:
            print(f"[{did}] no data found — run collect_datasets.py first")
            continue

        print(f"\n{'='*60}")
        print(f"Dataset: {did}  ({source}, {len(posts)} posts)")
        print('='*60)

        all_posts[did] = posts

        if args.no_clustering:
            from bite_scorer import BITEScorer
            scorer      = BITEScorer()
            bite_scored = scorer.score_corpus(posts)
            bite_agg    = scorer.aggregate(bite_scored)
            result = {
                "dataset_id": did,
                "n_posts":    len(posts),
                "bite":       {"aggregate": bite_agg, "timeline": scorer.temporal_profile(bite_scored)},
            }
        else:
            result = analyse_dataset(posts, did, method=args.method, k=args.k)
            all_topics[did] = result["cluster"]["topics"]

        all_results[did] = result

        # Write per-dataset result
        out_dir  = f"{RESULTS_DIR}/{did}"
        os.makedirs(out_dir, exist_ok=True)
        out_path = f"{out_dir}/analysis.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"  → {out_path}")

    # ── Cross-dataset analyses ─────────────────────────────────────────────
    cross = {}

    if len(all_posts) >= 2:
        print("\n── Cross-platform migration ──────────────────────────────")
        cross["platform_migration"] = platform_migration(all_posts)
        print(f"  {len(cross['platform_migration'])} monthly data points")

    if len(all_topics) >= 2:
        print("\n── Cross-platform topic overlap (Hoseini et al. 2021) ───")
        overlap = cross_platform_topic_overlap(all_topics)
        cross["topic_overlap"] = overlap
        for pair, data in sorted(overlap.items(), key=lambda x: -x[1]["jaccard"])[:10]:
            print(f"  {data['dataset_a']:15} × {data['dataset_b']:15}  Jaccard={data['jaccard']:.3f}  "
                  f"shared: {', '.join(data['shared_keywords'][:5])}")

    # ── Comparative BITE summary ───────────────────────────────────────────
    print("\n── BITE model summary across datasets ───────────────────────")
    print(f"{'Dataset':<22} {'B':>6} {'I':>6} {'T':>6} {'E':>6}  {'Total':>7}  Dominant")
    print("-" * 75)
    for did, result in all_results.items():
        agg = result.get("bite", {}).get("aggregate", {})
        b   = agg.get("B",     {}).get("mean", 0)
        i   = agg.get("I",     {}).get("mean", 0)
        t   = agg.get("T",     {}).get("mean", 0)
        e   = agg.get("E",     {}).get("mean", 0)
        tot = agg.get("total", {}).get("mean", 0)
        dom = agg.get("corpus_dominant", "?")
        print(f"{did:<22} {b:>6.3f} {i:>6.3f} {t:>6.3f} {e:>6.3f}  {tot:>7.3f}  {dom}")

    # ── Write master index ─────────────────────────────────────────────────
    index = {
        "generated":    datetime.now(tz=timezone.utc).isoformat(),
        "method":       args.method,
        "datasets":     list(all_results.keys()),
        "cross":        cross,
        "bite_summary": {
            did: {
                dim: result.get("bite", {}).get("aggregate", {}).get(dim, {}).get("mean", 0)
                for dim in ["B", "I", "T", "E", "total"]
            }
            for did, result in all_results.items()
        },
    }
    index_path = f"{RESULTS_DIR}/index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"\n  Master index → {index_path}")
    print("  Done. Run compare_results.py to generate the comparison report.")


if __name__ == "__main__":
    main()
