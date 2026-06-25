---
name: "Replicate Paper"
description: "Replicate a published paper's methodology on our datasets. Use when: checking if our results match the literature, implementing a new analytical approach from a paper, or benchmarking against published findings."
agent: researcher
argument-hint: "Name the paper to replicate, e.g. 'Hoseini 2021' or 'Priniski & Bavel 2021'"
---

Replicate the methodology of the specified paper using our multi-dataset pipeline.

## Papers Already Implemented

| Paper | Status | Function |
|---|---|---|
| Hoseini et al. 2021 | ✅ Implemented | `cross_platform_topic_overlap()` |
| iDRAMA Lab 2021 | ✅ Implemented | `platform_migration()` |
| Priniski & Bavel 2021 | ✅ Implemented | `score_motivated_reasoning()` |
| de Zeeuw et al. 2020 | ⏳ Partial | Temporal framing shifts |
| Hassan 2018 (BITE) | ✅ Implemented | `BITEScorer` in `bite_scorer.py` |

## For a New Paper

### Step 1 — Research (as @researcher)
Summarise:
- Citation and DOI
- Research question
- Data used
- Method in 3 bullet points
- Key finding (with numbers if available)

### Step 2 — Design (as @ml-engineer)
Map the paper's method to our pipeline:
- Which of our 7 datasets best matches theirs?
- What new function needs to be added to `multi_dataset_analysis.py`?
- Write pseudocode

### Step 3 — Implement (as @ml-engineer)
Add the function and wire it into `main()`.

### Step 4 — Run (as @executor)
```bash
python multi_dataset_analysis.py --samples-only
python compare_results.py
```

### Step 5 — Compare (as @analyst)
```
Our result:   [number]
Paper result: [number]
Match:        [close / diverges]
Explanation:  [why if different]
```

### Step 6 — Document (as @writer)
Add a row to the "Replicating related work" table in `README.md`.

## Replication Template

```
## Replication: [Paper Citation]

**Research question**: ...
**Their dataset**: ...  **Our equivalent**: ...
**Their method**: ...   **Our implementation**: function `xxx()` in `multi_dataset_analysis.py`
**Their key finding**: ...
**Our result**: ...
**Assessment**: Consistent / Diverges because ...
```
