#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
improved_experiment.py — Run an improved, paper-style experiment with ablations.

This script orchestrates the full pipeline and adds:
  1) Cross-dataset analysis + comparison report regeneration.
  2) A model/parameter ablation sweep on Q drops.
  3) Optional preprocessing ablation (drop-admin enabled).
  4) Publication-ready plots (PNG) and structured reports (JSON/MD/HTML).
  5) A single transfer bundle zip with all required artifacts.

Design goals:
  - Reproducible CLI workflow.
  - Metrics aligned with standard clustering papers: silhouette, c_v coherence,
    topic persistence/stability (no confidence-centric reporting).
  - Explicit experiment codebook format for downstream writing.

USAGE
-----
    python improved_experiment.py
    python improved_experiment.py --method bertopic --samples-only
    python improved_experiment.py --models BAAI/bge-large-en-v1.5,all-mpnet-base-v2
"""

import argparse
import glob
import html
import json
import os
import subprocess
import sys
import zipfile
from collections import Counter
from datetime import datetime, timezone


CATALOG_PATH = "datasets/catalog.json"
NORM_DIR = "datasets/normalised"
SAMPLES_DIR = "datasets/samples"
RESULTS_DIR = "results"

IMPROVED_DIR = f"{RESULTS_DIR}/improved"
PLOTS_DIR = f"{IMPROVED_DIR}/plots"
RUNS_DIR = f"{IMPROVED_DIR}/runs"

COMPARE_JSON = "compare_results.json"
COMPARE_HTML = "compare_results.html"
STABILITY_JSON = "stability_report.json"
STABILITY_CSV = "stability_report.csv"

IMPROVED_REPORT_JSON = f"{IMPROVED_DIR}/improved_experiment_report.json"
IMPROVED_REPORT_MD = f"{IMPROVED_DIR}/improved_experiment_report.md"
IMPROVED_REPORT_HTML = f"{IMPROVED_DIR}/improved_experiment_report.html"
IMPROVED_CODEBOOK_JSON = f"{IMPROVED_DIR}/improved_experiment_codebook.json"

DEFAULT_METHOD = "bertopic"
DEFAULT_MODELS = "BAAI/bge-large-en-v1.5,all-mpnet-base-v2,all-MiniLM-L6-v2"
DEFAULT_MCS = "15,25,40"
DEFAULT_BUNDLE = "qanon_results_bundle_improved.zip"
DEFAULT_BATCH_SIZE = 16


def parse_csv(raw):
    return [x.strip() for x in str(raw).split(",") if x.strip()]


def get_plt():
    """Lazy matplotlib import so --help works before dependencies are installed."""
    try:
        import matplotlib.pyplot as plt  # pylint: disable=import-outside-toplevel
    except ImportError as exc:
        raise RuntimeError(
            "matplotlib is required for plotting. Install dependencies with: pip install -r requirements.txt"
        ) from exc
    return plt


def ensure_dirs():
    os.makedirs(IMPROVED_DIR, exist_ok=True)
    os.makedirs(PLOTS_DIR, exist_ok=True)
    os.makedirs(RUNS_DIR, exist_ok=True)


def run_cmd(cmd, step, env=None, allow_fail=False):
    print(f"\n[step] {step}")
    print("       " + " ".join(cmd))
    rc = subprocess.run(cmd, env=env, check=False).returncode
    if rc != 0 and not allow_fail:
        raise RuntimeError(f"Step failed ({step}) with exit code {rc}")
    return rc


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def save_markdown(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def save_html(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def normalize_platform(p):
    if p == "4ch":
        return "4chan"
    if p == "8ch":
        return "8kun"
    return p


def score_run(run):
    """
    Composite ablation score.
    Prioritizes stability and separation, with optional coherence support.
    """
    persistence = float(run.get("mean_persistence") or 0.0)
    silhouette = float(run.get("silhouette") or 0.0)
    coherence = float(run.get("coherence") or 0.0)
    return round(0.50 * persistence + 0.30 * max(silhouette, 0.0) + 0.20 * max(coherence, 0.0), 4)


def collect_ablation_runs(report_path, ablation_label):
    if not os.path.exists(report_path):
        return []
    rep = load_json(report_path)
    out = []
    for r in rep.get("runs", []):
        row = {
            "ablation": ablation_label,
            "tag": r.get("tag", "—"),
            "model": r.get("model", "—"),
            "mcs": r.get("mcs"),
            "n_topics": r.get("n_topics"),
            "silhouette": r.get("silhouette"),
            "coherence": r.get("coherence"),
            "mean_persistence": r.get("mean_persistence"),
            "file": r.get("file", ""),
        }
        row["score"] = score_run(row)
        out.append(row)
    return out


def plot_bite_totals(comp, out_path):
    plt = get_plt()
    rows = comp.get("bite_table", [])
    labels = [r.get("dataset", "") for r in rows]
    vals = [r.get("total", 0.0) for r in rows]

    plt.figure(figsize=(10, 4.8))
    plt.bar(labels, vals, color="#6E2A28")
    plt.title("BITE Total Mean by Dataset")
    plt.ylabel("Mean total BITE score")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_overlap_pairs(comp, out_path, top_n=12):
    plt = get_plt()
    rows = comp.get("topic_overlap", [])[:top_n]
    labels = [f"{r.get('ds_a','')}|{r.get('ds_b','')}" for r in rows]
    vals = [r.get("jaccard", 0.0) for r in rows]

    plt.figure(figsize=(11, 5.2))
    plt.barh(labels[::-1], vals[::-1], color="#2E5575")
    plt.title(f"Top {top_n} Topic-Overlap Pairs (Jaccard)")
    plt.xlabel("Jaccard")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_migration_totals(comp, out_path):
    plt = get_plt()
    totals = Counter()
    for row in comp.get("migration", []):
        for k, v in row.items():
            if k == "period" or not isinstance(v, int):
                continue
            totals[normalize_platform(k)] += v

    labels = [k for k, _ in totals.most_common()]
    vals = [v for _, v in totals.most_common()]

    plt.figure(figsize=(9, 4.8))
    plt.bar(labels, vals, color="#245C4D")
    plt.title("Total Posts by Platform (Migration Aggregate)")
    plt.ylabel("Posts")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_ablation_scoreboard(ablation_rows, out_path):
    if not ablation_rows:
        return
    plt = get_plt()
    rows = sorted(ablation_rows, key=lambda r: -r["score"])[:15]
    labels = [f"{r['ablation']}:{r['tag']}" for r in rows]
    vals = [r["score"] for r in rows]

    plt.figure(figsize=(12, 5.8))
    plt.barh(labels[::-1], vals[::-1], color="#8C3A33")
    plt.title("Ablation Scoreboard (stability + silhouette + coherence)")
    plt.xlabel("Composite score")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def build_codebook(args, compare_obj, ablation_rows, best_row, analysis_method, sweep_method):
    generated = datetime.now(tz=timezone.utc).isoformat()
    top_bite = (compare_obj.get("bite_table") or [{}])[0]
    top_pair = (compare_obj.get("topic_overlap") or [{}])[0]
    n_periods = len(compare_obj.get("migration", []))

    return {
        "generated": generated,
        "title": "Improved Multi-Dataset QAnon Experiment",
        "device_target": args.device,
        "analysis_method": analysis_method,
        "sweep_method": sweep_method,
        "primary_embedding_model": args.models.split(",")[0].strip(),
        "ablation_models": parse_csv(args.models),
        "ablation_mcs": parse_csv(args.mcs),
        "no_confidence_reporting": True,
        "experiments": [
            {
                "id": "improved_cross_dataset_analysis",
                "title": "Improved cross-dataset analysis",
                "status": "completed",
                "objective": "Regenerate unified cross-platform analysis with standardized outputs.",
                "dataset_scope": "All available datasets (full qdrops + sampled external datasets)",
                "model_family": analysis_method,
                "model_details": [
                    f"Method: {analysis_method}",
                    "Outputs: results/<dataset>/analysis.json, results/index.json",
                    f"Top BITE total observed on {top_bite.get('dataset', '—')} = {top_bite.get('total', 0):.4f}",
                ],
                "llm_model": "Not required for baseline scoring pipeline",
                "llm_setup": [
                    "LLM used only for optional extensions",
                    "No confidence metrics requested or reported",
                ],
                "implementation": "multi_dataset_analysis.py + compare_results.py",
                "outputs": [
                    "compare_results.json",
                    "compare_results.html",
                ],
                "repro_command": "python multi_dataset_analysis.py --samples-only --method bertopic && python compare_results.py",
            },
            {
                "id": "model_parameter_ablation",
                "title": "Embedding + min_cluster_size ablation",
                "status": "completed",
                "objective": "Select robust topic solution under model/parameter variation.",
                "dataset_scope": "Q drops corpus",
                "model_family": sweep_method,
                "model_details": [
                    f"Models: {', '.join(parse_csv(args.models))}",
                    f"min_cluster_size grid: {', '.join(parse_csv(args.mcs))}",
                    "Metrics: silhouette, c_v coherence, mean persistence",
                    f"Best run: {best_row.get('tag', '—')} (score={best_row.get('score', 0):.4f})",
                ],
                "llm_model": "Not used (deterministic clustering ablation)",
                "llm_setup": [
                    "No confidence metric included",
                    "Ranking based on stability and quality metrics only",
                ],
                "implementation": "qdrops_sweep.py",
                "outputs": [
                    "stability_report.json",
                    "stability_report.csv",
                    "run_*.json",
                ],
                "repro_command": (
                    f"python qdrops_sweep.py --method {sweep_method} --models {args.models} "
                    f"--mcs {args.mcs}"
                ),
            },
            {
                "id": "preprocessing_ablation",
                "title": "Administrative-content exclusion ablation",
                "status": "completed" if args.admin_ablation else "skipped",
                "objective": "Measure sensitivity to operational/admin drop filtering.",
                "dataset_scope": "Q drops corpus",
                "model_family": sweep_method,
                "model_details": [
                    "Toggle: --drop-admin on/off",
                    f"Admin ablation models: {parse_csv(args.models)[0] if parse_csv(args.models) else '—'}",
                    f"Periods in migration timeline: {n_periods}",
                ],
                "llm_model": "Not used",
                "llm_setup": [
                    "No confidence fields requested",
                    "Comparisons reported with identical scoring pipeline",
                ],
                "implementation": "qdrops_sweep.py --drop-admin",
                "outputs": [
                    "results/improved/admin_stability_report.json",
                    "results/improved/runs/admin/*",
                ],
                "repro_command": (
                    f"python qdrops_sweep.py --method {sweep_method} --models {parse_csv(args.models)[0]} "
                    f"--mcs {args.mcs} --drop-admin --report {IMPROVED_DIR}/admin_stability_report.json"
                ),
            },
            {
                "id": "replication_summary",
                "title": "Replication summary refresh",
                "status": "completed",
                "objective": "Refresh reported replication checks for Hoseini/iDRAMA/Priniski/Hassan.",
                "dataset_scope": "Cross-dataset report",
                "model_family": "Report synthesis",
                "model_details": [
                    f"Top overlap pair: {top_pair.get('ds_a', '—')}|{top_pair.get('ds_b', '—')} ({top_pair.get('jaccard', 0):.4f})",
                    "Schema includes detailed experiment setup fields",
                ],
                "llm_model": "Optional local LLM profile available in compare_results.json",
                "llm_setup": [
                    "Deterministic JSON settings recommended for extensions",
                    "Confidence not required for reporting",
                ],
                "implementation": "compare_results.py",
                "outputs": [
                    "compare_results.json -> replication_summary + experiment_setups",
                    "compare_results.html",
                ],
                "repro_command": "python compare_results.py",
            },
        ],
        "ablation_rows": ablation_rows,
        "best_ablation_run": best_row,
    }


def build_markdown_report(codebook, compare_obj, ablation_rows, bundle_path):
    best = codebook.get("best_ablation_run", {})
    overview = compare_obj.get("overview_stats", {})
    top_bite = (compare_obj.get("bite_table") or [{}])[0]
    low_bite = (compare_obj.get("bite_table") or [{}])[-1]
    top_pair = (compare_obj.get("topic_overlap") or [{}])[0]

    lines = []
    lines.append("# Improved Experiment Report")
    lines.append("")
    lines.append(f"Generated: {codebook.get('generated', '—')}")
    lines.append(f"Device target: {codebook.get('device_target', 't4')}")
    lines.append(f"Primary model: {codebook.get('primary_embedding_model', '—')}")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Total posts: {overview.get('total_posts', 0)}")
    lines.append(f"- Time span: {overview.get('period_start', '—')} to {overview.get('period_end', '—')}")
    lines.append(f"- Highest BITE total: {top_bite.get('dataset', '—')} ({top_bite.get('total', 0):.4f})")
    lines.append(f"- Lowest BITE total: {low_bite.get('dataset', '—')} ({low_bite.get('total', 0):.4f})")
    lines.append(
        f"- Top overlap pair: {top_pair.get('ds_a', '—')}|{top_pair.get('ds_b', '—')} ({top_pair.get('jaccard', 0):.4f})"
    )
    lines.append("")
    lines.append("## Ablation Leader")
    lines.append(f"- Best run: {best.get('tag', '—')}")
    lines.append(f"- Ablation: {best.get('ablation', '—')}")
    lines.append(f"- Composite score: {best.get('score', 0):.4f}")
    lines.append(f"- Silhouette: {best.get('silhouette')}")
    lines.append(f"- Coherence (c_v): {best.get('coherence')}")
    lines.append(f"- Mean persistence: {best.get('mean_persistence')}")
    lines.append("")
    lines.append("## Ablation Table")
    lines.append("| run | ablation | model | mcs | topics | silhouette | coherence_cv | persistence | score |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|")
    for r in sorted(ablation_rows, key=lambda x: -x.get("score", 0.0)):
        lines.append(
            f"| {r.get('tag','—')} | {r.get('ablation','—')} | {r.get('model','—')} "
            f"| {r.get('mcs','—')} | {r.get('n_topics','—')} "
            f"| {r.get('silhouette','—')} | {r.get('coherence','—')} "
            f"| {r.get('mean_persistence','—')} | {r.get('score',0):.4f} |"
        )
    lines.append("")
    lines.append("## Artifacts")
    lines.append("- Plots: results/improved/plots/")
    lines.append("- Codebook: results/improved/improved_experiment_codebook.json")
    lines.append(f"- Transfer bundle: {bundle_path}")
    lines.append("")
    return "\n".join(lines)


def build_html_report(codebook, compare_obj, ablation_rows):
    rows_html = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(r.get('tag', '—')))}</td>"
        f"<td>{html.escape(str(r.get('ablation', '—')))}</td>"
        f"<td>{html.escape(str(r.get('model', '—')))}</td>"
        f"<td>{html.escape(str(r.get('mcs', '—')))}</td>"
        f"<td>{html.escape(str(r.get('n_topics', '—')))}</td>"
        f"<td>{html.escape(str(r.get('silhouette', '—')))}</td>"
        f"<td>{html.escape(str(r.get('coherence', '—')))}</td>"
        f"<td>{html.escape(str(r.get('mean_persistence', '—')))}</td>"
        f"<td>{r.get('score', 0):.4f}</td>"
        "</tr>"
        for r in sorted(ablation_rows, key=lambda x: -x.get("score", 0.0))
    )

    best = codebook.get("best_ablation_run", {})
    overview = compare_obj.get("overview_stats", {})

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Improved Experiment Report</title>
<style>
body{{font-family:system-ui,sans-serif;margin:24px;background:#f8f9fa;color:#222}}
h1,h2{{color:#1f3b4d}}
.card{{background:#fff;border:1px solid #dfe4ea;border-radius:8px;padding:14px 16px;margin:10px 0}}
table{{border-collapse:collapse;width:100%;background:#fff}}
th,td{{border:1px solid #dfe4ea;padding:8px 10px;font-size:13px;text-align:left}}
th{{background:#f0f4f7}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px}}
img{{max-width:100%;border:1px solid #dfe4ea;border-radius:6px;background:#fff}}
</style>
</head>
<body>
<h1>Improved Experiment Report</h1>
<div class="card">Generated: {html.escape(codebook.get('generated', '—'))} · Device target: {html.escape(codebook.get('device_target', 't4'))}</div>

<h2>Overview</h2>
<div class="grid">
  <div class="card"><b>Total posts</b><br>{overview.get('total_posts', 0)}</div>
  <div class="card"><b>Time span</b><br>{overview.get('period_start', '—')} to {overview.get('period_end', '—')}</div>
  <div class="card"><b>Best ablation run</b><br>{html.escape(str(best.get('tag', '—')))} (score {best.get('score', 0):.4f})</div>
</div>

<h2>Ablation Table</h2>
<table>
<thead>
<tr><th>Run</th><th>Ablation</th><th>Model</th><th>mcs</th><th>Topics</th><th>Silhouette</th><th>Coherence</th><th>Persistence</th><th>Score</th></tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>

<h2>Plots</h2>
<div class="grid">
  <div class="card"><img src="plots/bite_totals.png" alt="BITE totals"></div>
  <div class="card"><img src="plots/top_overlap_pairs.png" alt="Top overlap pairs"></div>
  <div class="card"><img src="plots/migration_platform_totals.png" alt="Platform totals"></div>
  <div class="card"><img src="plots/ablation_scoreboard.png" alt="Ablation scoreboard"></div>
</div>

</body>
</html>
"""


def add_to_zip(zf, path, added):
    if not os.path.exists(path):
        return
    if os.path.isfile(path):
        if path not in added:
            zf.write(path, arcname=path)
            added.add(path)
        return
    for root, _, files in os.walk(path):
        for name in files:
            fp = os.path.join(root, name)
            if fp not in added:
                zf.write(fp, arcname=fp)
                added.add(fp)


def create_bundle(bundle_path):
    include_paths = [
        RESULTS_DIR,
        COMPARE_JSON,
        COMPARE_HTML,
        "qdrops_clustered.json",
        "qdrops_topics_summary.csv",
        STABILITY_JSON,
        STABILITY_CSV,
        NORM_DIR,
        SAMPLES_DIR,
        IMPROVED_REPORT_JSON,
        IMPROVED_REPORT_MD,
        IMPROVED_REPORT_HTML,
        IMPROVED_CODEBOOK_JSON,
    ]
    include_paths.extend(glob.glob("run_*.json"))
    include_paths.extend(glob.glob("run_*_topics_summary.csv"))

    os.makedirs(os.path.dirname(bundle_path) or ".", exist_ok=True)
    added = set()
    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in include_paths:
            add_to_zip(zf, p, added)


def run_pipeline(args):
    ensure_dirs()
    env = os.environ.copy()
    env.setdefault("QDROPS_BATCH_SIZE", str(args.batch_size))

    # 1) Data collection / normalization
    if not args.skip_collect:
        collect_cmd = [sys.executable, "collect_datasets.py"]
        if args.samples_only:
            collect_cmd.append("--samples-only")
        run_cmd(collect_cmd, "Collect datasets", env=env)

    # 2) Cross-dataset analysis (fallback to kmeans if bertopic fails)
    analysis_method = args.method
    ana_cmd = [sys.executable, "multi_dataset_analysis.py", "--method", analysis_method]
    if args.samples_only:
        ana_cmd.append("--samples-only")

    ana_rc = run_cmd(ana_cmd, "Run multi-dataset analysis", env=env, allow_fail=(analysis_method == "bertopic"))
    if ana_rc != 0 and analysis_method == "bertopic":
        analysis_method = "kmeans"
        ana_cmd = [sys.executable, "multi_dataset_analysis.py", "--method", "kmeans"]
        if args.samples_only:
            ana_cmd.append("--samples-only")
        run_cmd(ana_cmd, "Fallback analysis (kmeans)", env=env)

    # 3) Cross-dataset comparison report
    run_cmd([sys.executable, "compare_results.py"], "Build compare report", env=env)

    # 4) Q-drops single run (legacy outputs retained)
    qdrop_method = analysis_method if analysis_method in {"bertopic", "kmeans"} else "kmeans"
    qc_cmd = [sys.executable, "qdrops_cluster.py", "--method", qdrop_method, "--no-coherence"]
    run_cmd(qc_cmd, "Run qdrops single clustering", env=env)

    # 5) Main ablation sweep (models x min_cluster_size)
    sweep_method = args.method
    sweep_cmd = [
        sys.executable,
        "qdrops_sweep.py",
        "--method", sweep_method,
        "--models", args.models,
        "--mcs", args.mcs,
        "--out-prefix", "run",
        "--report", STABILITY_JSON,
    ]
    if args.no_coherence:
        sweep_cmd.append("--no-coherence")

    sweep_rc = run_cmd(sweep_cmd, "Run main ablation sweep", env=env, allow_fail=(sweep_method == "bertopic"))
    if sweep_rc != 0 and sweep_method == "bertopic":
        sweep_method = "kmeans"
        sweep_cmd = [
            sys.executable,
            "qdrops_sweep.py",
            "--method", "kmeans",
            "--models", args.models,
            "--mcs", args.mcs,
            "--out-prefix", "run",
            "--report", STABILITY_JSON,
            "--no-coherence",
        ]
        run_cmd(sweep_cmd, "Fallback ablation sweep (kmeans)", env=env)

    # 6) Optional preprocessing ablation (drop-admin)
    admin_report = f"{IMPROVED_DIR}/admin_stability_report.json"
    if args.admin_ablation:
        first_model = parse_csv(args.models)[0] if parse_csv(args.models) else "all-MiniLM-L6-v2"
        os.makedirs(f"{RUNS_DIR}/admin", exist_ok=True)
        admin_cmd = [
            sys.executable,
            "qdrops_sweep.py",
            "--method", sweep_method,
            "--models", first_model,
            "--mcs", args.mcs,
            "--drop-admin",
            "--out-prefix", f"{RUNS_DIR}/admin/run",
            "--report", admin_report,
        ]
        if args.no_coherence:
            admin_cmd.append("--no-coherence")
        run_cmd(admin_cmd, "Run admin-filter ablation", env=env)

    # 7) Build improved summaries + plots
    comp = load_json(COMPARE_JSON)
    main_rows = collect_ablation_runs(STABILITY_JSON, "main")
    admin_rows = collect_ablation_runs(admin_report, "drop_admin") if args.admin_ablation else []
    ablation_rows = main_rows + admin_rows
    best_row = max(ablation_rows, key=lambda r: r["score"]) if ablation_rows else {}

    plot_bite_totals(comp, f"{PLOTS_DIR}/bite_totals.png")
    plot_overlap_pairs(comp, f"{PLOTS_DIR}/top_overlap_pairs.png")
    plot_migration_totals(comp, f"{PLOTS_DIR}/migration_platform_totals.png")
    plot_ablation_scoreboard(ablation_rows, f"{PLOTS_DIR}/ablation_scoreboard.png")

    codebook = build_codebook(args, comp, ablation_rows, best_row, analysis_method, sweep_method)
    write_json(codebook, IMPROVED_CODEBOOK_JSON)

    bundle_path = args.bundle
    report_md = build_markdown_report(codebook, comp, ablation_rows, bundle_path)
    save_markdown(IMPROVED_REPORT_MD, report_md)

    report_html = build_html_report(codebook, comp, ablation_rows)
    save_html(IMPROVED_REPORT_HTML, report_html)

    report_json = {
        "generated": datetime.now(tz=timezone.utc).isoformat(),
        "device_target": args.device,
        "analysis_method": analysis_method,
        "sweep_method": sweep_method,
        "best_ablation_run": best_row,
        "n_ablation_runs": len(ablation_rows),
        "plots": {
            "bite_totals": f"{PLOTS_DIR}/bite_totals.png",
            "overlap_pairs": f"{PLOTS_DIR}/top_overlap_pairs.png",
            "migration_totals": f"{PLOTS_DIR}/migration_platform_totals.png",
            "ablation_scoreboard": f"{PLOTS_DIR}/ablation_scoreboard.png",
        },
        "codebook": IMPROVED_CODEBOOK_JSON,
    }
    write_json(report_json, IMPROVED_REPORT_JSON)

    # 8) Bundle
    create_bundle(bundle_path)
    print(f"\nDONE: {bundle_path}")


def main():
    ap = argparse.ArgumentParser(description="Run improved QAnon experiment with ablations and bundle outputs.")
    ap.add_argument("--device", choices=["t4", "v5e-1", "cpu"], default="t4",
                    help="Execution target metadata (recommended: t4)")
    ap.add_argument("--method", choices=["bertopic", "kmeans"], default=DEFAULT_METHOD,
                    help="Primary clustering method")
    ap.add_argument("--models", default=DEFAULT_MODELS,
                    help="Comma-separated sentence-transformers models for ablation")
    ap.add_argument("--mcs", default=DEFAULT_MCS,
                    help="Comma-separated min_cluster_size values (or k for kmeans)")
    ap.add_argument("--samples-only", action="store_true",
                    help="Use sample datasets for cross-dataset analysis")
    ap.add_argument("--skip-collect", action="store_true",
                    help="Skip collect_datasets.py step")
    ap.add_argument("--no-coherence", action="store_true",
                    help="Skip gensim coherence in sweeps")
    ap.add_argument("--admin-ablation", action="store_true",
                    help="Run preprocessing ablation with --drop-admin")
    ap.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE,
                    help="Embedding batch size (exported as QDROPS_BATCH_SIZE)")
    ap.add_argument("--bundle", default=DEFAULT_BUNDLE,
                    help="Output zip path")
    args = ap.parse_args()

    run_pipeline(args)


if __name__ == "__main__":
    main()
