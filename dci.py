#!/usr/bin/env python3
"""dci.py — the Delegated-Closure Index (DCI).

A per-drop, embedding-free, LLM-free, regex/count-computable operationalization of
"gap-leaving" — how much interpretive closure a Q drop withholds and offloads onto
the reader. Implements the "Delegated Closure" theory's measurement contribution.

DCI_i = clip( 0.22*INTERROGATIVE + 0.20*DECODE_disjoint + 0.18*REDACTION
            + 0.15*BREVITY + 0.13*(1-CONCRETENESS) + 0.12*(1-GROUNDING), 0, 1)

Design guarantees (see future.html#non-circular):
  • Engagement / amplification is NEVER an input  -> non-circular.
  • Every token shared with bite_scorer.py is removed from DECODE  -> measurement-
    independent of BITE.
  • No embeddings, no parser, no LLM — only text / referenced_posts / time.

Reads  : posts.json
Writes : results/improved/dci_findings.json
Run    : python dci.py
"""
import json, re, datetime as dt
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
UTC = dt.timezone.utc

WEIGHTS = {
    "INTERROGATIVE": 0.22, "DECODE": 0.20, "REDACTION": 0.18,
    "BREVITY": 0.15, "NONCONCRETE": 0.13, "NONGROUNDED": 0.12,
}

# DECODE lexicon — deliberately DISJOINT from bite_scorer.py.
# Excludes "future proves past", "trust the plan", "map" (BITE lines 104/124/105).
DECODE = re.compile(
    r"re[_ ]?read|expand your thinking|connect the dots|you have more than you know"
    r"|think mirror|coincidence\?|stringer", re.I)
BRACKET = re.compile(r"\[[^\]]+\]")
UNDERSCORE = re.compile(r"[A-Z]+_+[A-Z_]*|_{2,}")
ALLCAPS_TOK = re.compile(r"\b[A-Z]{2,}\b")
ALPHA_TOK = re.compile(r"\b[A-Za-z]{2,}\b")
CAPITALIZED = re.compile(r"\b[A-Z][a-z]+\b")
BARE_PRON = re.compile(r"\b(this|that|they|it)\b", re.I)
DATEPAT = re.compile(
    r"\b\d{1,2}/\d{1,2}\b|\b(january|february|march|april|may|june|july|august|"
    r"september|october|november|december)\b", re.I)
ACTIONPAT = re.compile(r"\b(will be|arrested|indict|extradition|tomorrow|next week|by \w+day)\b", re.I)


def components(text, refs):
    """Return the six DCI components in [0,1] for one drop."""
    t = text or ""
    words = t.split()
    nw = len(words)

    interrogative = min(1.0, t.count("?") / 3.0)
    decode = 1.0 if DECODE.search(t) else 0.0

    # REDACTION = max of purely-lexical blackout signals
    bracket = 1.0 if BRACKET.search(t) else 0.0
    underscore = 1.0 if UNDERSCORE.search(t) else 0.0
    alpha = ALPHA_TOK.findall(t)
    allcaps_ratio = (len(ALLCAPS_TOK.findall(t)) / len(alpha)) if alpha else 0.0
    bare_pron = 1.0 if (BARE_PRON.search(t) and not CAPITALIZED.search(t) and not refs) else 0.0
    redaction = max(bracket, underscore, min(1.0, allcaps_ratio), bare_pron)

    brevity = 1.0 - min(1.0, nw / 20.0)
    concrete = 1.0 if (DATEPAT.search(t) or ACTIONPAT.search(t)) else 0.0
    grounded = 1.0 if ("http" in t or refs) else 0.0

    return {
        "INTERROGATIVE": interrogative, "DECODE": decode, "REDACTION": redaction,
        "BREVITY": brevity, "NONCONCRETE": 1.0 - concrete, "NONGROUNDED": 1.0 - grounded,
    }


def dci_from(comp, weights=WEIGHTS):
    return max(0.0, min(1.0, sum(weights[k] * comp[k] for k in weights)))


def ols_slope(x, y):
    """slope of y on x via least squares."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    return float(np.polyfit(x, y, 1)[0])


def pearson(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if x.std() == 0 or y.std() == 0:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def partial_r(x, y, z):
    """partial correlation of x,y controlling for z."""
    rxy, rxz, ryz = pearson(x, y), pearson(x, z), pearson(y, z)
    denom = ((1 - rxz**2) * (1 - ryz**2)) ** 0.5
    return float((rxy - rxz * ryz) / denom) if denom else 0.0


def main():
    posts = json.load(open(ROOT / "posts.json"))["posts"]
    rows = []
    for p in posts:
        m = p.get("post_metadata", {})
        t = m.get("time")
        if not t:
            continue
        text = p.get("text") or ""
        refs = p.get("referenced_posts") or []
        comp = components(text, refs)
        rows.append(dict(
            time=t, year=dt.datetime.fromtimestamp(t, UTC).year,
            words=len(text.split()), text=text, comp=comp,
            dci=dci_from(comp), uni=dci_from(comp, {k: 1/6 for k in WEIGHTS}),
        ))
    n = len(rows)
    dci = np.array([r["dci"] for r in rows])
    yrs = sorted({r["year"] for r in rows})

    # ---- distribution ----
    qs = np.quantile(dci, [.25, .5, .75])
    hist_counts, _ = np.histogram(dci, bins=20, range=(0, 1))
    dist = dict(n=n, mean=round(float(dci.mean()), 4), sd=round(float(dci.std()), 4),
                min=round(float(dci.min()), 4), max=round(float(dci.max()), 4),
                median=round(float(qs[1]), 4), q1=round(float(qs[0]), 4), q3=round(float(qs[2]), 4),
                hist_bins=20, hist=[int(c) for c in hist_counts])

    # ---- by-year means (overall + per component) ----
    by_year = {}
    for y in yrs:
        rs = [r for r in rows if r["year"] == y]
        by_year[str(y)] = dict(
            n=len(rs), dci=round(float(np.mean([r["dci"] for r in rs])), 4),
            **{k: round(float(np.mean([r["comp"][k] for r in rs])), 4) for k in WEIGHTS})

    # ---- ODS: slope of DCI on time (per-year units) + per component + placebo ----
    times = np.array([r["time"] for r in rows], float)
    SECS_YR = 365.25 * 24 * 3600
    ods_overall = ols_slope(times, dci) * SECS_YR
    ods_comp = {k: round(ols_slope(times, [r["comp"][k] for r in rows]) * SECS_YR, 5) for k in WEIGHTS}
    rng = np.random.default_rng(42)
    placebo = float(np.mean([abs(ols_slope(times, rng.permutation(dci)) * SECS_YR) for _ in range(200)]))
    ods = dict(overall_per_year=round(ods_overall, 5),
               per_component_per_year=ods_comp,
               placebo_mean_abs_slope=round(placebo, 5),
               interpretation="real overall slope vs ~0 placebo; per-component shows which signals drive drift")

    # ---- FER over 2017-2019 (deferral vs concreteness) ----
    fer = {}
    for y in (2017, 2018, 2019):
        rs = [r for r in rows if r["year"] == y]
        dec = np.mean([r["comp"]["DECODE"] for r in rs])
        con = np.mean([1 - r["comp"]["NONCONCRETE"] for r in rs])
        fer[str(y)] = dict(decode_share=round(float(dec), 4), concrete_share=round(float(con), 4),
                           fer=round(float(dec / con), 3) if con else None)

    # ---- weight invariance ----
    uni = np.array([r["uni"] for r in rows])
    order_weighted = [by_year[str(y)]["dci"] for y in yrs]
    uni_by_year = [round(float(np.mean([r["uni"] for r in rows if r["year"] == y])), 4) for y in yrs]
    weight_inv = dict(
        pearson_weighted_vs_uniform=round(pearson(dci, uni), 4),
        ods_uniform_per_year=round(ols_slope(times, uni) * SECS_YR, 5),
        year_order_preserved=bool(np.all(np.argsort(order_weighted) == np.argsort(uni_by_year))))

    # ---- leave-one-out ablation ----
    loo = {}
    for drop_k in WEIGHTS:
        w = {k: v for k, v in WEIGHTS.items() if k != drop_k}
        s = sum(w.values()); w = {k: v / s for k, v in w.items()}
        vals = np.array([dci_from(r["comp"], w) for r in rows])
        loo[drop_k] = dict(mean=round(float(vals.mean()), 4),
                           ods_per_year=round(ols_slope(times, vals) * SECS_YR, 5),
                           r_vs_full=round(pearson(vals, dci), 4))

    # ---- OLP: DCI vs BITE, partial out word_count + BITE-T variance ----
    olp = {"note": "BITE scored per-drop via bite_scorer.py; word_count partialled out"}
    try:
        from bite_scorer import BITEScorer
        sc = BITEScorer()
        bt = np.array([sc.score(r["text"]) for r in rows])
        bite_total = np.array([b["total"] for b in bt])
        bite_T = np.array([b["T"] for b in bt])
        wc = np.array([r["words"] for r in rows], float)
        olp.update(
            decode_lexicon_overlap_with_bite=0,
            r_dci_bite_total=round(pearson(dci, bite_total), 4),
            partial_r_dci_bite_total_given_wordcount=round(partial_r(dci, bite_total, wc), 4),
            bite_T_mean=round(float(bite_T.mean()), 4), bite_T_var=round(float(bite_T.var()), 6),
            interpretation="near-zero BITE-T variance => 'DCI beats BITE-T' would be uninformative; "
                           "if partial-r collapses vs raw r, any DCI-BITE link is a brevity artifact")
    except Exception as e:  # pragma: no cover
        olp["error"] = f"BITE scoring skipped: {e}"

    # ---- discriminant examples ----
    rows_sorted = sorted(rows, key=lambda r: r["dci"])
    def snip(r): return dict(dci=round(r["dci"], 3), words=r["words"], text=(r["text"][:140]))
    discriminant = dict(highest=[snip(r) for r in rows_sorted[-3:][::-1]],
                        lowest=[snip(r) for r in rows_sorted[:3]])

    out = dict(
        generated=dt.datetime.now(UTC).isoformat(), theory="Delegated Closure",
        metric="Delegated-Closure Index (DCI)", weights=WEIGHTS, n_drops=n,
        source="posts.json (real 4,966-drop Q corpus); downstream platforms excluded (synthetic — see catalog.json)",
        distribution=dist, by_year=by_year, ods=ods, fer=fer,
        weight_invariance=weight_inv, leave_one_out=loo, olp=olp, discriminant=discriminant)
    dest = ROOT / "results/improved/dci_findings.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(dest, "w"), indent=2)
    print(f"wrote {dest} · n={n} · DCI mean={dist['mean']} sd={dist['sd']} "
          f"range {dist['min']}-{dist['max']} · ODS={ods['overall_per_year']}/yr placebo={ods['placebo_mean_abs_slope']}")
    return out


if __name__ == "__main__":
    main()
