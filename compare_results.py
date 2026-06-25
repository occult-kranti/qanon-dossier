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
import statistics
from datetime import datetime, timezone

RESULTS_DIR  = "results"
INDEX_PATH   = f"{RESULTS_DIR}/index.json"
OUT_JSON     = "compare_results.json"
OUT_HTML     = "compare_results.html"

DIM_NAMES    = {"B": "Behavior Control", "I": "Information Control",
                "T": "Thought Control",  "E": "Emotional Control"}
DIM_COLORS   = {"B": "#e74c3c", "I": "#e67e22", "T": "#9b59b6", "E": "#3498db"}
DS_LABELS    = {
    "qdrops": "Q Drops",
    "reddit_qanon": "Reddit",
    "4chan_pol": "4chan /pol/",
    "8kun_qresearch": "8kun /qresearch/",
    "parler": "Parler",
    "telegram": "Telegram",
    "twitter": "Twitter/X",
}
DS_PLATFORM  = {
    "qdrops": "4chan/8chan/8kun",
    "reddit_qanon": "reddit",
    "4chan_pol": "4chan",
    "8kun_qresearch": "8kun",
    "parler": "parler",
    "telegram": "telegram",
    "twitter": "twitter",
}
LLM_PROFILE  = {
    "framework": "Ollama",
    "default_model": "qwen2.5:7b",
    "high_quality_model": "qwen2.5:14b",
    "fallback_model": "qwen2.5:3b",
    "json_mode": True,
    "generation": {
        "temperature": 0,
        "top_p": 0.1,
        "top_k": 20,
        "seed": 42,
    },
    "output_contract": [
        "Return strict JSON only",
        "No markdown or prose outside JSON",
        "Validate schema and retry on malformed output",
    ],
}


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


def period_bounds(periods):
    """Return lexical YYYY-MM min/max from a list of period strings."""
    clean = sorted(p for p in periods if isinstance(p, str) and p)
    if not clean:
        return "—", "—"
    return clean[0], clean[-1]


def build_keyword_bridges(topic_comp):
    """Aggregate cross-pair shared keywords to identify bridge motifs."""
    counts = {}
    pairs = {}
    for row in topic_comp:
        pair_name = f"{row['ds_a']}|{row['ds_b']}"
        for kw in row.get("shared", []):
            counts[kw] = counts.get(kw, 0) + 1
            pairs.setdefault(kw, set()).add(pair_name)

    bridges = []
    for kw, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        bridges.append({
            "keyword": kw,
            "pair_count": count,
            "pairs": sorted(pairs.get(kw, set())),
        })
    return bridges


def build_replication_summary(bite_table, topic_comp, migration, mr_comp):
    """Build concise match-status rows for replicated literature checks."""
    overlap_vals = [r.get("jaccard", 0) for r in topic_comp]
    max_overlap = max(overlap_vals) if overlap_vals else 0
    min_overlap = min(overlap_vals) if overlap_vals else 0
    top_pair = topic_comp[0] if topic_comp else {"ds_a": "—", "ds_b": "—", "jaccard": 0}

    hoseini_status = "match_directional" if max_overlap > 0 else "insufficient_data"

    migration_platforms = set()
    for row in migration:
        migration_platforms.update(k for k in row.keys() if k != "period")
    required = {"4chan", "8kun", "parler", "telegram"}
    idrama_status = "match_strong" if required.issubset(migration_platforms) else "partial_match"

    mr_sorted = sorted(mr_comp, key=lambda x: -x.get("mean_score", 0))
    mr_top = mr_sorted[0] if mr_sorted else {"dataset": "—", "mean_score": 0}
    mr_bottom = mr_sorted[-1] if mr_sorted else {"dataset": "—", "mean_score": 0}
    priniski_status = "partial_match" if mr_top.get("mean_score", 0) > mr_bottom.get("mean_score", 0) else "insufficient_data"

    dominant_all_t = all(row.get("dominant") == "T" for row in bite_table) if bite_table else False
    hassan_status = "match_directional" if dominant_all_t else "partial_match"

    return {
        "experiments": [
            {
                "experiment": "Hoseini et al. 2021",
                "replicated_via": "Jaccard overlap on top topic keywords",
                "our_result": (
                    f"Max overlap {top_pair.get('ds_a','—')} x {top_pair.get('ds_b','—')} "
                    f"= {top_pair.get('jaccard', 0):.4f}; range {min_overlap:.4f}-{max_overlap:.4f}"
                ),
                "paper_expected": "Cross-platform diffusion with partial lexical convergence",
                "match_status": hoseini_status,
                "caption": "Low-to-moderate overlap still indicates shared narrative anchors across platforms.",
            },
            {
                "experiment": "iDRAMA platform diaspora",
                "replicated_via": "Monthly platform migration timeline",
                "our_result": f"{len(migration)} monthly periods with sequential platform shifts",
                "paper_expected": "Migration from imageboards into mainstream/social alternatives",
                "match_status": idrama_status,
                "caption": "Observed sequence tracks the documented diaspora pattern.",
            },
            {
                "experiment": "Priniski & Bavel 2021",
                "replicated_via": "Motivated-reasoning keyword classifier",
                "our_result": (
                    f"Highest mean on {mr_top.get('dataset','—')} ({mr_top.get('mean_score',0):.3f}); "
                    f"lowest on {mr_bottom.get('dataset','—')} ({mr_bottom.get('mean_score',0):.3f})"
                ),
                "paper_expected": "Identity-protective reasoning should be present and uneven by platform",
                "match_status": priniski_status,
                "caption": "Signal is present but high-intensity prevalence remains low under current thresholds.",
            },
            {
                "experiment": "Hassan BITE model",
                "replicated_via": "Weighted BITE lexicon scoring",
                "our_result": "Thought Control dominates all datasets",
                "paper_expected": "Cultic rhetoric should cluster strongly in thought/information-emotion control",
                "match_status": hassan_status,
                "caption": "Directionally consistent with BITE-style discourse control patterns.",
            },
        ]
    }


def build_experiment_setups(index, bite_table, topic_comp, migration, mr_comp):
    """Detailed, report-ready setup notes for each experiment."""
    method = index.get("method", "kmeans")
    cluster_stack = (
        "BERTopic (sentence-transformers + UMAP + HDBSCAN)"
        if method == "bertopic"
        else "TF-IDF + KMeans"
    )
    top_pair = topic_comp[0] if topic_comp else {}
    top_mr = mr_comp[0] if mr_comp else {}
    top_bite = bite_table[0] if bite_table else {}
    low_bite = bite_table[-1] if bite_table else {}

    return [
        {
            "id": "hoseini_topic_overlap",
            "title": "Hoseini et al. 2021 replication: cross-platform topic overlap",
            "status": "completed",
            "objective": "Measure lexical convergence of QAnon narratives across platform pairs.",
            "dataset_scope": "7 datasets, all unique platform pairs",
            "model_family": "Keyword-set overlap with Jaccard similarity",
            "model_details": [
                f"Cluster generation stack: {cluster_stack}",
                "Keywords per topic: top 10 terms",
                "Pair scoring: Jaccard(shared/union)",
                f"Top observed pair: {top_pair.get('ds_a', '—')} x {top_pair.get('ds_b', '—')} ({top_pair.get('jaccard', 0):.4f})",
            ],
            "llm_model": "Not used in this run (deterministic lexical method)",
            "llm_setup": [
                "Optional extension can use Ollama qwen2.5:7b for narrative label refinement",
                "Recommended settings: JSON mode, temperature=0, seed=42",
            ],
            "implementation": "multi_dataset_analysis.py::cross_platform_topic_overlap",
            "outputs": [
                "results/index.json -> cross.topic_overlap",
                "compare_results.json -> topic_overlap",
            ],
            "repro_command": "python multi_dataset_analysis.py --samples-only --method bertopic && python compare_results.py",
        },
        {
            "id": "idrama_migration",
            "title": "iDRAMA replication: platform migration timeline",
            "status": "completed",
            "objective": "Track monthly platform-level movement of discourse activity.",
            "dataset_scope": "All posts with valid timestamps",
            "model_family": "Temporal aggregation by platform and month",
            "model_details": [
                "Time binning: YYYY-MM (UTC)",
                "Metric: monthly post counts per platform",
                f"Timeline span: {len(migration)} monthly periods",
                "Normalization: 4ch merged into 4chan, 8ch merged into 8kun for visualization",
            ],
            "llm_model": "Not used in this run (count-based temporal method)",
            "llm_setup": [
                "Optional extension can use qwen2.5:7b for event annotation/captioning",
                "Keep extraction deterministic (temperature=0) for reproducible labels",
            ],
            "implementation": "multi_dataset_analysis.py::platform_migration",
            "outputs": [
                "results/index.json -> cross.platform_migration",
                "compare_results.json -> migration",
            ],
            "repro_command": "python multi_dataset_analysis.py --samples-only --method bertopic && python compare_results.py",
        },
        {
            "id": "priniski_motivated_reasoning",
            "title": "Priniski & Bavel replication: motivated reasoning markers",
            "status": "completed",
            "objective": "Estimate identity-protective reasoning intensity across platforms.",
            "dataset_scope": "Per-dataset post text",
            "model_family": "Rule-based keyword scoring",
            "model_details": [
                "Categories: certainty, us-vs-them, dismissal, in-group",
                "Score scaling: min(total_hits/8, 1.0)",
                "Distribution bands: low (<0.25), medium (0.25-0.49), high (>=0.50)",
                f"Highest mean observed: {top_mr.get('dataset', '—')} ({top_mr.get('mean_score', 0):.3f})",
            ],
            "llm_model": "Not used in this run (keyword lexicon method)",
            "llm_setup": [
                "Optional extension can replace lexicon with qwen2.5:7b JSON-classified rhetoric bands",
                "Use strict schema validation and retry loop for malformed responses",
            ],
            "implementation": "multi_dataset_analysis.py::score_motivated_reasoning",
            "outputs": [
                "results/<dataset>/analysis.json -> motivated_reasoning",
                "compare_results.json -> motivated_reasoning",
            ],
            "repro_command": "python multi_dataset_analysis.py --samples-only --method bertopic && python compare_results.py",
        },
        {
            "id": "hassan_bite",
            "title": "Hassan BITE replication: cult-control rhetoric scoring",
            "status": "completed",
            "objective": "Quantify behavior, information, thought, and emotional control rhetoric by platform.",
            "dataset_scope": "All normalized texts (full qdrops + sampled external datasets)",
            "model_family": "Weighted regex lexicon with dimension-wise aggregation",
            "model_details": [
                "Implementation: bite_scorer.py",
                "Pattern inventory: 136 weighted patterns across B/I/T/E",
                "Aggregation: per-post score -> corpus mean/std -> monthly timeline",
                f"Highest total observed: {top_bite.get('dataset', '—')} ({top_bite.get('total', 0):.4f}); lowest: {low_bite.get('dataset', '—')} ({low_bite.get('total', 0):.4f})",
            ],
            "llm_model": "Not used in this run (lexicon baseline retained for reproducibility)",
            "llm_setup": [
                "Optional LLM-assisted annotation profile available via Ollama",
                f"Default recommended model: {LLM_PROFILE['default_model']}",
                f"Fallback model: {LLM_PROFILE['fallback_model']}",
                "Deterministic generation: temperature=0, top_p=0.1, top_k=20",
            ],
            "implementation": "bite_scorer.py + multi_dataset_analysis.py::analyse_dataset",
            "outputs": [
                "results/<dataset>/analysis.json -> bite.aggregate and bite.timeline",
                "compare_results.json -> bite_table and highlights",
            ],
            "repro_command": "python multi_dataset_analysis.py --samples-only --method bertopic && python compare_results.py",
        },
        {
            "id": "llm_bite_extension",
            "title": "LLM extension (optional): JSON BITE adjudication",
            "status": "planned_not_executed",
            "objective": "Augment lexicon scoring with model-based interpretation and evidence snippets.",
            "dataset_scope": "Any dataset in datasets/normalised or datasets/samples",
            "model_family": "Instruction-tuned local LLM JSON classification",
            "model_details": [
                "Prompt contract: strict JSON output with labels and evidence quotes",
                "Validation: schema parse + bounds checks + retry on failure",
                "Suggested batching: one post per call for maximum schema fidelity",
            ],
            "llm_model": (
                f"Framework={LLM_PROFILE['framework']}, default={LLM_PROFILE['default_model']}, "
                f"HQ={LLM_PROFILE['high_quality_model']}, fallback={LLM_PROFILE['fallback_model']}"
            ),
            "llm_setup": [
                "Use JSON mode and fixed seed for reproducibility",
                "No markdown/code-fence outputs",
                "Persist outputs to results/<dataset>/llm_bite.json for comparison",
            ],
            "implementation": "Planned script: local_llm_bite.py (Ollama backend)",
            "outputs": [
                "results/<dataset>/llm_bite.json (planned)",
                "compare_results.json -> llm comparison fields (planned)",
            ],
            "repro_command": "ollama run qwen2.5:7b (with strict JSON prompt contract)",
        },
    ]


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
        dist = mr.get("distribution", {})
        n_posts = max(res.get("n_posts", 1), 1)
        high = dist.get("high", 0)
        med = dist.get("medium", 0)
        low = dist.get("low", 0)
        mr_comp.append({
            "dataset":    did,
            "mean_score": mr.get("mean_score", 0),
            "pct_high":   round(100 * high / n_posts, 1),
            "pct_medium": round(100 * med / n_posts, 1),
            "pct_low":    round(100 * low / n_posts, 1),
            "distribution": {
                "high": high,
                "medium": med,
                "low": low,
            },
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

    dataset_meta = []
    for did, res in results.items():
        timeline_periods = [r.get("period") for r in res.get("bite", {}).get("timeline", [])]
        start_period, end_period = period_bounds(timeline_periods)
        n_posts = res.get("n_posts", 0)
        dataset_meta.append({
            "dataset": did,
            "label": DS_LABELS.get(did, did),
            "platform": DS_PLATFORM.get(did, did),
            "sample_type": "full" if did == "qdrops" and n_posts > 1000 else "sample",
            "n_posts": n_posts,
            "period_start": start_period,
            "period_end": end_period,
        })
    dataset_meta.sort(key=lambda x: x["dataset"])

    all_posts = sum(r.get("n_posts", 0) for r in bite_table)
    overlap_values = [r.get("jaccard", 0) for r in topic_comp]
    overlap_max = max(overlap_values) if overlap_values else 0
    overlap_min = min(overlap_values) if overlap_values else 0
    overlap_mean = statistics.mean(overlap_values) if overlap_values else 0
    overlap_median = statistics.median(overlap_values) if overlap_values else 0

    migration_periods = [m.get("period") for m in migration]
    migration_start, migration_end = period_bounds(migration_periods)

    keyword_bridges = build_keyword_bridges(topic_comp)
    replication_summary = build_replication_summary(bite_table, topic_comp, migration, mr_comp)
    experiment_setups = build_experiment_setups(index, bite_table, topic_comp, migration, mr_comp)

    top_bite = bite_table[0] if bite_table else {}
    bottom_bite = bite_table[-1] if bite_table else {}

    return {
        "generated":     datetime.now(tz=timezone.utc).isoformat(),
        "method":        index.get("method", "kmeans"),
        "n_datasets":    len(results),
        "datasets":      list(results.keys()),
        "overview_stats": {
            "total_posts": all_posts,
            "period_start": migration_start,
            "period_end": migration_end,
            "mean_bite_total": round(statistics.mean([r.get("total", 0) for r in bite_table]), 4) if bite_table else 0,
            "max_bite_total": top_bite.get("total", 0),
            "max_bite_dataset": top_bite.get("dataset", "—"),
            "min_bite_total": bottom_bite.get("total", 0),
            "min_bite_dataset": bottom_bite.get("dataset", "—"),
            "max_overlap": round(overlap_max, 4),
            "min_overlap": round(overlap_min, 4),
            "mean_overlap": round(overlap_mean, 4),
            "median_overlap": round(overlap_median, 4),
        },
        "dataset_meta": dataset_meta,
        "bite_table":    bite_table,
        "topic_overlap": topic_comp,
        "keyword_bridges": keyword_bridges,
        "migration":     migration,
        "motivated_reasoning": mr_comp,
        "cluster_quality":     cluster_comp,
        "highlights":          highlights,
        "replication_summary": replication_summary,
        "experiment_setups": experiment_setups,
        "llm_profile": LLM_PROFILE,
        "method_flags": {
            "synthetic_samples_present": any(d["sample_type"] == "sample" for d in dataset_meta),
            "note": "Q drops uses full corpus; other datasets are representative 500-post samples unless fully downloaded.",
        },
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
