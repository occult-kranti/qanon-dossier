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

Scores are produced per-document and aggregated per dataset/time-window.

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
| `qdrops_cluster.py` | The **clustering pipeline** (run locally). Downloads the research-only [JSON-QAnon](https://github.com/jkingsman/JSON-QAnon) dataset, embeds each drop, and lets topics form themselves via **embeddings → UMAP → HDBSCAN** (BERTopic; also `--method hdbscan` and a no-torch `--method kmeans`). Reports **validity** (silhouette + gensim c_v coherence), extracts **metadata** (images, references, tripcodes, source board → corpus composition + board migration), and **tags administrative drops** (`--drop-admin`). Exports `qdrops_clustered.json` + CSV. |
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
