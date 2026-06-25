---
name: "Run Full Analysis"
description: "Run the complete pipeline: collect datasets, cluster + BITE score all datasets, generate comparison report. Use when starting a fresh analysis run or after adding new data."
agent: executor
argument-hint: "Optional: specify --method bertopic for better quality, or --dataset <id> for a single dataset"
---

Run the full QAnon multi-dataset analysis pipeline in order. Stop and report any failure before proceeding to the next step.

## Step 1 — Collect & organise datasets

```bash
python collect_datasets.py --samples-only
```

Expected: 7 datasets listed, all with ✅ Sample.

## Step 2 — Run clustering + BITE scoring on all datasets

```bash
python multi_dataset_analysis.py --samples-only ${input:flags:}
```

Expected: 7 `results/<id>/analysis.json` files written.

## Step 3 — Generate comparison report

```bash
python compare_results.py
```

Expected: `compare_results.json` and `compare_results.html` written.

## Step 4 — QA check

```bash
python bite_scorer.py --text "WWG1WGA trust the plan the great awakening patriots"
```

Expected: T score > 0.5

## Report back

After all steps complete, print:
- Which datasets were analysed
- BITE summary table (B/I/T/E/total per dataset)  
- Top topic overlap pair (highest Jaccard)
- Any failures or warnings
