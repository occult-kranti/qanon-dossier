---
name: "Deploy Dashboard"
description: "Deploy the latest results to GitHub Pages. Use after running the analysis pipeline to publish compare_results.html and all result files."
agent: devops
argument-hint: "Optional: specify a commit message"
---

Deploy the latest analysis results to GitHub Pages.

## Pre-deployment checklist (run as @qa first)

```bash
# Verify all output files exist
ls compare_results.json compare_results.html results/index.json
ls results/*/analysis.json | wc -l   # should be 7
```

## Step 1 — Regenerate all outputs

```bash
python multi_dataset_analysis.py --samples-only
python compare_results.py
```

## Step 2 — Check the HTML renders correctly

```bash
python3 -m http.server 8000 &
# Open http://localhost:8000/compare_results.html
# Verify: tables populated, no console errors
kill %1
```

## Step 3 — Commit and push

```bash
git add compare_results.json compare_results.html results/ datasets/
git add datasets/catalog.json datasets/CATALOG.md datasets/samples/
git status
git commit -m "${input:message:chore: update analysis results and comparison report}"
git push origin main
```

## Step 4 — Confirm GitHub Pages

After push:
1. Go to https://github.com/occult-kranti/qanon-dossier/actions
2. Wait for Pages deployment action to complete (typically 1–3 min)
3. Visit https://occult-kranti.github.io/qanon-dossier/compare_results.html

## Files that MUST be at root for GitHub Pages

- `compare_results.html` ✅
- `compare_results.json` ✅  
- `drops.html` ✅
- `qdrops_clustered.json` ✅ (if running full clustering)
- `stability_report.json` ✅
- `run_*.json` ✅ (sweep results)
- `.nojekyll` ✅

## What NOT to commit

- `datasets/normalised/*.json` (large files — add to `.gitignore` if needed)
- `__pycache__/`
- `*.log`
