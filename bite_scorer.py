#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bite_scorer.py — Steven Hassan's BITE Model as an NLP scorer.

The BITE model (Hassan, 2018) evaluates authoritarian/cult control across four
dimensions. Each dimension is scored per-document (0.0–1.0) using a weighted
keyword lexicon, returning a BITE profile for every post and aggregate statistics.

CONSTRUCT-VALIDITY LIMITATIONS (see audit.html — do not over-read these scores)
------------------------------------------------------------------------------
  * UNVALIDATED. The lexicon and per-pattern weights are hand-set; they have NOT
    been validated against human coding, and no inter-rater reliability (Cohen's
    kappa) has been computed. Treat outputs as EXPLORATORY, not measured facts.
  * NO STANCE/NEGATION HANDLING. Scoring is substring presence only. A sentence
    that *debunks* QAnon ("WWG1WGA is a deep-state slogan") scores high "Thought
    Control" purely from containing the terms. The scorer therefore measures
    TOPIC SALIENCE, not coercion — it cannot tell speaker from subject.
  * The saturation constant (3.0) is a tuning choice, not an estimated parameter.
These limits matter most for cross-corpus comparisons; they are why the
cross-platform "amplification" claim is flagged as unsupported.

Dimensions
----------
  B  Behavior Control      — compliance, surveillance, control of actions
  I  Information Control   — gatekeeping, enemy-media framing, insider knowledge
  T  Thought Control       — loaded language, thought-stopping, black/white thinking
  E  Emotional Control     — fear, love-bombing, shame, urgency

Score interpretation
--------------------
  0.0 – 0.15  Not detected
  0.15 – 0.35 Weakly present
  0.35 – 0.55 Moderately present
  0.55 – 0.75 Strongly present
  0.75 – 1.0  Pervasive

Reference
---------
  Hassan, S. (2018). Combating cult mind control (Updated ed.). Freedom of Mind Press.
  Bite model criteria: https://freedomofmind.com/cult-mind-control/bite-model/

USAGE
-----
    from bite_scorer import BITEScorer
    scorer = BITEScorer()
    result = scorer.score("Trust the plan. WWG1WGA. Fake news is the enemy of the people.")
    # result = {"B": 0.22, "I": 0.64, "T": 0.71, "E": 0.45, "total": 0.50, ...}

    python bite_scorer.py --input datasets/normalised/qdrops.json --output bite_qdrops.json
"""

import argparse
import json
import math
import os
import re
import sys
from collections import defaultdict

# ──────────────────────────────────────────────────────────────────────────────
# Keyword Lexicon
# Each entry: (pattern, weight)
# Patterns are case-insensitive sub-strings or simple regex.
# Higher weight = stronger signal for that dimension.
# ──────────────────────────────────────────────────────────────────────────────

LEXICON = {
    # ── B: Behavior Control ───────────────────────────────────────────────────
    # Compliance instructions, operational orders, surveillance, control of actions
    "B": [
        (r"\barchive\s+(everything|offline|now)\b", 0.9),
        (r"\bfollow\s+the\s+plan\b",                0.8),
        (r"\bstand\s+ready\b",                      0.7),
        (r"\boperators\s+are\s+(active|standing)\b", 0.8),
        (r"\breport\s+(shills?|infiltrators?|clowns?)\b", 0.8),
        (r"\bfollow\s+orders?\b",                   0.8),
        (r"\bobey\b",                               0.6),
        (r"\bdo\s+as\s+(you|you're)\s+told\b",      0.8),
        (r"\bpermission\b",                         0.4),
        (r"\bsurveillance\b",                       0.5),
        (r"\bmonitored?\b",                         0.4),
        (r"\bnot\s+a\s+game\b",                     0.6),
        (r"\bshill\s+hunt\b",                       0.7),
        (r"\bid\s+the\s+shills?\b",                 0.7),
        (r"\bdiscipline\b",                         0.4),
        (r"\bmust\s+(comply|follow|obey|report)\b",  0.7),
        (r"\bprotocol\b",                           0.4),
        (r"\bmarch\s+madness\b",                    0.5),
        (r"\blearn\s+comms\b",                      0.6),
        (r"\bprivate\s+comms\b",                    0.6),
        (r"\bboard\s+owner\b",                      0.4),
        (r"\bnew\s+trip\b",                         0.5),
        (r"\bfilter\s+and\s+move\b",                0.5),
    ],

    # ── I: Information Control ────────────────────────────────────────────────
    # Gatekeeping, enemy-media framing, insider knowledge, censorship framing
    "I": [
        (r"\bfake\s+news\b",                        0.9),
        (r"\bmsm\b",                                0.8),
        (r"\bmainstream\s+media\b",                 0.7),
        (r"\benemy\s+of\s+the\s+people\b",          1.0),
        (r"\bpropaganda\b",                         0.7),
        (r"\bdo\s+your\s+(own\s+)?research\b",      0.7),
        (r"\bred\s+pill(ed)?\b",                    0.8),
        (r"\bwake\s+up\b",                          0.6),
        (r"\bthey\s+don'?t\s+want\s+you\s+to\s+know\b", 1.0),
        (r"\bthey'?re\s+hiding\b",                  0.8),
        (r"\bcensored?\b",                          0.8),
        (r"\bshadow\s+bann?ed?\b",                  0.8),
        (r"\balgorithm(s)?\b",                      0.5),
        (r"\bcover\s+up\b",                         0.7),
        (r"\bwon'?t\s+(show|tell|report)\s+you\b",  0.8),
        (r"\bsilenced?\b",                          0.7),
        (r"\bcrumbs?\b",                            0.6),
        (r"\bfuture\s+proves\s+past\b",             0.8),
        (r"\bthe\s+map\b",                          0.5),
        (r"\bnews\s+unlocks\b",                     0.7),
        (r"\bcontrolled\s+(media|narrative|press)\b", 0.9),
        (r"\boperation\s+mockingbird\b",            0.9),
        (r"\bwe\s+are\s+the\s+news\b",              0.8),
        (r"\binside\s+information\b",               0.6),
        (r"\bclassified\b",                         0.5),
        (r"\bhidden\s+truth\b",                     0.7),
        (r"\bback\s+channels?\b",                   0.6),
        (r"\b4am\b",                                0.6),  # Q's claim that MSM gets talking points at 4am
    ],

    # ── T: Thought Control ────────────────────────────────────────────────────
    # Loaded language, thought-stopping slogans, all-or-nothing, sacred science
    "T": [
        (r"\bwwg1wga\b",                            1.0),  # "Where We Go 1 We Go All"
        (r"\bwhere\s+we\s+go\s+one\b",              1.0),
        (r"\bthe\s+great\s+awakening\b",            0.9),
        (r"\bgreat\s+awakening\b",                  0.8),
        (r"\btrust\s+the\s+plan\b",                 0.9),
        (r"\bnothing\s+can\s+stop\s+what\s+is\s+coming\b", 0.9),
        (r"\bdeep\s+state\b",                       0.8),
        (r"\bthe\s+cabal\b",                        0.8),
        (r"\bcabal\b",                              0.7),
        (r"\bpure\s+evil\b",                        0.8),
        (r"\bgood\s+vs\s+(evil|them)\b",            0.7),
        (r"\bdark\s+to\s+light\b",                  0.8),
        (r"\blight\s+vs\s+dark(ness)?\b",           0.7),
        (r"\bpatriot(s)?\b",                        0.5),
        (r"\banon(s)?\b",                           0.5),
        (r"\bsheeple\b",                            0.8),
        (r"\bnormies?\b",                           0.7),
        (r"\bsleepers?\b",                          0.7),
        (r"\bawake(ned)?\b",                        0.5),
        (r"\bthe\s+storm\b",                        0.8),
        (r"\bq\s+told\s+us\b",                      0.8),
        (r"\bq\s+said\b",                           0.7),
        (r"\bq\s+(confirms?|confirmed)\b",           0.7),
        (r"\bq\s+drops?\b",                         0.6),
        (r"\bfollow\s+the\s+white\s+rabbit\b",      0.7),
        (r"\bdown\s+the\s+rabbit\s+hole\b",         0.6),
        (r"\bmatrix\b",                             0.5),
        (r"\bblue\s+pill\b",                        0.6),
        (r"\bnew\s+world\s+order\b",                0.7),
        (r"\bglobalists?\b",                        0.7),
        (r"\bpanik\b|\bpanic\s+in\s+dc\b",          0.6),
        (r"\bbooom+\b",                             0.5),
        (r"\bq\s+is\s+real\b",                      0.9),
        (r"\balice\s+(in\s+)?wonderland\b",         0.6),
        (r"\bsymbolism\s+will\s+be\s+their\s+downfall\b", 0.8),
    ],

    # ── E: Emotional Control ──────────────────────────────────────────────────
    # Fear, love-bombing, shame, urgency, solidarity manipulation
    "E": [
        # Fear
        (r"\bthey'?re\s+coming\s+for\s+(you|us)\b", 0.9),
        (r"\bafraid\b",                             0.6),
        (r"\bterror(ism)?\b",                       0.6),
        (r"\bdanger(ous)?\b",                       0.5),
        (r"\bthreaten(ed)?\b",                      0.6),
        (r"\bhunters?\s+become\s+the\s+hunted\b",   0.8),
        (r"\bsick\s+people\b",                      0.6),
        (r"\bpure\s+evil\b",                        0.8),
        # Love-bombing
        (r"\bgod\s+bless\b",                        0.7),
        (r"\bbless\s+you\b",                        0.6),
        (r"\bwe\s+love\s+(you|our)\b",              0.7),
        (r"\bthank\s+you\s+for\s+your\s+service\b", 0.6),
        (r"\bhero(es)?\b",                          0.5),
        (r"\bpatriot(s)?\b",                        0.5),
        (r"\bgod\s+wins\b",                         0.7),
        (r"\bgod\s+bless\s+america\b",              0.6),
        (r"\byou\s+are\s+(wonderful|great|amazing)\b", 0.6),
        # Shame & othering
        (r"\bsheeple\b",                            0.8),
        (r"\bnormies?\b",                           0.7),
        (r"\bsleepers?\b",                          0.6),
        (r"\basleep\b",                             0.5),
        (r"\bbrainwashed\b",                        0.7),
        (r"\bstupid\s+people\b",                    0.7),
        (r"\bpeople\s+are\s+stupid\b",              0.8),
        # Urgency & doom
        (r"\bnow\s+or\s+never\b",                   0.8),
        (r"\blast\s+chance\b",                      0.7),
        (r"\btime\s+is\s+running\s+out\b",          0.7),
        (r"\bact\s+now\b",                          0.6),
        (r"\bsomething\s+big\s+(is\s+)?(coming|about\s+to)\b", 0.7),
        (r"\bhappening\s+now\b",                    0.6),
        (r"\bthis\s+is\s+it\b",                     0.5),
        (r"\bforward\s+this\b",                     0.6),
        (r"\bspread\s+this\b",                      0.5),
        # Solidarity manipulation
        (r"\bwe\s+are\s+one\b",                     0.6),
        (r"\bunity\b",                              0.5),
        (r"\bhold\s+the\s+line\b",                  0.7),
        (r"\bwe\s+stand\s+together\b",              0.6),
        (r"\bnight\s+shift\b",                      0.4),
    ],
}

# Pre-compile all patterns
_COMPILED = {
    dim: [(re.compile(pat, re.IGNORECASE), weight) for pat, weight in patterns]
    for dim, patterns in LEXICON.items()
}

DIMENSIONS = ["B", "I", "T", "E"]
DIM_NAMES  = {
    "B": "Behavior Control",
    "I": "Information Control",
    "T": "Thought Control",
    "E": "Emotional Control",
}


# ──────────────────────────────────────────────────────────────────────────────
# Scorer
# ──────────────────────────────────────────────────────────────────────────────

class BITEScorer:
    """Score text on the four BITE model dimensions."""

    def __init__(self, saturation=3.0):
        """
        saturation: how many max-weight hits push a dimension to ~1.0.
        Lower = more sensitive; higher = requires more hits.
        """
        self.saturation = saturation

    def _raw_score(self, text, dim):
        """Sum of weights of all matching patterns for a dimension."""
        total = 0.0
        hits  = []
        for pat, weight in _COMPILED[dim]:
            m = pat.search(text)
            if m:
                total += weight
                hits.append({"pattern": pat.pattern, "match": m.group(), "weight": weight})
        return total, hits

    def score(self, text, include_hits=False):
        """
        Score a single text string.

        Returns
        -------
        dict with keys B, I, T, E, total, dominant_dimension,
        and optionally hits (per-pattern matches).
        """
        if not text or not text.strip():
            result = {d: 0.0 for d in DIMENSIONS}
            result.update({"total": 0.0, "dominant_dimension": None})
            return result

        raw   = {}
        hits  = {}
        for dim in DIMENSIONS:
            r, h = self._raw_score(text, dim)
            raw[dim] = r
            hits[dim] = h

        # Sigmoid-like saturation: score = raw / (raw + saturation)
        scores = {dim: raw[dim] / (raw[dim] + self.saturation) for dim in DIMENSIONS}

        total = sum(scores.values()) / len(DIMENSIONS)
        dominant = max(DIMENSIONS, key=lambda d: scores[d]) if total > 0 else None

        result = {d: round(scores[d], 4) for d in DIMENSIONS}
        result["total"]               = round(total, 4)
        result["dominant_dimension"]  = dominant
        if include_hits:
            result["hits"] = hits
        return result

    def score_corpus(self, posts, text_field="text", id_field="id"):
        """
        Score a list of post dicts. Returns list of {id, B, I, T, E, total, …}.
        """
        results = []
        for p in posts:
            text = p.get(text_field, "")
            s = self.score(text)
            s["id"]      = p.get(id_field, "")
            s["dataset"] = p.get("dataset", "")
            s["platform"]= p.get("platform", "")
            s["board"]   = p.get("board", "")
            s["timestamp"] = p.get("timestamp", 0)
            results.append(s)
        return results

    def aggregate(self, scored_posts):
        """
        Aggregate per-post scores into dataset-level statistics.
        Returns mean, std, and distribution buckets for each dimension.
        """
        if not scored_posts:
            return {}

        import statistics

        agg = {}
        for dim in DIMENSIONS + ["total"]:
            vals = [p[dim] for p in scored_posts if dim in p]
            if not vals:
                agg[dim] = {}
                continue
            agg[dim] = {
                "mean":   round(sum(vals) / len(vals), 4),
                # POST-AUDIT FIX: use statistics.median (averages the two central
                # values for even n) instead of the upper-biased sorted[n//2].
                "median": round(statistics.median(vals), 4),
                "std":    round(statistics.pstdev(vals), 4),
                "max":    round(max(vals), 4),
                "dist": {
                    "not_detected":   sum(1 for v in vals if v < 0.15),
                    "weak":           sum(1 for v in vals if 0.15 <= v < 0.35),
                    "moderate":       sum(1 for v in vals if 0.35 <= v < 0.55),
                    "strong":         sum(1 for v in vals if 0.55 <= v < 0.75),
                    "pervasive":      sum(1 for v in vals if v >= 0.75),
                },
            }

        # Dominant dimension across corpus
        dim_means = {dim: agg[dim].get("mean", 0) for dim in DIMENSIONS}
        agg["corpus_dominant"] = max(dim_means, key=dim_means.get)
        agg["n_posts"] = len(scored_posts)
        return agg

    def temporal_profile(self, scored_posts, window="month"):
        """
        Build a time-series of mean BITE scores.

        window: "day" | "week" | "month" | "year"
        Returns list of {period, B_mean, I_mean, T_mean, E_mean, n}.
        """
        from datetime import datetime, timezone

        def bucket(ts):
            dt = datetime.fromtimestamp(ts, tz=timezone.utc) if ts else datetime(2017, 1, 1)
            if window == "day":   return dt.strftime("%Y-%m-%d")
            if window == "week":  return dt.strftime("%Y-W%W")
            if window == "month": return dt.strftime("%Y-%m")
            return dt.strftime("%Y")

        grouped = defaultdict(list)
        for p in scored_posts:
            grouped[bucket(p.get("timestamp", 0))].append(p)

        timeline = []
        for period in sorted(grouped.keys()):
            group = grouped[period]
            entry = {"period": period, "n": len(group)}
            for dim in DIMENSIONS:
                vals = [p[dim] for p in group]
                entry[f"{dim}_mean"] = round(sum(vals)/len(vals), 4) if vals else 0.0
            timeline.append(entry)
        return timeline


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="BITE model NLP scorer")
    ap.add_argument("--input",   "-i", default=None,   help="path to normalised JSON posts")
    ap.add_argument("--output",  "-o", default=None,   help="output JSON path (default: bite_<dataset>.json)")
    ap.add_argument("--window",  "-w", default="month",help="temporal window: day|week|month|year")
    ap.add_argument("--text",    help="score a single text string and exit (no --input needed)")
    args = ap.parse_args()

    if not args.input and not args.text:
        ap.error("provide --input <file> to score a corpus, or --text <string> to score one text")

    scorer = BITEScorer()

    if args.text:
        result = scorer.score(args.text, include_hits=True)
        print(json.dumps(result, indent=2))
        return

    print(f"Loading {args.input}...")
    with open(args.input, encoding="utf-8") as f:
        posts = json.load(f)
    print(f"  {len(posts)} posts")

    print("Scoring...")
    scored = scorer.score_corpus(posts)

    print("Aggregating...")
    agg  = scorer.aggregate(scored)
    tl   = scorer.temporal_profile(scored, window=args.window)

    dataset_id = posts[0].get("dataset", "unknown") if posts else "unknown"
    out_path = args.output or f"bite_{dataset_id}.json"

    output = {
        "dataset":     dataset_id,
        "n_posts":     len(posts),
        "aggregate":   agg,
        "timeline":    tl,
        "per_post":    scored,
    }

    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nBITE scores for [{dataset_id}]")
    print(f"  Posts:   {agg['n_posts']}")
    for dim in DIMENSIONS:
        d = agg.get(dim, {})
        bar = "█" * int(d.get('mean', 0) * 20)
        print(f"  {dim} ({DIM_NAMES[dim]:<22}) {d.get('mean', 0):.3f}  {bar}")
    print(f"  Total:   {agg.get('total', {}).get('mean', 0):.3f}")
    print(f"  Dominant dimension: {agg.get('corpus_dominant', '?')}")
    print(f"\n  Written: {out_path}")


if __name__ == "__main__":
    main()
