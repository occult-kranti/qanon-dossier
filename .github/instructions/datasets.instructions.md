---
applyTo: "datasets/**"
---

# Dataset Handling — QAnon Research Platform

## Normalised schema (required fields for every post)

```json
{
  "id":        "string — unique within dataset",
  "dataset":   "catalog ID (qdrops|reddit_qanon|4chan_pol|8kun_qresearch|parler|telegram|twitter)",
  "platform":  "4chan|reddit|parler|telegram|twitter|8kun",
  "board":     "/pol|r/greatawakening|/qresearch/|etc.",
  "timestamp": "UNIX epoch UTC (integer)",
  "text":      "plain text, HTML stripped",
  "author":    "string (may be anonymised)",
  "has_image": "boolean",
  "has_link":  "boolean"
}
```

## catalog.json required fields per entry

```json
{
  "id": "snake_case string",
  "name": "human-readable name",
  "platform": "comma-separated platforms",
  "boards": ["array of boards"],
  "period": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
  "post_count": 0,
  "format": "json|json-lines|csv",
  "license": "research-only|academic|public",
  "access": "auto|manual|api-ratelimited",
  "local_path": "path or null",
  "sample_path": "datasets/samples/<id>_sample.json",
  "url": "canonical download URL"
}
```

## Naming rules
- Normalised files: `datasets/normalised/<id>.json`
- Sample files: `datasets/samples/<id>_sample.json`
- Raw/input files: `datasets/<id>.json` or as specified in `local_path`

## Quality rules
- `text` must be non-empty after stripping (warn but do not drop zero-length posts)
- `timestamp` must be a positive integer (warn if zero; use 0 as fallback, do not drop)
- `id` must be unique within the file
- Do not store PII beyond what is in the original public post
