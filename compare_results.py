#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compare_results.py — Generate a cross-dataset comparison report.

Reads results/index.json + results/<dataset>/analysis.json for every dataset
and produces:
  1. compare_results.json  — machine-readable comparison for the web dashboard
  2. compare_results.html  — self-contained interactive comparison page

USAGE
-----
    python compare_results.py
    python compare_results.py --output my_report.json
"""

import argparse
import json
import os
from datetime import datetime, timezone

RESULTS_DIR  = "results"
INDEX_PATH   = f"{RESULTS_DIR}/index.json"
OUT_JSON     = "compare_results.json"
OUT_HTML     = "compare_results.html"

DIM_NAMES    = {"B": "Behavior Control", "I": "Information Control",
                "T": "Thought Control",  "E": "Emotional Control"}
DIM_COLORS   = {"B": "#e74c3c", "I": "#e67e22", "T": "#9b59b6", "E": "#3498db"}


# ──────────────────────────────────────────────────────────────────────────────
# Data loading
# ──────────────────────────────────────────────────────────────────────────────

def load_results():
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(
            f"Index not found at {INDEX_PATH}. Run multi_dataset_analysis.py first."
        )
    with open(INDEX_PATH, encoding="utf-8") as f:
        index = json.load(f)

    dataset_results = {}
    for did in index.get("datasets", []):
        path = f"{RESULTS_DIR}/{did}/analysis.json"
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                dataset_results[did] = json.load(f)

    return index, dataset_results


# ──────────────────────────────────────────────────────────────────────────────
# Build comparison object
# ──────────────────────────────────────────────────────────────────────────────

def build_comparison(index, results):
    dims = ["B", "I", "T", "E"]

    # ── 1. BITE comparison table ───────────────────────────────────────────
    bite_table = []
    for did, res in results.items():
        agg = res.get("bite", {}).get("aggregate", {})
        row = {
            "dataset": did,
            "n_posts": res.get("n_posts", 0),
        }
        for dim in dims:
            d = agg.get(dim, {})
            row[dim]               = d.get("mean",   0)
            row[f"{dim}_std"]      = d.get("std",    0)
            row[f"{dim}_pervasive"] = d.get("dist",  {}).get("pervasive", 0)
        row["total"]   = agg.get("total",  {}).get("mean", 0)
        row["dominant"] = agg.get("corpus_dominant", "?")
        bite_table.append(row)

    bite_table.sort(key=lambda r: -r["total"])

    # ── 2. Topic comparison (Hoseini methodology) ──────────────────────────
    topic_overlap = index.get("cross", {}).get("topic_overlap", {})
    topic_comp = []
    for pair_key, data in topic_overlap.items():
        topic_comp.append({
            "pair":    pair_key,
            "ds_a":    data["dataset_a"],
            "ds_b":    data["dataset_b"],
            "jaccard": data["jaccard"],
            "shared":  data.get("shared_keywords", []),
        })
    topic_comp.sort(key=lambda x: -x["jaccard"])

    # ── 3. Platform migration (iDRAMA methodology) ─────────────────────────
    migration = index.get("cross", {}).get("platform_migration", [])

    # ── 4. Motivated reasoning comparison ─────────────────────────────────
    mr_comp = []
    for did, res in results.items():
        mr = res.get("motivated_reasoning", {})
        mr_comp.append({
            "dataset":    did,
            "mean_score": mr.get("mean_score", 0),
            "pct_high":   round(100 * mr.get("distribution", {}).get("high", 0) /
                                max(res.get("n_posts", 1), 1), 1),
        })
    mr_comp.sort(key=lambda x: -x["mean_score"])

    # ── 5. Cluster quality ─────────────────────────────────────────────────
    cluster_comp = []
    for did, res in results.items():
        cl = res.get("cluster", {})
        if cl:
            cluster_comp.append({
                "dataset":      did,
                "n_clusters":   cl.get("n_clusters", 0),
                "silhouette":   cl.get("metrics", {}).get("silhouette") or 0,
                "top_topics":   [t["label"] for t in cl.get("topics", [])[:5]],
            })

    # ── 6. Top BITE posts (for the dashboard spotlight) ───────────────────
    highlights = []
    for did, res in results.items():
        bite_tl = res.get("bite", {}).get("timeline", [])
        agg     = res.get("bite", {}).get("aggregate", {})
        dom     = agg.get("corpus_dominant", "?")
        peak    = max(bite_tl, key=lambda x: x.get(f"{dom}_mean", 0)) if bite_tl and dom != "?" else {}
        highlights.append({
            "dataset":         did,
            "dominant_dim":    dom,
            "dominant_name":   DIM_NAMES.get(dom, dom),
            "total_mean":      agg.get("total", {}).get("mean", 0),
            "peak_period":     peak.get("period", "—"),
            "peak_dim_score":  peak.get(f"{dom}_mean", 0) if dom != "?" else 0,
        })

    return {
        "generated":     datetime.now(tz=timezone.utc).isoformat(),
        "n_datasets":    len(results),
        "datasets":      list(results.keys()),
        "bite_table":    bite_table,
        "topic_overlap": topic_comp,
        "migration":     migration,
        "motivated_reasoning": mr_comp,
        "cluster_quality":     cluster_comp,
        "highlights":          highlights,
        "dim_names":     DIM_NAMES,
        "dim_colors":    DIM_COLORS,
    }


# ──────────────────────────────────────────────────────────────────────────────
# HTML report
# ──────────────────────────────────────────────────────────────────────────────

def bar(value, color="#3498db", max_val=1.0):
    pct = min(100, round(100 * value / max(max_val, 0.001)))
    return (f'<div style="background:#eee;border-radius:3px;height:10px;width:200px;display:inline-block;">'
            f'<div style="background:{color};width:{pct}%;height:10px;border-radius:3px;"></div></div>'
            f' <small>{value:.3f}</small>')


def build_html(comp):
    dims    = ["B", "I", "T", "E"]
    colors  = comp["dim_colors"]
    names   = comp["dim_names"]
    rows_bite = ""
    for r in comp["bite_table"]:
        cells = "".join(
            f'<td style="white-space:nowrap">{bar(r.get(d,0), colors[d])}</td>'
            for d in dims
        )
        rows_bite += (
            f'<tr><td><strong>{r["dataset"]}</strong></td>'
            f'<td>{r["n_posts"]:,}</td>'
            f'{cells}'
            f'<td>{bar(r["total"])}</td>'
            f'<td><span style="background:{colors.get(r["dominant"],"#888")};color:#fff;'
            f'padding:2px 8px;border-radius:12px;font-size:0.85em">'
            f'{r["dominant"]} – {names.get(r["dominant"],"")}</span></td></tr>\n'
        )

    rows_overlap = ""
    for r in comp["topic_overlap"][:20]:
        j = r["jaccard"]
        color = "#27ae60" if j > 0.4 else ("#e67e22" if j > 0.2 else "#95a5a6")
        rows_overlap += (
            f'<tr><td>{r["ds_a"]}</td><td>{r["ds_b"]}</td>'
            f'<td>{bar(j, color, max_val=0.8)}</td>'
            f'<td style="font-size:0.85em">{", ".join(r["shared"][:6])}</td></tr>\n'
        )

    rows_mr = ""
    for r in comp["motivated_reasoning"]:
        rows_mr += (
            f'<tr><td>{r["dataset"]}</td>'
            f'<td>{bar(r["mean_score"], "#9b59b6")}</td>'
            f'<td>{r["pct_high"]}%</td></tr>\n'
        )

    rows_cl = ""
    for r in comp["cluster_quality"]:
        sil = r["silhouette"] or 0
        rows_cl += (
            f'<tr><td>{r["dataset"]}</td><td>{r["n_clusters"]}</td>'
            f'<td>{bar(sil, "#27ae60")}</td>'
            f'<td style="font-size:0.85em">{"; ".join(r["top_topics"][:3])}</td></tr>\n'
        )

    # Highlight cards
    highlight_cards = ""
    for h in comp["highlights"]:
        c = colors.get(h["dominant_dim"], "#888")
        highlight_cards += f"""
<div style="border:2px solid {c};border-radius:8px;padding:16px;margin:8px;
            min-width:200px;max-width:260px;display:inline-block;vertical-align:top">
  <div style="font-size:1.1em;font-weight:bold;color:{c}">{h["dataset"]}</div>
  <div style="font-size:0.85em;color:#666;margin:4px 0">Dominant: {h["dominant_name"]}</div>
  <div style="font-size:1.8em;font-weight:bold">{h["total_mean"]:.2f}</div>
  <div style="font-size:0.8em;color:#888">avg BITE score</div>
  <div style="font-size:0.8em;margin-top:6px">
    Peak: <strong>{h["peak_period"]}</strong>
    ({h["dominant_dim"]}={h["peak_dim_score"]:.3f})
  </div>
</div>"""

    # Migration mini-table (last 12 periods)
    migration = comp.get("migration", [])[-12:]
    platforms = set()
    for m in migration:
        platforms.update(k for k in m if k != "period")
    platforms = sorted(platforms)
    mig_head  = "<tr><th>Period</th>" + "".join(f"<th>{p}</th>" for p in platforms) + "</tr>"
    mig_rows  = ""
    for m in migration:
        mig_rows += "<tr><td>" + m["period"] + "</td>"
        mig_rows += "".join(f'<td style="text-align:right">{m.get(p,"—"):,}</td>'
                            if isinstance(m.get(p), int) else f'<td>—</td>'
                            for p in platforms)
        mig_rows += "</tr>\n"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Cross-Dataset Comparison — QAnon NLP Analysis</title>
<style>
  body{{font-family:system-ui,sans-serif;margin:0;padding:24px;background:#f8f9fa;color:#212529}}
  h1{{color:#2c3e50;border-bottom:3px solid #3498db;padding-bottom:8px}}
  h2{{color:#34495e;margin-top:32px}}
  table{{border-collapse:collapse;width:100%;background:#fff;
        box-shadow:0 1px 3px rgba(0,0,0,.1);border-radius:6px;overflow:hidden}}
  th{{background:#2c3e50;color:#fff;padding:10px 12px;text-align:left;font-size:.9em}}
  td{{padding:9px 12px;border-bottom:1px solid #ecf0f1;font-size:.9em}}
  tr:last-child td{{border-bottom:none}}
  tr:hover td{{background:#f8f9fa}}
  .meta{{color:#666;font-size:.85em;margin-bottom:24px}}
  .section{{margin-bottom:40px}}
  .note{{background:#eaf4fb;border-left:4px solid #3498db;padding:10px 16px;
         border-radius:3px;font-size:.9em;color:#2c3e50;margin:12px 0}}
</style>
</head>
<body>
<h1>QAnon Multi-Dataset Comparison Report</h1>
<p class="meta">
  Generated: {comp["generated"]} ·
  Datasets: {comp["n_datasets"]} ·
  <a href="compare_results.json">Download JSON</a>
</p>

<div class="note">
  <strong>Methodology.</strong> Clustering: TF-IDF + KMeans (or BERTopic where available).
  BITE scoring: keyword-weighted lexicon (Hassan 2018). Topic overlap: Jaccard similarity
  on top-10 cluster keywords (Hoseini et al. 2021). Motivated reasoning: keyword classifier
  (Priniski &amp; Bavel 2021). Platform migration: monthly post counts per platform (iDRAMA Lab).
</div>

<div class="section">
<h2>Dataset Highlights</h2>
<div style="display:flex;flex-wrap:wrap;gap:8px">
{highlight_cards}
</div>
</div>

<div class="section">
<h2>BITE Model Scores by Dataset</h2>
<p style="font-size:.85em;color:#666">Mean score per dimension (0 = absent → 1 = pervasive).
  Dominant dimension shown as coloured badge.</p>
<table>
<tr>
  <th>Dataset</th><th>Posts</th>
  <th>B – Behavior</th><th>I – Information</th>
  <th>T – Thought</th><th>E – Emotional</th>
  <th>Total</th><th>Dominant</th>
</tr>
{rows_bite}
</table>
</div>

<div class="section">
<h2>Cross-Platform Topic Overlap <small style="font-weight:normal;color:#666">(Hoseini et al. 2021)</small></h2>
<p style="font-size:.85em;color:#666">Jaccard similarity of top-10 cluster keywords between dataset pairs.
  Higher = more narrative overlap across platforms.</p>
<table>
<tr><th>Dataset A</th><th>Dataset B</th><th>Jaccard Overlap</th><th>Shared Keywords</th></tr>
{rows_overlap if rows_overlap else '<tr><td colspan="4" style="color:#aaa">Need ≥2 datasets with clustering results</td></tr>'}
</table>
</div>

<div class="section">
<h2>Motivated Reasoning <small style="font-weight:normal;color:#666">(Priniski &amp; Bavel 2021)</small></h2>
<p style="font-size:.85em;color:#666">Mean score of identity-protective reasoning markers
  (certainty, us-vs-them, dismissal, in-group language).</p>
<table>
<tr><th>Dataset</th><th>Mean Score</th><th>% High Scorers</th></tr>
{rows_mr}
</table>
</div>

<div class="section">
<h2>Cluster Quality</h2>
<p style="font-size:.85em;color:#666">Silhouette score (−1 to 1; higher = better-separated topics).</p>
<table>
<tr><th>Dataset</th><th>Clusters</th><th>Silhouette</th><th>Top Topics</th></tr>
{rows_cl if rows_cl else '<tr><td colspan="4" style="color:#aaa">No clustering results yet</td></tr>'}
</table>
</div>

<div class="section">
<h2>Platform Migration Timeline <small style="font-weight:normal;color:#666">(iDRAMA Lab)</small></h2>
<p style="font-size:.85em;color:#666">Monthly post volume per platform (last 12 available periods).</p>
<table>
{mig_head}
{mig_rows if mig_rows else '<tr><td colspan="10" style="color:#aaa">No migration data yet</td></tr>'}
</table>
</div>

<div class="note" style="margin-top:40px">
  <strong>References.</strong><br>
  Hoseini et al. (2021). <em>How Globalization of QAnon Bypasses Twitter's Ban.</em> ICWSM.<br>
  iDRAMA Lab (2021). <em>An Early Look at the Parler Online Social Network.</em> ICWSM.<br>
  Priniski &amp; Bavel (2021). <em>Identity-based motivation and QAnon.</em> Perspectives on Psychological Science.<br>
  Hassan, S. (2018). <em>Combating Cult Mind Control.</em> Freedom of Mind Press.<br>
  Kingsman, J. (2025). <em>JSON-QAnon.</em> DOI 10.13140/RG.2.2.28778.32964.
</div>
</body>
</html>
"""


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Generate cross-dataset comparison report")
    ap.add_argument("--output", default=OUT_JSON, help=f"JSON output path (default: {OUT_JSON})")
    ap.add_argument("--html",   default=OUT_HTML, help=f"HTML output path (default: {OUT_HTML})")
    args = ap.parse_args()

    print("Loading results...")
    index, results = load_results()
    print(f"  {len(results)} datasets: {', '.join(results.keys())}")

    print("Building comparison...")
    comp = build_comparison(index, results)

    # Write JSON
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(comp, f, ensure_ascii=False, indent=2)
    print(f"  JSON → {args.output}")

    # Write HTML
    html_out = build_html(comp)
    with open(args.html, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"  HTML → {args.html}")

    # Print summary to console
    print(f"\n{'='*65}")
    print(f"{'Dataset':<22} {'B':>6} {'I':>6} {'T':>6} {'E':>6} {'Total':>7}")
    print("-" * 65)
    for r in comp["bite_table"]:
        dims = " ".join(f"{r.get(d,0):>6.3f}" for d in ["B","I","T","E"])
        print(f"{r['dataset']:<22} {dims} {r['total']:>7.3f}")

    print(f"\nAll done. Open {args.html} in a browser to view the report.")
    print(f"Or serve: python3 -m http.server 8000 → http://localhost:8000/{args.html}")


if __name__ == "__main__":
    main()
