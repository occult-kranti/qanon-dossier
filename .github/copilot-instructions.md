# QAnon Research Platform — Copilot Instructions

This workspace is a **multi-dataset NLP research platform** for studying QAnon as a political movement and digital cult. It is academic/journalistic — claims are never amplified, only analysed.

## Project Map

| Path | Purpose |
|---|---|
| `posts.json` | Q drops corpus (4,966 posts, 2017–2020) |
| `datasets/catalog.json` | Registry of 7 datasets |
| `datasets/normalised/` | Common-schema JSON per dataset |
| `datasets/samples/` | 500-post test samples per dataset |
| `results/<dataset>/analysis.json` | Per-dataset clustering + BITE results |
| `results/index.json` | Cross-dataset index |
| `compare_results.json` | Comparison report data |
| `compare_results.html` | Self-contained comparison dashboard |
| `collect_datasets.py` | Dataset downloader / organiser |
| `bite_scorer.py` | BITE model NLP scorer |
| `multi_dataset_analysis.py` | Clustering + BITE + replication pipeline |
| `compare_results.py` | Cross-dataset comparison report generator |
| `qdrops_cluster.py` | Original Q-drops clustering pipeline |
| `qdrops_sweep.py` | Multi-config stability sweep |

## Team & Delegation

This project uses a 10-role team. **Always delegate to the right agent.**

| Task | Agent to invoke |
|---|---|
| Add / validate a dataset | `@data-engineer` |
| Run any Python script | `@executor` |
| Design or modify a model | `@ml-engineer` |
| Analyse results, make charts | `@analyst` |
| Update GitHub Actions / deploy | `@devops` |
| Write / update docs or reports | `@writer` |
| Validate outputs, run tests | `@qa` |
| Research a paper / new method | `@researcher` |
| Build / update HTML dashboard | `@web-developer` |
| Overall plan / priority | `@coordinator` |

When in doubt about ownership, ask `@coordinator`.

## Common-Schema Normalised Post

```json
{
  "id": "qdrops_001",
  "dataset": "qdrops",
  "platform": "4chan",
  "board": "/pol",
  "timestamp": 1509223468,
  "text": "...",
  "author": "Anonymous",
  "has_image": false,
  "has_link": false
}
```

## BITE Model Dimensions

| Key | Full Name | Measures |
|---|---|---|
| B | Behavior Control | compliance orders, surveillance rhetoric |
| I | Information Control | enemy-media framing, gatekeeping |
| T | Thought Control | loaded language, thought-stopping slogans |
| E | Emotional Control | fear, love-bombing, shame, urgency |

Score 0.0–1.0; `total` = mean of B+I+T+E.

## Code Conventions

- All Python scripts are CLI-runnable: `python <script>.py --help`
- Results always written to `results/<dataset_id>/analysis.json`
- Normalised datasets live in `datasets/normalised/<id>.json`
- Samples live in `datasets/samples/<id>_sample.json`
- Never hardcode file paths; use the constants at the top of each script
- Ethical note: do **not** generate new conspiracy content; only analyse existing text
