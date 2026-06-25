---
name: "Score BITE"
description: "Run BITE model scoring on a specific dataset or a piece of text. Use to check BITE dimension scores, see which dimension dominates, or test the scorer on new text."
agent: executor
argument-hint: "Provide a dataset ID (e.g. 'qdrops') or paste a text string to score"
---

Run the BITE model scorer on the specified input.

## Option A — Score a dataset

```bash
python bite_scorer.py \
  --input datasets/normalised/${input:dataset_id:qdrops}.json \
  --output results/${input:dataset_id:qdrops}/bite_detailed.json \
  --window month
```

Then summarise the output:
```python
import json
r = json.load(open('results/${input:dataset_id:qdrops}/bite_detailed.json'))
agg = r['aggregate']
for dim in ['B','I','T','E','total']:
    d = agg.get(dim, {})
    print(f"{dim}: mean={d.get('mean',0):.3f}  std={d.get('std',0):.3f}  "
          f"pervasive={d.get('dist',{}).get('pervasive',0)} posts")
print("Dominant:", agg.get('corpus_dominant'))
print("Peak month:", max(r['timeline'], key=lambda x: x.get('T_mean',0))['period'])
```

## Option B — Score a specific text

```bash
python bite_scorer.py --text "${input:text:WWG1WGA trust the plan patriots}"
```

## Interpret the result

Report:
- Which dimension scored highest and why (which keywords triggered it)
- Whether the total score indicates weak / moderate / strong / pervasive control rhetoric
- For timeline data: when did BITE peak and what was happening in QAnon at that time?

## Reference: Score Interpretation

| Range | Label |
|---|---|
| 0.00–0.15 | Not detected |
| 0.15–0.35 | Weakly present |
| 0.35–0.55 | Moderately present |
| 0.55–0.75 | Strongly present |
| 0.75–1.00 | Pervasive |
