---
applyTo: "**/*.py"
---

# Python Standards — QAnon Research Platform

## Script conventions
- Every script must be CLI-runnable: `python <script>.py --help`
- Use `argparse` for all arguments; always include `--help` text
- Constants go at the top of each file in ALL_CAPS (paths, URLs, seeds)
- Never hardcode `posts.json` or `results/` inside functions — use the constants

## Data safety
- Never `print()` raw post text in error messages (privacy + content policy)
- Strip HTML before storing: `re.sub(r'<[^>]+>', ' ', text)`
- Always handle `KeyError` and `TypeError` when reading post fields — schema varies by dataset

## Paths
```python
RESULTS_DIR = "results"
NORM_DIR    = "datasets/normalised"
SAMPLES_DIR = "datasets/samples"
CATALOG_PATH = "datasets/catalog.json"
```

## Output files
- Results: `results/<dataset_id>/analysis.json`
- Per-dataset BITE: `results/<dataset_id>/bite_detailed.json`
- Index: `results/index.json`
- Comparison: `compare_results.json` + `compare_results.html`

## Imports to reuse
```python
from bite_scorer import BITEScorer   # BITE model scoring
import qdrops_cluster as qc          # embed / cluster / validity helpers
```

## Ethical constraint
Do NOT generate, synthesise, or complete conspiracy content.
The analysis tools consume existing text only.
