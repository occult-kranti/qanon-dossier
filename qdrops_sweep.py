#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qdrops_sweep.py  --  Run several clustering configurations and measure which topics are REAL.

The single-run script (qdrops_cluster.py) gives you one clustering. But clustering is
parameter-sensitive: change the embedding model or HDBSCAN's min_cluster_size and the
topics shift. The honest move is to run it several ways and keep only the topics that
PERSIST. This driver does that and quantifies it.

WHAT IT DOES
------------
1. Loads + normalises the drops ONCE (so every config sees the identical drop set).
2. For each embedding model it embeds ONCE, then clusters at each min_cluster_size
   (so the 15/25/40 variants of a model reuse the same embeddings -- fast).
3. Scores every run: silhouette (separation) + gensim c_v coherence (interpretability).
4. Writes each run to its own file:  run_<model>_mcs<N>.json   (any can be opened in drops.html)
5. STABILITY: because all runs cluster the same drops, it matches topics across runs by
   document-membership overlap (Jaccard). A topic's *persistence* = its mean best-overlap
   with the other runs. High persistence = robust/real; low = an artifact of the settings.
6. Writes stability_report.json + stability_report.csv and prints a ranked summary.
   drops.html has a "Stability" panel that loads stability_report.json.

USAGE
-----
    pip install -r requirements.txt
    python qdrops_sweep.py                                   # MiniLM x {15,25,40}
    python qdrops_sweep.py --mcs 15,25,40 --models all-MiniLM-L6-v2,all-mpnet-base-v2
    python qdrops_sweep.py --method hdbscan --drop-admin     # exclude admin drops, no BERTopic
    python qdrops_sweep.py --no-coherence                    # faster (skip c_v)

Each run file is a normal drops.html dataset; stability_report.json drives the Stability panel.
"""

import argparse
import csv
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

import qdrops_cluster as qc


def short_model(m):
    return (m.split("/")[-1].replace("all-", "").replace("sentence-transformers-", "")
            .replace("-v2", "").replace("-v1", ""))


def jaccard(a, b):
    if not a and not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def membership(topics):
    """topic_id -> set(doc indices), excluding noise (-1)."""
    m = defaultdict(set)
    for i, t in enumerate(topics):
        if t != -1:
            m[int(t)].add(i)
    return m


def verdict(p):
    if p is None:
        return "n/a"
    if p >= 0.5:
        return "stable"
    if p >= 0.3:
        return "borderline"
    return "fragile"


def main():
    ap = argparse.ArgumentParser(description="Sweep clustering configs and score topic stability.")
    ap.add_argument("--method", choices=["bertopic", "hdbscan", "kmeans"], default="bertopic")
    ap.add_argument("--models", default=qc.EMBED_MODEL,
                    help="comma-separated sentence-transformers models")
    ap.add_argument("--mcs", default="15,25,40",
                    help="comma-separated HDBSCAN min_cluster_size values (or k values for kmeans)")
    ap.add_argument("--reduce-outliers", action="store_true")
    ap.add_argument("--drop-admin", action="store_true")
    ap.add_argument("--author-filter", default=None)
    ap.add_argument("--no-coherence", action="store_true")
    ap.add_argument("--input", default=qc.DEFAULT_INPUT)
    ap.add_argument("--no-download", action="store_true")
    ap.add_argument("--out-prefix", default="run")
    ap.add_argument("--report", default="stability_report.json")
    ap.add_argument("--max-posts", type=int, default=0)
    args = ap.parse_args()

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    mcs_list = [int(x) for x in args.mcs.split(",") if x.strip()]
    if len(models) * len(mcs_list) < 2:
        print("[warn] stability needs >= 2 configs; add more --models or --mcs values.")

    # ---- load + normalise ONCE ----
    if not args.no_download:
        qc.download_dataset(args.input)
    if not os.path.exists(args.input):
        sys.exit(f"ERROR: {args.input} not found. Get it from {qc.RAW_URL}")
    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)
    posts = qc.coerce_posts(data)
    print(f"[load] {len(posts)} posts")
    rows, comp = qc.normalise(posts, author_filter=args.author_filter, drop_admin=args.drop_admin)
    if args.max_posts:
        rows = rows[: args.max_posts]
    docs = [r["_clean"] for r in rows]
    print(f"[sweep] fixed drop set: {len(docs)} drops · "
          f"{len(models)} model(s) x {len(mcs_list)} setting(s) = {len(models)*len(mcs_list)} runs\n")

    runs = []  # {tag, model, mcs, topics, keywords, validity, n_topics, file}
    for model in models:
        embeddings = None if args.method == "kmeans" else qc.embed_docs(docs, model)
        for mcs in mcs_list:
            tag = f"{short_model(model)}_mcs{mcs}" if args.method != "kmeans" else f"{short_model(model)}_k{mcs}"
            print(f"\n--- run {tag} ---")
            result, coords2d = qc.cluster_once(docs, embeddings, args.method,
                                               mcs, mcs, args.reduce_outliers)
            validity = qc.compute_validity(result["space"], result["topics"], docs,
                                           result["keywords"], do_coherence=not args.no_coherence)
            embed_name = model if args.method != "kmeans" else "TF-IDF"
            params = {"min_cluster_size": mcs, "reduce_outliers": args.reduce_outliers,
                      "drop_admin": args.drop_admin}
            payload = qc.build_payload(rows, result, coords2d, validity, comp,
                                       args.method, embed_name, params)
            out_file = f"{args.out_prefix}_{tag}.json"
            qc.write_payload(payload, out_file)
            n_topics = len([t for t in set(result["topics"]) if t != -1])
            runs.append({"tag": tag, "model": model, "mcs": mcs, "topics": result["topics"],
                         "keywords": result["keywords"], "validity": validity,
                         "n_topics": n_topics, "file": out_file})

    # ---- cross-run stability via membership Jaccard ----
    print("\n================ STABILITY ================")
    mems = [membership(r["topics"]) for r in runs]
    sizes = [Counter(t for t in r["topics"] if t != -1) for r in runs]

    # pairwise mean best-Jaccard between runs (how similar two clusterings are overall)
    pairwise = {}
    for i in range(len(runs)):
        for j in range(len(runs)):
            if i >= j:
                continue
            best = []
            for a, sa in mems[i].items():
                bj = max((jaccard(sa, sb) for sb in mems[j].values()), default=0.0)
                best.append(bj)
            score = round(sum(best) / len(best), 3) if best else 0.0
            pairwise[f"{runs[i]['tag']}|{runs[j]['tag']}"] = score

    # per-run, per-topic persistence = mean over OTHER runs of best Jaccard
    for ri, r in enumerate(runs):
        persistence = {}
        for a, sa in mems[ri].items():
            others = []
            for rj in range(len(runs)):
                if rj == ri:
                    continue
                bj = max((jaccard(sa, sb) for sb in mems[rj].values()), default=0.0)
                others.append(bj)
            persistence[a] = round(sum(others) / len(others), 3) if others else None
        r["persistence"] = persistence
        vals = [p for p in persistence.values() if p is not None]
        r["mean_persistence"] = round(sum(vals) / len(vals), 3) if vals else None

    # anchor = run with highest mean topic persistence (most representative clustering)
    scored = [r for r in runs if r["mean_persistence"] is not None]
    anchor = max(scored, key=lambda r: r["mean_persistence"]) if scored else runs[0]
    ai = runs.index(anchor)

    anchor_topics = []
    for t, p in sorted(anchor["persistence"].items(), key=lambda kv: (-(kv[1] or 0), kv[0])):
        anchor_topics.append({
            "topic": t, "label": qc._labels_from_keywords(anchor["keywords"]).get(t, f"topic {t}"),
            "keywords": anchor["keywords"].get(t, [])[:8], "size": sizes[ai].get(t, 0),
            "persistence": p, "verdict": verdict(p),
        })

    # ---- print summary ----
    print("\nPer-run quality (sorted by mean topic persistence):")
    print(f"  {'run':24} {'topics':>6} {'silhouette':>10} {'c_v':>6} {'persistence':>11}")
    for r in sorted(runs, key=lambda r: -(r["mean_persistence"] or 0)):
        sil = r["validity"]["silhouette"]; coh = r["validity"]["coherence_cv_mean"]
        mp = r["mean_persistence"]
        print(f"  {r['tag']:24} {r['n_topics']:>6} "
              f"{('  n/a' if sil is None else f'{sil:>10.3f}')} "
              f"{('  n/a' if coh is None else f'{coh:>6.2f}')} "
              f"{('  n/a' if mp is None else f'{mp:>11.3f}')}")

    n_stable = sum(1 for t in anchor_topics if t["verdict"] == "stable")
    print(f"\nAnchor run: {anchor['tag']}  ->  {n_stable}/{len(anchor_topics)} topics are STABLE "
          f"(persist >=0.5 across the other runs)")
    print("Most -> least stable topics in the anchor run:")
    for t in anchor_topics:
        mark = {"stable": "[OK ]", "borderline": "[~~ ]", "fragile": "[!! ]", "n/a": "[ ? ]"}[t["verdict"]]
        pp = "  n/a" if t["persistence"] is None else f"{t['persistence']:>4.2f}"
        print(f"  {mark} persist={pp}  #{t['topic']:<3} ({t['size']:>4})  {', '.join(t['keywords'][:6])}")

    # ---- write reports ----
    report = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "method": args.method, "n_drops": len(docs),
        "runs": [{"tag": r["tag"], "model": r["model"], "mcs": r["mcs"],
                  "n_topics": r["n_topics"], "file": r["file"],
                  "silhouette": r["validity"]["silhouette"],
                  "coherence": r["validity"]["coherence_cv_mean"],
                  "mean_persistence": r["mean_persistence"]} for r in runs],
        "pairwise": pairwise, "anchor": anchor["tag"], "anchor_topics": anchor_topics,
    }
    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n[out] {args.report}")
    csvp = os.path.splitext(args.report)[0] + ".csv"
    with open(csvp, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["anchor_run", "topic", "label", "size", "persistence", "verdict", "keywords"])
        for t in anchor_topics:
            w.writerow([anchor["tag"], t["topic"], t["label"], t["size"],
                        t["persistence"], t["verdict"], ", ".join(t["keywords"])])
    print(f"[out] {csvp}")
    print("\nDone. Open any run_*.json in drops.html, and load stability_report.json in the Stability panel.")


if __name__ == "__main__":
    main()
