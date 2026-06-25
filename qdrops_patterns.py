#!/usr/bin/env python3
"""qdrops_patterns.py — original pattern-mining over the raw Q-drop corpus.

Goes beyond the topic/BITE pipeline to extract *metadata* signatures the other
scripts discard: posting circadian rhythm, stylistic phase shifts across the
board migration, falsifiable-claim ("concreteness") decay, source-vs-platform
BITE amplification, and inter-drop cadence.

Reads  : posts.json (raw JSON-QAnon archive)  +  results/index.json (BITE summary)
Writes : results/improved/original_findings.json

These signatures back the two "theories" panels on index.html / results.html and
are fully reproducible:  python qdrops_patterns.py
"""
import json, re, datetime as dt, statistics as st
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UTC = dt.timezone.utc


def load_recs():
    posts = json.load(open(ROOT / "posts.json"))["posts"]
    recs = []
    for p in posts:
        m = p.get("post_metadata", {})
        t = m.get("time")
        if not t:
            continue
        d = dt.datetime.fromtimestamp(t, UTC)
        txt = p.get("text") or ""
        recs.append(dict(
            t=t, d=d, year=d.year, hour=d.hour, wd=d.weekday(),
            site=m.get("source", {}).get("site"),
            board=m.get("source", {}).get("board"),
            text=txt, words=len(txt.split()),
            q=txt.count("?"),
            urls=len(re.findall(r"https?://", txt)),
        ))
    recs.sort(key=lambda r: r["t"])
    return recs


def style(rs):
    n = len(rs)
    if not n:
        return None
    return dict(
        n=n,
        med_words=st.median(r["words"] for r in rs),
        pct_short=round(sum(1 for r in rs if r["words"] <= 5) / n * 100, 1),
        pct_question=round(sum(1 for r in rs if r["q"] > 0) / n * 100, 1),
        pct_url=round(sum(1 for r in rs if r["urls"] > 0) / n * 100, 1),
        q_per_drop=round(sum(r["q"] for r in rs) / n, 2),
    )


def main():
    recs = load_recs()
    tot = len(recs)
    hour = Counter(r["hour"] for r in recs)

    # --- circadian: timezone-robust sleep trough ---
    def trough_center(off):
        lc = Counter()
        for h in range(24):
            lc[(h + off) % 24] += hour.get(h, 0)
        return min(range(24), key=lambda c: sum(lc[(c + k) % 24] for k in range(-2, 3)))

    busy, quiet = max(hour.values()), min(hour.values())
    deep = sum(hour.get(h, 0) for h in (11, 12, 13))
    circadian = dict(
        utc_hist={str(h): hour.get(h, 0) for h in range(24)},
        busiest_hours_utc=sorted(sorted(range(24), key=lambda h: -hour.get(h, 0))[:6]),
        quietest_hours_utc=sorted(sorted(range(24), key=lambda h: hour.get(h, 0))[:6]),
        busy_quiet_ratio=round(busy / quiet, 1),
        deep_trough_utc="11-13",
        deep_trough_pct=round(deep / tot * 100, 2),
        trough_center_local={lbl: trough_center(off) for off, lbl in
                             [(-8, "PST"), (-7, "MST"), (-6, "CST"), (-5, "EST"), (-4, "EDT")]},
    )

    weekday = {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][i]:
               Counter(r["wd"] for r in recs).get(i, 0) for i in range(7)}

    by_year = defaultdict(list)
    for r in recs:
        by_year[r["year"]].append(r)
    style_by_year = {str(y): style(by_year[y]) for y in sorted(by_year)}

    phases = dict(
        early_2017_4ch_8ch=style([r for r in recs if r["d"] < dt.datetime(2018, 1, 1, tzinfo=UTC)]),
        mid_2018_2019_8ch=style([r for r in recs if dt.datetime(2018, 1, 1, tzinfo=UTC) <= r["d"] < dt.datetime(2019, 11, 1, tzinfo=UTC)]),
        late_8kun=style([r for r in recs if r["d"] >= dt.datetime(2019, 11, 1, tzinfo=UTC)]),
    )

    # --- concreteness / falsifiable-claim decay ---
    months = r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\b"
    datepat = re.compile(r"\b\d{1,2}/\d{1,2}\b|" + months, re.I)
    actionpat = re.compile(r"\b(will be|arrested|indict|extradition|tomorrow|next week|by \w+day)\b", re.I)
    concreteness = {}
    for y in sorted(by_year):
        rs = by_year[y]
        n = len(rs)
        concreteness[str(y)] = dict(
            date_or_month_pct=round(sum(1 for r in rs if datepat.search(r["text"])) / n * 100, 1),
            action_prediction_pct=round(sum(1 for r in rs if actionpat.search(r["text"])) / n * 100, 1),
        )

    # --- source vs platform BITE amplification ---
    bs = json.load(open(ROOT / "results/index.json"))["bite_summary"]
    src = bs["qdrops"]["total"]
    amplification = {k: dict(total=v["total"], T=v["T"], B=v["B"],
                             mult=round(v["total"] / src, 1)) for k, v in bs.items()}

    # --- cadence ---
    gaps = [(recs[i + 1]["t"] - recs[i]["t"]) / 3600 for i in range(len(recs) - 1)]
    cadence = dict(
        median_gap_h=round(st.median(gaps), 2),
        mean_gap_h=round(st.mean(gaps), 2),
        burst_share_lt5min=round(sum(1 for g in gaps if g < 1 / 12) / len(gaps) * 100, 1),
        silence_share_gt7d=round(sum(1 for g in gaps if g > 168) / len(gaps) * 100, 1),
    )

    site_by_year = {str(y): dict(Counter(r["site"] for r in by_year[y])) for y in sorted(by_year)}

    out = dict(
        generated=dt.datetime.now(UTC).isoformat(),
        n_drops=tot,
        source="posts.json (JSON-QAnon) + results/index.json",
        circadian=circadian, weekday=weekday,
        style_by_year=style_by_year, phases=phases,
        concreteness_by_year=concreteness, amplification=amplification,
        cadence=cadence, site_by_year=site_by_year,
    )
    dest = ROOT / "results/improved/original_findings.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(dest, "w"), indent=2)
    print("wrote", dest, "·", tot, "drops")
    return out


if __name__ == "__main__":
    main()
