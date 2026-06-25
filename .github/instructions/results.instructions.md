---
applyTo: "results/**"
---

# Results Interpretation — QAnon Research Platform

## analysis.json structure

```json
{
  "dataset_id": "string",
  "n_posts": 0,
  "cluster": {
    "method": "kmeans|bertopic",
    "n_clusters": 10,
    "metrics": {"silhouette": 0.05},
    "topics": [{"id":0,"label":"word · word · word","keywords":[],"size":0,"share_pct":0}]
  },
  "bite": {
    "aggregate": {
      "B": {"mean":0,"std":0,"max":0,"dist":{"not_detected":0,"weak":0,"moderate":0,"strong":0,"pervasive":0}},
      "I": {}, "T": {}, "E": {}, "total": {},
      "corpus_dominant": "T",
      "n_posts": 0
    },
    "timeline": [{"period":"YYYY-MM","B_mean":0,"I_mean":0,"T_mean":0,"E_mean":0,"n":0}]
  },
  "motivated_reasoning": {"mean_score": 0, "distribution": {"high":0,"medium":0,"low":0}},
  "corpus": {"boards": {}, "by_year": {}}
}
```

## BITE score interpretation

| Range | Label | Meaning |
|---|---|---|
| 0.00–0.15 | Not detected | Dimension absent from this corpus |
| 0.15–0.35 | Weak | Occasional markers |
| 0.35–0.55 | Moderate | Regular presence; notable pattern |
| 0.55–0.75 | Strong | Dominant framing |
| 0.75–1.00 | Pervasive | Near-universal in corpus |

## Silhouette score interpretation (text clustering)

Dense-text silhouette is typically low (0.02–0.15 for good results):
- < 0.01: clusters not distinguishable
- 0.01–0.10: weak but real structure
- 0.10–0.25: moderate structure
- > 0.25: strong separation (unusual for free text)

Silhouette = 1.0 on synthetic samples is expected — all posts are nearly identical.

## Notes on synthetic samples

Results on `datasets/samples/*_sample.json` (500 synthetic posts) are for pipeline testing only. BITE scores from synthetic samples are inflated because the texts were constructed to contain BITE markers. Use `datasets/normalised/qdrops.json` (4,966 real posts) for research-quality results.
