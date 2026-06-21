# QAnon — Research Dossier, Literature & Timeline

A self-contained, fully-cited academic website examining **QAnon as a documented political movement and digital cult**. It treats conspiracy claims strictly as *discourse objects* and labels every load-bearing statement with an epistemic tag (Documented / Reported / Alleged / Disputed / Debunked / Conspiracy). The site is built for academic, journalistic, and educational use.

> **Purpose & ethics.** This project documents and analyses QAnon; it does **not** amplify or endorse its claims. Conspiracy assertions are clearly marked as such, debunked claims are flagged with rebuttals, and survivor-support resources are linked throughout.

---

## Pages

| File | What it is |
|------|------------|
| **`index.html`** | The main dossier — 8 sections (origin, beliefs, manipulation frameworks, money trail, violence & law, cross-movement overlap, academic sources, discourse & survivors) plus consolidated scorecards (BITE, Lifton, Langone, cross-movement) and a numbered source list. |
| **`research.html`** | A **deep, thematically-organised bibliography** of ~27 peer-reviewed works (2017–2025) across five tracks: the **iDRAMA Lab computational corpus** (the 4chan → Voat → Parler → Telegram → Poal platform diaspora), radicalization & security studies, psychology & relational harm, religion & meaning-making, and belief/diffusion/method. Each entry shows venue, year, and verified DOI/arXiv links. Institutional reports (CSIS, ICCT, ADL, Soufan, GWU, NCRI) are listed separately as *not* peer-reviewed. |
| **`review.html`** | A **Critical Review** that stress-tests the evidence base: the threat-inflation debate, the "who is Q" stylometry question, sampling/platform bias in computational work, whether "cult" is the right word, failed prophecy & falsifiability, the antisemitism lineage, and an **evidence-quality scorecard** rating each major claim Strong / Moderate / Contested. |
| **`timeline.html`** | A **sourced event chronology** in seven eras — precursors, the first Q drop, platform migrations, key drops, violent incidents, parallel global events, and a final **"Current events & the news"** era (2022–2026) linking QAnon's mythology to live news: Trump's Q embrace, the January 2025 pardons of the "QAnon Shaman," and the Epstein-files fracture. |
| `assets/style.css` | Shared stylesheet (the "forensic OSINT dossier" design system). |
| `assets/app.js` | Shared JS (scrollspy, mobile nav, reveal-on-scroll). |
| `.nojekyll` | Tells GitHub Pages to serve files as-is (so `assets/` isn't processed by Jekyll). |

All four pages share one stylesheet and one script and are cross-linked via the navigation in the left rail.

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
