# Dataset Catalog

All datasets used in the multi-dataset analysis pipeline. Columns: **ID** · **Name** · **Platform** · **Size** · **Period** · **License** · **Access**.

---

## DS01 — Q Drops (JSON-QAnon)

| Field | Value |
|---|---|
| **ID** | `qdrops` |
| **Source** | Jack Kingsman's JSON-QAnon corpus |
| **URL** | https://github.com/jkingsman/JSON-QAnon |
| **DOI** | 10.13140/RG.2.2.28778.32964 |
| **Platform** | 4chan /pol/, 8chan /pol/, 8chan /qresearch/, 8kun /qresearch/ |
| **Period** | Oct 2017 – Dec 2020 |
| **Posts** | ~4,966 |
| **Format** | JSON (`posts.json`) |
| **License** | Research only — no commercial redistribution |
| **Access** | **Auto-downloaded** by `collect_datasets.py` |
| **Schema** | `post_metadata{id,time,author,board,site}`, `text`, `referenced_posts[]` |
| **Notes** | Primary dataset; already used in `qdrops_cluster.py` and `qdrops_sweep.py` |

---

## DS02 — Reddit QAnon Subreddits

| Field | Value |
|---|---|
| **ID** | `reddit_qanon` |
| **Source** | Pushshift Reddit archive |
| **URL** | https://academictorrents.com/details/9c263fc85366c1ef8f5bb9da0203f4c8c8db75f4 |
| **Platform** | Reddit |
| **Subreddits** | r/greatawakening (banned Jun 2018), r/CBTS_Stream (banned Feb 2018), r/The_Great_Awakening, r/qanon, r/WWG1WGA |
| **Period** | 2017 – 2018 (pre-ban) + 2018–2021 (surviving subs) |
| **Posts** | ~1.5M comments + 100K submissions |
| **Format** | JSON-lines (`.zst` compressed) |
| **License** | Academic / research |
| **Access** | **Manual** — download from Pushshift Academic Torrents or use the curated sample in `datasets/reddit_qanon_sample.json` |
| **Tool** | `pip install zstandard` then `python collect_datasets.py --dataset reddit` |
| **Schema** | `{id, subreddit, author, created_utc, body/selftext, score, url}` |
| **Notes** | r/greatawakening had ~70K subscribers at peak; banned under Reddit's hate-speech policy |

---

## DS03 — 4chan /pol/ Q-Thread Sample

| Field | Value |
|---|---|
| **ID** | `4chan_pol` |
| **Source** | 4plebs archive (public API) |
| **URL** | https://4plebs.org/pol/ |
| **API** | https://archive.4plebs.org/_/api/chan/search/?boards=pol&text=Q+drop |
| **Platform** | 4chan /pol/ |
| **Period** | Oct 2017 – Jan 2018 (early Q drops era) |
| **Posts** | ~50K threads (estimated); collector samples ~5K |
| **Format** | JSON (4plebs API response) |
| **License** | Public domain posts — API rate-limited |
| **Access** | **Auto-collected** by `collect_datasets.py --dataset 4chan` (rate-limited sample) |
| **Schema** | `{num, thread_num, op, timestamp, comment, capcode, trip, poster_country}` |
| **Notes** | Q first appeared on 4chan /pol/ before moving to 8chan. Trip-code authenticity signals are preserved. |

---

## DS04 — 8chan / 8kun /qresearch/ Archive

| Field | Value |
|---|---|
| **ID** | `8kun_qresearch` |
| **Source** | Archive.org crawl of 8kun.top/qresearch/ |
| **URL** | https://archive.org/details/8kun-qresearch |
| **Platform** | 8chan /qresearch/, 8kun /qresearch/ |
| **Period** | Nov 2018 – Dec 2020 |
| **Posts** | ~3M+ posts across threads |
| **Format** | JSON (board-exported posts) |
| **License** | Public domain; research use |
| **Access** | **Manual** — large dataset (~50 GB); use `collect_datasets.py --dataset 8kun --sample` for a 10K post sample |
| **Schema** | `{no, time, name, trip, id, capcode, country, com, sub, tim, ext, w, h}` |
| **Notes** | This is the main Q research board; contains the "anon" community responding to drops |

---

## DS05 — Parler QAnon Posts

| Field | Value |
|---|---|
| **ID** | `parler` |
| **Source** | ProPublica / George Washington University curated subset |
| **URL** | https://www.propublica.org/datastore/dataset/parler-data |
| **Alt URL** | https://ddosecrets.com/wiki/Parler (DDoSecrets — requires verification) |
| **Platform** | Parler |
| **Period** | Aug 2018 – Jan 2021 |
| **Posts** | ~400K QAnon-tagged posts (filtered) |
| **Format** | JSON-lines |
| **License** | Research / journalism |
| **Access** | **Manual** — apply at ProPublica datastore or download curated subset |
| **Schema** | `{PostId, UserId, Body, CreatedAt, HashtagsAll, Impressions, Comments, Upvotes, Reposts}` |
| **Notes** | Parler was the platform of choice after Twitter/Facebook bans; heavy QAnon activity |

---

## DS06 — Telegram Q Channels

| Field | Value |
|---|---|
| **ID** | `telegram` |
| **Source** | TG Stat / public academic exports |
| **URL** | https://tgstat.com/ |
| **Channels** | Q Movement, QAnon, WWG1WGA, GreatAwakening (various) |
| **Platform** | Telegram |
| **Period** | 2019 – 2023 |
| **Posts** | ~200K messages (estimated active channels) |
| **Format** | JSON (Telegram export format) |
| **License** | Public messages; research use |
| **Access** | **Manual** — use Telegram's "Export Chat History" on public channels |
| **Schema** | `{id, type, date, from, text, forwarded_from, photo, sticker, file}` |
| **Notes** | QAnon migrated heavily to Telegram after 2020 platform bans |

---

## DS07 — Twitter / X QAnon Hashtag Corpus

| Field | Value |
|---|---|
| **ID** | `twitter` |
| **Source** | Academic API / existing research exports |
| **URL** | https://developer.twitter.com/en/products/twitter-api/academic-research |
| **Hashtags** | #QAnon, #WWG1WGA, #TheGreatAwakening, #GreatAwakening, #TrustThePlan |
| **Platform** | Twitter / X |
| **Period** | 2018 – 2021 (peak activity) |
| **Posts** | ~10M+ tweets (full corpus); samples available |
| **Format** | JSON (Twitter API v2) |
| **License** | Academic research; redistribution of tweet IDs only |
| **Access** | **Manual** — Academic API access required; or rehydrate from tweet-ID datasets |
| **Alt** | Zenodo: https://doi.org/10.5281/zenodo.4586545 (Sharma et al. 2021, tweet IDs) |
| **Schema** | `{id, text, author_id, created_at, public_metrics, entities}` |
| **Notes** | QAnon suspended in 2020; hydrated IDs from Zenodo are the easiest route |

---

## Access Summary

| ID | Name | Auto-Download | Manual Steps | Sample Included |
|---|---|---|---|---|
| `qdrops` | Q Drops | ✅ Yes | — | ✅ posts.json |
| `reddit_qanon` | Reddit QAnon | ❌ No | PushShift torrent | ✅ 500 posts |
| `4chan_pol` | 4chan /pol/ | ✅ Rate-limited | — | ✅ ~1K posts |
| `8kun_qresearch` | 8kun /qresearch/ | ❌ No | Archive.org | ✅ 500 posts |
| `parler` | Parler | ❌ No | ProPublica apply | ✅ 500 posts |
| `telegram` | Telegram | ❌ No | Channel export | ✅ 500 posts |
| `twitter` | Twitter/X | ❌ No | Academic API / Zenodo | ✅ 500 posts |

All sample datasets (500 posts each) are included in `datasets/samples/` for testing the full pipeline without downloading the large corpora.

---

## Schema Normalisation

All datasets are normalised to a common schema by `collect_datasets.py`:

```json
{
  "id":        "unique string",
  "dataset":   "qdrops | reddit_qanon | 4chan_pol | ...",
  "platform":  "4chan | reddit | parler | telegram | twitter",
  "board":     "/pol | /qresearch | r/greatawakening | ...",
  "timestamp": 1509223468,
  "text":      "post text (HTML stripped)",
  "author":    "anonymous or handle",
  "has_image": false,
  "has_link":  false
}
```

---

## References

- Hoseini, M. et al. (2021). *How Globalization of the QAnon Conspiracy Theory Bypasses Twitter's Ban*. ICWSM.
- Aliapoulios, M. et al. (2021). *An Early Look at the Parler Online Social Network*. ICWSM / iDRAMA Lab.
- de Zeeuw, D. et al. (2020). *Tracing Normiefication: A multi-platform analysis of the QAnon conspiracy*. First Monday.
- Priniski, J.H. & Bavel, J.J.V. (2021). *Identity-based motivation and QAnon*. Perspectives on Psychological Science.
- Sharma, K. et al. (2021). *Characterizing the "#QAnon" Movement on Twitter*. arXiv:2104.04473. [Zenodo DOI 10.5281/zenodo.4586545]
- Kingsman, J. (2025). *JSON-QAnon*. DOI 10.13140/RG.2.2.28778.32964.

---

Last Updated: 2026-06-25
