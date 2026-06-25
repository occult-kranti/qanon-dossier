---
name: "Add Dataset"
description: "Add a new dataset to the catalog and analysis pipeline. Use when you have a new data source to integrate — Reddit dump, Parler export, Telegram archive, etc."
agent: data-engineer
argument-hint: "Describe the dataset: name, platform, file path or URL, and approximate post count"
---

Add a new dataset to the QAnon Research Platform. Gather information from the user and implement end-to-end.

## Information Needed

Ask for (or infer from context):
1. **Dataset name** — human-readable, e.g. "Voat QAnon Posts"
2. **Dataset ID** — short snake_case, e.g. `voat`
3. **Platform** — 4chan | reddit | parler | telegram | twitter | 8kun | voat | etc.
4. **Board/channel** — e.g. `/v/GreatAwakening`
5. **File path** — where the raw data file is (or URL to download it)
6. **Raw schema** — show me the first record so I can write the normaliser

## Steps to Implement

### 1. Inspect the raw data

```python
import json
data = json.load(open('${input:file_path:datasets/new_dataset.json}'))
sample = data[:1] if isinstance(data, list) else list(data.values())[:1]
print(json.dumps(sample, indent=2))
```

### 2. Add to `datasets/catalog.json`

Add an entry with all required fields. Use the existing entries as templates.

### 3. Write a normaliser in `collect_datasets.py`

Add a function `normalise_<id>(posts_raw)` that maps the raw schema to:
```json
{"id": "", "dataset": "", "platform": "", "board": "", "timestamp": 0,
 "text": "", "author": "", "has_image": false, "has_link": false}
```

Register it in the `NORMALISERS` dict.

### 4. Add a sample generator entry (for synthetic testing)

Add text samples to `SAMPLE_TEXTS[dataset_id]` and a base timestamp to `BASE_TIMES`.

### 5. Test

```bash
python collect_datasets.py --dataset ${input:dataset_id:new_id}
```

Verify: normalised file written, sample generated, no exceptions.

### 6. Run analysis

```bash
python multi_dataset_analysis.py --dataset ${input:dataset_id:new_id} --samples-only
python compare_results.py
```

### 7. Document in `datasets/CATALOG.md`

Add a `## DSN — Name` section with the standard table.
