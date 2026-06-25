# QAnon — Research Dossier & Computational Analysis

A fully-cited academic website and **multi-dataset NLP research platform** examining QAnon as a political movement and digital cult. Conspiracy claims are treated as *discourse objects*, labelled with epistemic tags (Documented / Reported / Alleged / Disputed / Debunked / Conspiracy), and never amplified.

> **Purpose & ethics.** This project documents and analyses QAnon; it does **not** amplify or endorse its claims. Debunked claims are flagged with rebuttals; survivor-support resources are linked throughout.

## Quick start

```bash
pip install -r requirements.txt

# 1 – collect & organise all datasets
python collect_datasets.py

# 2 – run BITE scoring + clustering on every dataset
python multi_dataset_analysis.py

# 3 – compare results across datasets
python compare_results.py

# 4 – single-dataset explorer (original pipeline)
python qdrops_cluster.py          # Q drops only, BERTopic
python qdrops_sweep.py            # stability sweep
python qdrops_patterns.py        # metadata patterns → original_findings.json

# 5 – view results
python3 -m http.server 8000       # → http://localhost:8000
```

## Improved Experiment (Ablation + Plots + Bundle)

Use this when you want a paper-style experiment refresh with model/parameter ablations,
updated reports, and publication-ready figures.

### Recommended runtime
- Prefer **T4 GPU** for the largest practical sentence-transformer stack in this repo.
- `v5e-1 TPU` is not ideal for this Python clustering stack (BERTopic/HDBSCAN are GPU/CPU-centric).

### Single-command Colab run

Paste this in one Colab cell:

```bash
!bash -lc "set -euo pipefail; rm -rf /content/qanon-dossier; git clone --depth 1 --branch main https://github.com/occult-kranti/qanon-dossier.git /content/qanon-dossier; cd /content/qanon-dossier; python -m pip install -q --upgrade pip; python -m pip install -q -r requirements.txt; python improved_experiment.py --device t4 --method bertopic --models BAAI/bge-large-en-v1.5,all-mpnet-base-v2,all-MiniLM-L6-v2 --mcs 15,25,40 --admin-ablation --bundle /content/qanon_results_bundle_improved.zip; echo DONE:/content/qanon_results_bundle_improved.zip"
```

### What it generates
- Standard outputs:
   - `results/<dataset>/analysis.json`
   - `results/index.json`
   - `compare_results.json`
   - `compare_results.html`
   - `run_*.json`, `stability_report.json`, `stability_report.csv`
- Improved outputs:
   - `results/improved/improved_experiment_codebook.json`
   - `results/improved/improved_experiment_report.json`
   - `results/improved/improved_experiment_report.md`
   - `results/improved/improved_experiment_report.html`
   - `results/improved/plots/*.png`
- Transfer bundle zip:
   - `/content/qanon_results_bundle_improved.zip`

## Latest run — best result, setup & LLM

**Experiment setup.** BERTopic (sentence-transformers → UMAP → HDBSCAN) on the full **4,966-drop** Q corpus, device target **T4 GPU**, run as a 12-cell ablation: three embedding models — **BAAI/bge-large-en-v1.5** (primary), **all-mpnet-base-v2**, **all-MiniLM-L6-v2** — crossed with **min_cluster_size ∈ {15, 25, 40}**, in both the full and admin-filtered corpora. Each run is scored on a composite of silhouette separation, gensim c<sub>v</sub> coherence, and cross-run topic persistence.

**Best run (composite winner):**

| Run | Model | mcs | Topics | Silhouette | c_v | Persistence | Score |
|---|---|---:|---:|---:|---:|---:|---:|
| **MiniLM·mcs40** | all-MiniLM-L6-v2 | 40 | 2 | **0.795** | **0.478** | 0.525 | **0.597** |
| MPNet·mcs40 | all-mpnet-base-v2 | 40 | 2 | 0.815 | 0.324 | 0.538 | 0.578 |
| bge·mcs40 (admin) | bge-large-en-v1.5 | 40 | 3 | 0.612 | 0.300 | 0.683 | 0.585 |

The two-topic solutions win because they are **robust**, not because they are simple: MiniLM·mcs40 and MPNet·mcs40 (two independent models) agree at Jaccard **0.928**, while finer settings shatter into 39–56 fragile topics that don't survive a model swap. Full scoreboard: [`results/improved/improved_experiment_report.md`](results/improved/improved_experiment_report.md).

**LLM used.** The baseline pipeline (embeddings, clustering, BITE) is **fully deterministic and LLM-free**. An LLM enters only as an *optional* extension for narrative topic-label refinement, profiled in `compare_results.json`: framework **Ollama**, default **qwen2.5:7b** (high-quality **qwen2.5:14b**, fallback **qwen2.5:3b**), strict **JSON mode**, **temperature 0, top_p 0.1, top_k 20, seed 42**, schema-validate-and-retry. No confidence scores are reported.

## Patterns, commonalities & two theories

A reproducible metadata pass — **`qdrops_patterns.py` → `results/improved/original_findings.json`** — mines signals the topic/BITE pipeline discards. Run it with `python qdrops_patterns.py`.

**Commonalities found across the drops:**
- **One travelling lexicon.** The same anchor words (`storm, patriots, coming, god, fisa, drop, msm, ready, wwg1wga, panic, map, trust`) recur across all 21 platform pairs; the strongest is **Parler × Twitter (Jaccard 0.273)** and **WWG1WGA** is the most stable topic across every embedding model.
- **Affective uniformity.** At mcs40 the corpus collapses to **two robust topics** (a slogan cluster + a ~4,000-drop "god/patriots/time" affect blob).
- **Stylistic drift across the migration.** 4chan→8chan→8kun: median length **17→12→8 words**, URL share **2.8%→31%→56%**, questions/drop **3.22→1.21→1.20**.
- **A single human's clock.** Posting time-of-day shows a **143×** busy/quiet ratio; the deepest 3-hour window (11–13 UTC) holds just **0.44%** of all drops, landing in the sleep band for every US time zone. 25.6% of consecutive drops are <5 min apart (typing sessions).

**Most data-backed theory.** *The drops are an affective engagement engine; the audience is the amplifier.* Thought-control dominates all 7 platforms while behaviour-control ≈ 0; the source is the **quietest** BITE signal (0.0184) and downstream platforms score **5.6–7.1× higher**; the corpus is mostly one affect blob; and it grew vaguer over time. Survives the stability sweep, the ablation, and directional/strong replication of Hoseini/iDRAMA/Hassan. **⚠ Caveat (added after adversarial review):** the amplification pillar rests on the six downstream datasets, which are *synthetic samples* (`collect_datasets.py make_sample`; `catalog.json` shows `local_path: null`), so the 5.6–7.1× figure is a lexicon-and-authorship artifact pending real platform data — see [`future.html`](future.html). The theory's other pillars stand on the real Q corpus.

**Most conspiratorial reading (shown as a discourse object, *not endorsed*).** *"The drops are a coordinated military-intelligence comms channel (the 'Q clock')."* Believers point at "operational" clusters (`sec_test · dod_route · oig·indictments`), timestamp-sync ("future proves past"), stable cross-platform slogans, and a 2020-03 Thought-control peak as "COVID foreknowledge." Every pillar is unfalsifiable post-hoc pattern-matching: repetition ≠ coordination, deplatforming ≠ orders, and the spike is the whole internet discovering COVID. The decisive point: the backed theory *predicts* the conspiratorial one — a corpus engineered for reinterpretation is exactly one in which motivated readers always "find" a hidden signal. Full side-by-side on [`index.html#readings`](index.html) and [`results.html#two-readings`](results.html).

## Original theories & designed experiments

Four falsifiable hypotheses derived from the data, each with a test and a kill condition (see `index.html#theories`):

| # | Theory | Designed experiment | Falsified if |
|---|---|---|---|
| **T1** | Single nocturnal operator, not a 24/7 team | Per-phase UTC-hour KDE + **DST-shift test** (does the trough track US daylight saving?); bootstrap a uniform null | Activity ~uniform across 24 h, or trough ignores DST |
| **T2** | Stylometric handoff at the 8chan→8kun migration (Nov 2019) | Change-point detection on a monthly style vector; phase-A vs phase-C authorship classifier | Change-points fall at random months; A/C not separable |
| **T3** | Engagement-maximising vagueness ("falsifiability decay") | Regress per-drop concreteness on time **and** downstream audience; interrupted time-series at failed-date events | Concreteness flat/rising; no break at failures |
| **T4** | Affective floor, informational ceiling | Hierarchical persistence: does each drop's topic survive all 3 models? + affect-vs-info classifier over time | Many mid-sized info topics persist across all models |

## New theory: Delegated Closure (`future.html` + `dci.py`)

A novel **measurement** contribution (not a new narrative — the producer/consumer "guided apophenia" reading is credited to Berkowitz, Argentino, Phillips & Milner, Muirhead & Rosenblum). **Thesis:** Q drops don't *transmit* cult control; they *solicit* it by withholding interpretive closure, so the audience self-authors the missing meaning and owns it as personal discovery.

The contribution is the **Delegated-Closure Index (DCI)** — the first per-post, embedding-free, LLM-free, regex-computable score of "gap-leaving":

```
DCI = clip( 0.22·INTERROGATIVE + 0.20·DECODE + 0.18·REDACTION
          + 0.15·BREVITY + 0.13·(1−CONCRETENESS) + 0.12·(1−GROUNDING), 0, 1 )
```

Built to be **non-circular**: engagement is never an input; tokens shared with `bite_scorer.py` (`future proves past`, `trust the plan`, `map`) are removed from DECODE; word-count is partialled out of every DCI-vs-BITE comparison.

**Honest results scorecard** (computed by `dci.py` on the real 4,966-drop corpus):

| Claim | Verdict | Evidence |
|---|---|---|
| DCI computable & non-degenerate | ✅ Pass | mean 0.342 ± 0.137, range 0.00–0.90 |
| DCI independent of BITE (non-circular) | ✅ Pass | r=0.05; partial-r (word-count out) = −0.03 |
| DCI weight-invariant | ✅ Pass | weighted vs uniform-1/6 r=0.96 |
| DCI discriminates gap-leaving vs self-resolving | ✅ Pass | high = "Coincidence?" cascades; low = URL-grounded links |
| Openness drifts upward over time (ODS) | ⬇ Downgraded | overall −0.0026/yr ≈ placebo 0.0017 → a **mode-shift**, not a rise |
| Falsifiability economy (FER rises) | ❌ Rejected | FER **falls** 0.71→0.50→0.34 across 2017–19 |
| Source openness → downstream control (5.6–7.1×) | ⛔ Blocked | downstream corpora are **synthetic** — not computable here |

The negatives are kept on purpose: a theory page that buried its rejected hypotheses and its synthetic-data problem would violate the dossier's evidence-grading contract. Full write-up, prior-research ledger, and the 5-phase roadmap (Phase 0 = collect real downstream data) live on [`future.html`](future.html).

## Datasets

See [`datasets/CATALOG.md`](datasets/CATALOG.md) for the full database list with sources, licenses, and download instructions. The collector (`collect_datasets.py`) auto-downloads freely available datasets and documents the rest.

## BITE model scoring

`bite_scorer.py` implements Steven Hassan's four-dimension BITE model as an NLP scorer:

| Dimension | Measures |
|---|---|
| **B** Behavior | Compliance instructions, surveillance, control rhetoric |
| **I** Information | Gatekeeping, enemy-media framing, insider knowledge |
| **T** Thought | Loaded language, thought-stopping slogans, black/white thinking |
| **E** Emotional | Fear, love-bombing, shame, urgency |

Scores are produced per-document and aggregated per dataset/time-window. **Key cross-platform finding:** Thought Control is the dominant dimension on **all 7** datasets, while the Q drops themselves are the *lowest*-scoring corpus (BITE total 0.0184) and downstream platforms score **5.6–7.1× higher**. **⚠ Important:** the six downstream datasets are *synthetic samples* (`collect_datasets.py make_sample`; `catalog.json` `local_path: null`), so the amplification figure is an artifact of researcher-authored, Q-saturated seed prose scored by a Q-keyword lexicon — **not** evidence of audience manufacture. Treat it as provisional pending real platform collection (see `future.html` and the `Delegated Closure` roadmap). Behaviour Control ≈ 0 everywhere is a genuine finding on the real Q corpus.

## Replicating related work

`multi_dataset_analysis.py` replicates the methodology of three key papers:

| Paper | Replicated via |
|---|---|
| Hoseini et al. 2021 – *Globalization of QAnon* | Cross-platform topic overlap (Jaccard on BERTopic word sets) |
| iDRAMA Lab – platform diaspora | Board-migration timeline per dataset |
| Priniski & Bavel 2021 – motivated reasoning | Identity-protective reasoning keyword classifier |

Results land in `compare_results.json` and `compare_results.html` (web dashboard tab).

---

## Pages

| File | What it is |
|------|------------|
| **`index.html`** | **Home / start page** — how to use each page, detailed summaries of every Drops-lab implementation, data provenance, and the rules for reading the analytics. (Was the dossier; the dossier now lives at `dossier.html`.) |
| **`dossier.html`** | The main dossier — 8 sections (origin, beliefs, manipulation frameworks, money trail, violence & law, cross-movement overlap, academic sources, discourse & survivors) plus consolidated scorecards (BITE, Lifton, Langone, cross-movement) and a numbered source list. |
| **`research.html`** | A **deep, thematically-organised bibliography** of ~27 peer-reviewed works (2017–2025) across five tracks: the **iDRAMA Lab computational corpus** (the 4chan → Voat → Parler → Telegram → Poal platform diaspora), radicalization & security studies, psychology & relational harm, religion & meaning-making, and belief/diffusion/method. Each entry shows venue, year, and verified DOI/arXiv links. Institutional reports (CSIS, ICCT, ADL, Soufan, GWU, NCRI) are listed separately as *not* peer-reviewed. |
| **`review.html`** | A **Critical Review** that stress-tests the evidence base: the threat-inflation debate, the "who is Q" stylometry question, sampling/platform bias in computational work, whether "cult" is the right word, failed prophecy & falsifiability, the antisemitism lineage, and an **evidence-quality scorecard** rating each major claim Strong / Moderate / Contested. |
| **`timeline.html`** | A **sourced event chronology** in seven eras — precursors, the first Q drop, platform migrations, key drops, violent incidents, parallel global events, and a final **"Current events & the news"** era (2022–2026) linking QAnon's mythology to live news: Trump's Q embrace, the January 2025 pardons of the "QAnon Shaman," and the Epstein-files fracture. |
| **`drops.html`** | An **interactive drop-cluster explorer + analytics dashboard**. Reads `qdrops_clustered.json` and renders a UMAP **cluster map**, **topic breakdown**, **searchable reader**, drops-per-year and monthly-volume charts (with literature milestones), **per-topic temporal sparklines**, a **validity readout** (silhouette + c_v), **corpus composition** and **board-migration** charts, a **tripcode-rotation timeline** (an authenticity signal), an **administrative-drop filter**, a **cross-reference table** vs. the peer-reviewed literature, and a **Stability panel** (loads `stability_report.json`; **click a stable topic to read its drops** in the reader). Works the moment the JSON is present; otherwise offers a file-picker + schema-preview demo. |
| **`methods.html`** | A consolidated **methods and data map**: all databases/derived files used, grouped experiment setup (normalization → clustering → validity → stability), and peer-reviewed tracks grouped by analytical role for quick reproducibility and evidence lookup. |
| **`future.html`** | The newest page: a **novel measurement theory — "Delegated Closure"** — and its metric, the **Delegated-Closure Index (DCI)**, the first per-post, embedding-free, LLM-free, regex-computable measure of how much interpretive closure a drop withholds. Carries an honest results scorecard (4 passes, 1 downgrade, 1 rejected hypothesis, 1 blocked), the **synthetic-downstream-data disclosure**, a prior-research ledger, and a phased research roadmap. Reads `results/improved/dci_findings.json`. |
| `qdrops_cluster.py` | The **clustering pipeline** (run locally). Downloads the research-only [JSON-QAnon](https://github.com/jkingsman/JSON-QAnon) dataset, embeds each drop, and lets topics form themselves via **embeddings → UMAP → HDBSCAN** (BERTopic; also `--method hdbscan` and a no-torch `--method kmeans`). Reports **validity** (silhouette + gensim c_v coherence), extracts **metadata** (images, references, tripcodes, source board → corpus composition + board migration), and **tags administrative drops** (`--drop-admin`). Exports `qdrops_clustered.json` + CSV. |
| `qdrops_patterns.py` | A **metadata pattern-miner** over the raw archive. Extracts the signatures the topic/BITE pipeline discards — posting **circadian rhythm** (UTC hour-of-day), **stylistic phase shifts** across the board migration, falsifiable-claim ("concreteness") decay, source-vs-platform **BITE amplification**, and inter-drop cadence. Writes `results/improved/original_findings.json`; backs the patterns & theories panels. |
| `dci.py` | The **Delegated-Closure Index** — a per-drop, embedding-free, LLM-free measure of interpretive gap-leaving (6 lexical components, weights sum to 1), plus its robustness battery: openness-drift slope with a time-shuffle placebo, the falsifiability-economy ratio, weight-invariance, leave-one-out ablation, and a BITE partial-correlation non-circularity check. Writes `results/improved/dci_findings.json`; backs `future.html`. Run `python dci.py`. |
| `qdrops_sweep.py` | A **multi-config sweep + stability comparator**. Runs several embedding models × `min_cluster_size` values (embedding once per model), scores each, writes one `run_*.json` per config, and measures **topic persistence** across runs by document-membership overlap — so you keep the topics that are *stable* (real) and discount the *fragile* ones (artifacts). Writes `stability_report.json` + CSV. |
| `requirements.txt` | Python dependencies for the pipeline (gensim is optional, for c_v). |
| `assets/style.css` | Shared stylesheet (the "forensic OSINT dossier" design system). |
| `assets/app.js` | Shared JS (scrollspy, mobile nav, reveal-on-scroll). |
| `.nojekyll` | Tells GitHub Pages to serve files as-is (so `assets/` isn't processed by Jekyll). |

All seven pages share one stylesheet and one script and are cross-linked via the navigation in the left rail.

## Generating the drop clusters

```bash
pip install -r requirements.txt
python qdrops_cluster.py --inspect       # sanity-check: prints the data structure + a sample
python qdrops_cluster.py                 # recommended: BERTopic + validity; auto-downloads posts.json
# accuracy levers & analysis:
python qdrops_cluster.py --method hdbscan              # embeddings + UMAP + HDBSCAN, no BERTopic
python qdrops_cluster.py --method kmeans -k 14          # quick TF-IDF baseline (no torch / no model)
python qdrops_cluster.py --model all-mpnet-base-v2      # higher-quality embeddings (slower)
python qdrops_cluster.py --reduce-outliers             # reassign the "noise" bucket to nearest topics
python qdrops_cluster.py --drop-admin                  # exclude operational drops (test/trip/comms…)
python qdrops_cluster.py --no-coherence                # skip gensim c_v (faster)
python qdrops_cluster.py --min-cluster-size 30          # coarser topics (default 15 = finer)

# Don't over-trust one clustering — sweep several configs and keep the topics that PERSIST:
python qdrops_sweep.py                                  # MiniLM × {15,25,40}
python qdrops_sweep.py --models all-MiniLM-L6-v2,all-mpnet-base-v2 --mcs 15,25,40
```

Each run now reports **validity numbers**: a **silhouette** score (cluster separation on the UMAP space) and **gensim c_v topic coherence** (mean + per-topic), so "good clustering" is measured, not eyeballed. The pipeline also extracts the metadata the first version discarded — **images, `referenced_posts`, tripcodes, and source board** — and emits a corpus **composition** summary plus a **board-by-year** breakdown (the 4chan → 8chan → 8kun migration). Operational drops ("test", "trip update", "comms", "disregard spelling"…) are **heuristically tagged** so they can be filtered in the page or excluded with `--drop-admin`.

`qdrops_sweep.py` loads/normalises the drops **once**, embeds **once per model**, clusters at each `min_cluster_size`, writes one `run_<model>_mcs<N>.json` per config (each openable in `drops.html`), and then matches topics across runs by **document-membership overlap (Jaccard)**. A topic's **persistence** = its mean best-overlap with the other runs: ≥0.50 = *stable* (real), 0.30–0.50 = *borderline*, <0.30 = *fragile* (an artifact of the settings). It writes **`stability_report.json`** (+ CSV), which the **Stability panel** in `drops.html` loads to show a per-run quality table and the anchor run's topics ranked by persistence.

The dataset's top level is `{"posts": [ … ]}`; the script reads `data["posts"]`. Run `--inspect` first if a future file changes shape. Topic labels are stopword-filtered (clean names like *"covid 19 virus lockdown"* rather than *"the to of"*).

**The explorer page** (`drops.html`) renders everything from `qdrops_clustered.json`: a validity readout (silhouette + c_v), per-topic coherence on each card, live metrics, drops-per-year and monthly-volume charts (with literature milestones), per-topic sparklines, **corpus-composition** and **board-migration** charts, an interactive cluster map, a searchable reader with a **"hide admin"** filter, a **cross-reference table** vs. the published findings (Gospel/iDRAMA, de Zeeuw, Hoseini, Priniski), and a **Stability panel**. An **Unload** button clears the data and returns to the loader (and stays unloaded across reloads). Older JSON files without the new fields still load — those panels simply show "—" until you re-run the pipeline.

This writes **`qdrops_clustered.json`**; place it next to `drops.html` (or use the in-page **Load a JSON file** button) and reload. Dataset: Kingsman, J. (2025) *JSON-QAnon*, DOI 10.13140/RG.2.2.28778.32964 — archived **for research only**. Why not k-NN: it's a *supervised* classifier and can't discover topics on its own; the pipeline uses density-based clustering so the topics self-select (k-NN only enters legitimately as a graph fed to community detection, noted in the script).

---

## View it locally

Because the pages load a shared `assets/` folder, open them through a tiny local server (not by double-clicking the file):

```bash
# from the project folder
python3 -m http.server 8000
# then visit http://localhost:8000 in your browser
```

---

## Publish it as a GitHub Page

You can do this entirely from the GitHub website, or from the command line.

### Option A — command line (fastest)

1. **Create an empty repo on GitHub** (no README/license — this folder already has one). Note its name, e.g. `qanon-dossier`.

2. **In this folder**, run:

   ```bash
   git init
   git add .
   git commit -m "QAnon dossier: site, research bibliography, and timeline"
   git branch -M main
   git remote add origin https://github.com/<YOUR-USERNAME>/<YOUR-REPO>.git
   git push -u origin main
   ```

3. **Enable Pages:** on GitHub, go to **Settings → Pages**. Under **Build and deployment → Source**, choose **Deploy from a branch**. Set **Branch** to `main` and folder to **`/ (root)`**, then **Save**.

4. Wait ~1 minute. Your site will be live at:

   ```
   https://<YOUR-USERNAME>.github.io/<YOUR-REPO>/
   ```

   `index.html` is served automatically as the home page.

### Option B — all in the browser

1. Create a new repository on GitHub.
2. Click **Add file → Upload files**, then drag in `index.html`, `research.html`, `timeline.html`, `.nojekyll`, `README.md`, **and the `assets` folder** (drag the whole folder so `assets/style.css` and `assets/app.js` keep their path). Commit.
3. **Settings → Pages → Source: Deploy from a branch → `main` / root → Save.**
4. Visit `https://<YOUR-USERNAME>.github.io/<YOUR-REPO>/`.

> **Tip:** all internal links are **relative** (`assets/style.css`, `research.html`, …), so the site works both at a project URL (`username.github.io/repo/`) and at a user/organization URL (`username.github.io/`). No paths need changing.

---

## Notes on sourcing

- Peer-reviewed venues include **ICWSM**, **The Web Conference (WWW)**, **CSCW**, **ACL**, **CogSci**, and journals such as *First Monday*, *Current Sociology*, *Sociological Perspectives*, and the Springer *Zeitschrift für Religion, Gesellschaft und Politik*. DOIs are shown where verified against the publisher.
- Two figures in the dossier correct commonly-repeated numbers against primary filings (the Patriot Legal Defense Fund total via IRS Form 8872, and the January 6 "1 in 12" claim via the GWU Program on Extremism).
- Framework scores (BITE, Lifton, Langone) are **analytical assessments** — interpretive, not measured facts — as stated in the dossier's methodology block.

---

*Compiled 2026 · For academic and educational use.*
