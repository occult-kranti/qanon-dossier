#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
collect_datasets.py — Collect, normalise, and organise all QAnon research datasets.

This script:
  1. Reads datasets/catalog.json to discover all known datasets.
  2. Auto-downloads datasets with access == "auto".
  3. For datasets that need manual download, prints clear instructions.
  4. Generates representative samples (500 posts) for every dataset so the
     full pipeline can be tested without downloading the large corpora.
  5. Normalises every dataset to the common schema and writes
     datasets/normalised/<id>.json for use by multi_dataset_analysis.py.

Common schema (one object per post):
  {
    "id":        str,   # unique within dataset
    "dataset":   str,   # catalog ID
    "platform":  str,   # 4chan | reddit | parler | telegram | twitter | 8kun
    "board":     str,   # /pol | r/greatawakening | etc.
    "timestamp": int,   # UNIX epoch UTC
    "text":      str,   # HTML-stripped post body
    "author":    str,
    "has_image": bool,
    "has_link":  bool
  }

USAGE
-----
    python collect_datasets.py                   # all auto-download datasets + samples
    python collect_datasets.py --dataset qdrops  # just Q drops
    python collect_datasets.py --samples-only    # skip downloads, regenerate samples
    python collect_datasets.py --list            # list datasets and status
"""

import argparse
import html
import json
import os
import random
import re
import sys
import time
import urllib.request
from datetime import datetime

CATALOG_PATH = "datasets/catalog.json"
SAMPLES_DIR  = "datasets/samples"
NORM_DIR     = "datasets/normalised"
POSTS_PATH   = "posts.json"
SEED         = 42

random.seed(SEED)

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def strip_html(text):
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def has_link(text):
    return bool(re.search(r"https?://", text or ""))

def has_image(post_raw, dataset_id):
    """Heuristic image detection per dataset schema."""
    if dataset_id == "qdrops":
        return bool(post_raw.get("post_metadata", {}).get("images"))
    if dataset_id == "4chan_pol":
        return bool(post_raw.get("media"))
    if dataset_id in ("parler",):
        return bool(post_raw.get("Urls") and any("img" in u.lower() for u in (post_raw["Urls"] or [])))
    if dataset_id == "telegram":
        return post_raw.get("type") in ("photo", "sticker", "video")
    return False

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def write_json(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print(f"  wrote {path} ({len(obj)} records)" if isinstance(obj, list) else f"  wrote {path}")

def sample(lst, n=500):
    return random.sample(lst, min(n, len(lst)))


# ──────────────────────────────────────────────────────────────────────────────
# Dataset-specific normalisers
# ──────────────────────────────────────────────────────────────────────────────

def normalise_qdrops(posts_raw):
    """Normalise JSON-QAnon posts."""
    out = []
    for p in posts_raw:
        meta = p.get("post_metadata", {})
        src  = meta.get("source", {})
        text = strip_html(p.get("text", ""))
        out.append({
            "id":        str(meta.get("id", "")),
            "dataset":   "qdrops",
            "platform":  src.get("site", "4chan"),
            "board":     src.get("board", "/pol"),
            "timestamp": int(meta.get("time", 0)),
            "text":      text,
            "author":    meta.get("author", "Anonymous"),
            "has_image": bool(meta.get("images")),
            "has_link":  has_link(text),
        })
    return out


def normalise_reddit(posts_raw):
    """Normalise Reddit Pushshift records (submissions and comments)."""
    out = []
    for p in posts_raw:
        text = strip_html(p.get("body") or p.get("selftext") or "")
        out.append({
            "id":        str(p.get("id", "")),
            "dataset":   "reddit_qanon",
            "platform":  "reddit",
            "board":     "r/" + p.get("subreddit", ""),
            "timestamp": int(p.get("created_utc", 0)),
            "text":      text,
            "author":    p.get("author", "[deleted]"),
            "has_image": has_link(p.get("url", "")),
            "has_link":  has_link(text),
        })
    return out


def normalise_4chan(posts_raw):
    """Normalise 4plebs API records."""
    out = []
    for p in posts_raw:
        text = strip_html(p.get("comment", ""))
        out.append({
            "id":        str(p.get("num", p.get("no", ""))),
            "dataset":   "4chan_pol",
            "platform":  "4chan",
            "board":     "/pol/",
            "timestamp": int(p.get("timestamp", p.get("time", 0))),
            "text":      text,
            "author":    p.get("name", "Anonymous"),
            "has_image": bool(p.get("media")),
            "has_link":  has_link(text),
        })
    return out


def normalise_8kun(posts_raw):
    """Normalise 8kun board exports."""
    out = []
    for p in posts_raw:
        text = strip_html(p.get("com", ""))
        out.append({
            "id":        str(p.get("no", "")),
            "dataset":   "8kun_qresearch",
            "platform":  "8kun",
            "board":     "/qresearch/",
            "timestamp": int(p.get("time", 0)),
            "text":      text,
            "author":    p.get("name", "Anonymous"),
            "has_image": bool(p.get("tim")),
            "has_link":  has_link(text),
        })
    return out


def normalise_parler(posts_raw):
    """Normalise Parler JSON records."""
    out = []
    for p in posts_raw:
        text = strip_html(p.get("Body", ""))
        ts_raw = p.get("CreatedAt", "")
        try:
            ts = int(datetime.fromisoformat(ts_raw.rstrip("Z")).timestamp()) if ts_raw else 0
        except Exception:
            ts = 0
        out.append({
            "id":        str(p.get("PostId", "")),
            "dataset":   "parler",
            "platform":  "parler",
            "board":     "parler",
            "timestamp": ts,
            "text":      text,
            "author":    str(p.get("UserId", "")),
            "has_image": has_image(p, "parler"),
            "has_link":  has_link(text),
        })
    return out


def normalise_telegram(posts_raw):
    """Normalise Telegram JSON exports."""
    out = []
    for p in posts_raw:
        if isinstance(p.get("text"), list):
            text = " ".join(t if isinstance(t, str) else t.get("text","") for t in p["text"])
        else:
            text = str(p.get("text", ""))
        text = strip_html(text)
        ts_raw = p.get("date", "")
        try:
            ts = int(datetime.fromisoformat(ts_raw).timestamp()) if ts_raw else 0
        except Exception:
            ts = 0
        out.append({
            "id":        str(p.get("id", "")),
            "dataset":   "telegram",
            "platform":  "telegram",
            "board":     p.get("chat", "telegram"),
            "timestamp": ts,
            "text":      text,
            "author":    p.get("from", ""),
            "has_image": has_image(p, "telegram"),
            "has_link":  has_link(text),
        })
    return out


def normalise_twitter(posts_raw):
    """Normalise Twitter API v2 / Zenodo rehydrated records."""
    out = []
    for p in posts_raw:
        text = strip_html(p.get("text", ""))
        ts_raw = p.get("created_at", "")
        try:
            ts = int(datetime.fromisoformat(ts_raw.rstrip("Z")).timestamp()) if ts_raw else 0
        except Exception:
            ts = 0
        out.append({
            "id":        str(p.get("id", "")),
            "dataset":   "twitter",
            "platform":  "twitter",
            "board":     "twitter",
            "timestamp": ts,
            "text":      text,
            "author":    str(p.get("author_id", "")),
            "has_image": False,
            "has_link":  has_link(text),
        })
    return out


NORMALISERS = {
    "qdrops":         normalise_qdrops,
    "reddit_qanon":   normalise_reddit,
    "4chan_pol":       normalise_4chan,
    "8kun_qresearch": normalise_8kun,
    "parler":         normalise_parler,
    "telegram":       normalise_telegram,
    "twitter":        normalise_twitter,
}


# ──────────────────────────────────────────────────────────────────────────────
# Sample generators (synthetic but realistic data for testing)
# ──────────────────────────────────────────────────────────────────────────────

# Representative posts drawn from public academic summaries (not real post content)
SAMPLE_TEXTS = {
    "reddit_qanon": [
        "Trust the plan. The storm is coming and nothing can stop what is coming. WWG1WGA patriots!",
        "The deep state will be exposed. Q has given us the map. Future proves past.",
        "MSM is covering this up. Do your own research. They are terrified of us waking up.",
        "God bless Q and POTUS. We are fighting pure evil. Light will defeat darkness.",
        "Anons knew this months ago. The crumbs lead here. Archive everything offline.",
        "The Great Awakening is real. More people are waking up every day. Panic in DC!",
        "FISA abuse will bring them all down. Trust Wray, trust Huber. Trust the plan.",
        "Q drop 1234 says it all. This is not a game. Dark to light. We are the news now.",
        "Children are being rescued! This is what Q warned us about. The truth is coming out.",
        "Fake news media won't report this. They fear what happens when we all wake up.",
    ],
    "4chan_pol": [
        "Q confirmed on 8ch, trip verified. Something big is about to drop. Get ready anons.",
        "Notice how they never address Q directly? That's because they can't debunk the map.",
        "Operation mockingbird is real. CIA controls media. Wake up normies.",
        "HRC panic mode. SA arrests. This is real. Archive offline NOW.",
        "Shills are heavy tonight, must be over target. WWG1WGA no matter what.",
        "Look at the timing of this tweet vs the Q post. Not a coincidence.",
        "Patriots in control. Trust the military. God bless America.",
        "Cabal is panicking. Resignations are coming. Watch the news this week.",
        "Red pill incoming: the Federal Reserve is a private bank. Rothschilds control it all.",
        "Anons already knew. MSM will claim conspiracy. We are the future historians.",
    ],
    "8kun_qresearch": [
        "Q Research General #14576 - Trust the Plan Edition. New Q drop at top of bread.",
        "Baker here. Q post confirmed with matching trip. This is it anons. New Q!",
        "Decode: Q drop refers to Epstein island. RC connects everything. See the map.",
        "NotableS: Huber report imminent. Barr activated. Durham ticking. Trust the plan.",
        "Shill ID'd. Filter and move on. They want to divide us. WWG1WGA is our shield.",
        "Great Awakening: 10 days of darkness before the Storm. Q confirmed.",
        "Timestamp delta between POTUS tweet and Q post: 1 minute 17 seconds. Proof.",
        "Alice and Wonderland reference confirmed in latest Q drop. It's all connected.",
        "Night shift best shift. Godspeed anons. Dark to light. Nothing can stop what is coming.",
        "BOOM BOOM BOOM. Q said big week. Arrests incoming. Panic in DC confirmed.",
    ],
    "parler": [
        "MSM won't show you this but Q told us months ago. Great Awakening is real!!! #WWG1WGA",
        "God bless our patriots! Trump knows everything. Trust the plan! #QAnon #MAGA",
        "They banned us everywhere because they fear the truth. But we will not be silenced.",
        "FISA will bring down the whole corrupt cabal. Justice is coming for them all.",
        "Join our Telegram: [link]. Censored everywhere else. Truth cannot be stopped.",
        "Q drop today confirms everything. Storm incoming. Patriots are ready. #TrustThePlan",
        "The election was stolen and Q warned us this would happen. Hold the line patriots!",
        "Big pharma, deep state, MSM are all connected. Wake up sheeple.",
        "I was red-pilled 3 years ago. Everything Q said is coming true. Wake up America.",
        "We are not a conspiracy theory. We are an awakening movement. #GreatAwakening",
    ],
    "telegram": [
        "Q just posted! New drop! Get in here everyone!! The storm is upon us 🇺🇸",
        "Breaking: Mass arrests imminent according to Q. Mainstream media silent. Of course.",
        "🔴 ALERT: Major FISA revelations coming. Durham has it all. Tick tock traitors.",
        "God wins. Evil will be exposed. Trust the plan. Forward this to everyone you know.",
        "They're trying to silence us here too. Archive everything. WWG1WGA 🌎",
        "Q said: Nothing can stop what is coming. NOTHING. Patriots worldwide are ready.",
        "Censored on Twitter. Banned from Facebook. But we are still here. Truth always wins.",
        "Decode the latest Q drops here: [link]. The map is complete. Follow the white rabbit.",
        "The cabal fears an awake population. That's why they want you distracted and afraid.",
        "BOOM! Q's latest prediction just came true. How can anyone still doubt the plan?",
    ],
    "twitter": [
        "Q drop today connects everything. Follow the money. #QAnon #WWG1WGA #TrustThePlan",
        "Mainstream media won't show you this. Q has been right all along. #GreatAwakening",
        "The deep state is terrified. Patriots are in control. #QAnon #MAGA",
        "God bless Q and all patriots fighting for truth and freedom! #WWG1WGA 🇺🇸",
        "#QAnon has been predicting this for months. Wake up! The storm is coming.",
        "They banned Q everywhere because the truth is too dangerous for them. #Censorship",
        "FISA DECLAS coming! Huber is ready! Q told us this weeks ago! #QAnon",
        "Do your research. Q is real. The plan is working. #TrustThePlan #WWG1WGA",
        "How is this still not on the news?! Q warned us! #FakeNews #MSM #QAnon",
        "We are the news now. Citizen journalists for truth. #QAnon #GreatAwakening",
    ],
}

BASE_TIMES = {
    "reddit_qanon":   1510000000,
    "4chan_pol":       1509223468,
    "8kun_qresearch":  1543000000,
    "parler":         1580000000,
    "telegram":       1609000000,
    "twitter":        1530000000,
}


def make_sample(dataset_id, n=500):
    """Generate n synthetic-but-realistic sample posts for a dataset."""
    texts   = SAMPLE_TEXTS.get(dataset_id, SAMPLE_TEXTS["twitter"])
    base_ts = BASE_TIMES.get(dataset_id, 1530000000)
    posts   = []
    for i in range(n):
        text = texts[i % len(texts)]
        # small variations
        suffix = ["", " WWG1WGA", " Trust the plan.", " God bless.", " #QAnon"][i % 5]
        posts.append({
            "id":        f"{dataset_id}_{i:05d}",
            "dataset":   dataset_id,
            "platform":  dataset_id.split("_")[0],
            "board":     {"reddit_qanon": "r/greatawakening", "4chan_pol": "/pol/",
                          "8kun_qresearch": "/qresearch/", "parler": "parler",
                          "telegram": "QAnon", "twitter": "twitter"}.get(dataset_id, dataset_id),
            "timestamp": base_ts + i * 3600 * random.randint(1, 48),
            "text":      text + suffix,
            "author":    f"anon_{i:04d}",
            "has_image": random.random() < 0.15,
            "has_link":  random.random() < 0.25,
        })
    return posts


# ──────────────────────────────────────────────────────────────────────────────
# Download helpers
# ──────────────────────────────────────────────────────────────────────────────

def download_qdrops(local_path):
    url = "https://raw.githubusercontent.com/jkingsman/JSON-QAnon/main/posts.json"
    if os.path.exists(local_path):
        print(f"  [qdrops] found cached {local_path}"); return
    print(f"  [qdrops] downloading from {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "qanon-research/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(local_path, "wb") as f:
        f.write(r.read())
    print(f"  [qdrops] saved ({os.path.getsize(local_path)/1e6:.1f} MB)")


# ──────────────────────────────────────────────────────────────────────────────
# Main pipeline
# ──────────────────────────────────────────────────────────────────────────────

def process_dataset(ds, samples_only=False):
    did   = ds["id"]
    print(f"\n[{did}] {ds['name']}")

    norm_path   = f"{NORM_DIR}/{did}.json"
    sample_path = f"{SAMPLES_DIR}/{did}_sample.json"

    # ── 1. Obtain raw data ──────────────────────────────────────────────────
    raw_posts = None

    if did == "qdrops" and not samples_only:
        download_qdrops(POSTS_PATH)
        raw = load_json(POSTS_PATH)
        raw_posts = raw["posts"] if isinstance(raw, dict) else raw
        print(f"  loaded {len(raw_posts)} raw posts")

    elif ds.get("access") == "manual":
        local = ds.get("local_path")
        if local and os.path.exists(local):
            raw_posts = load_json(local)
            print(f"  loaded {len(raw_posts)} posts from {local}")
        else:
            print(f"  [MANUAL DOWNLOAD REQUIRED]")
            print(f"  URL : {ds.get('url')}")
            if ds.get("doi"): print(f"  DOI : {ds.get('doi')}")
            print(f"  Place the file at: {local or 'datasets/' + did + '.json'}")
            print(f"  → will use synthetic sample for now")

    # ── 2. Normalise if we have raw data ───────────────────────────────────
    if raw_posts and not samples_only:
        normaliser = NORMALISERS.get(did)
        if normaliser:
            normed = normaliser(raw_posts)
            write_json(normed, norm_path)
        else:
            print(f"  [warn] no normaliser for {did}")

    # ── 3. Generate / update sample ────────────────────────────────────────
    if os.path.exists(norm_path):
        # Sample from the actual normalised data
        normed = load_json(norm_path)
        s = sample(normed, 500)
        write_json(s, sample_path)
        print(f"  sample: {len(s)} posts → {sample_path}")
    else:
        # Generate synthetic sample
        s = make_sample(did, 500)
        write_json(s, sample_path)
        print(f"  synthetic sample: {len(s)} posts → {sample_path}")

    return os.path.exists(norm_path)


def print_status(catalog):
    print(f"\n{'ID':<20} {'Name':<35} {'Access':<15} {'Normalised':<12} {'Sample'}")
    print("-" * 100)
    for ds in catalog["datasets"]:
        did        = ds["id"]
        normed     = "✅" if os.path.exists(f"{NORM_DIR}/{did}.json")    else "—"
        sampled    = "✅" if os.path.exists(f"{SAMPLES_DIR}/{did}_sample.json") else "—"
        print(f"{did:<20} {ds['name']:<35} {ds['access']:<15} {normed:<12} {sampled}")


def main():
    ap = argparse.ArgumentParser(description="Collect and normalise QAnon research datasets")
    ap.add_argument("--dataset",      help="process only this dataset ID")
    ap.add_argument("--samples-only", action="store_true", help="skip downloads, only generate samples")
    ap.add_argument("--list",         action="store_true", help="list dataset status and exit")
    args = ap.parse_args()

    catalog = load_json(CATALOG_PATH)

    os.makedirs(SAMPLES_DIR, exist_ok=True)
    os.makedirs(NORM_DIR,    exist_ok=True)

    if args.list:
        print_status(catalog); return

    datasets = catalog["datasets"]
    if args.dataset:
        datasets = [d for d in datasets if d["id"] == args.dataset]
        if not datasets:
            print(f"Unknown dataset: {args.dataset}"); sys.exit(1)

    results = {}
    for ds in datasets:
        ok = process_dataset(ds, samples_only=args.samples_only)
        results[ds["id"]] = ok

    print("\n── Collection summary ──────────────────────────────────────────")
    for did, ok in results.items():
        status = "normalised + sampled" if ok else "sample only (manual download needed)"
        print(f"  {did:<20} {status}")

    print_status(catalog)
    print("\nDone. Run multi_dataset_analysis.py to cluster and score all datasets.")


if __name__ == "__main__":
    main()
