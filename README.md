# QAnon — Research Dossier, Literature & Timeline

A self-contained, fully-cited academic website examining **QAnon as a documented political movement and digital cult**. It treats conspiracy claims strictly as *discourse objects* and labels every load-bearing statement with an epistemic tag (Documented / Reported / Alleged / Disputed / Debunked / Conspiracy). The site is built for academic, journalistic, and educational use.

> **Purpose & ethics.** This project documents and analyses QAnon; it does **not** amplify or endorse its claims. Conspiracy assertions are clearly marked as such, debunked claims are flagged with rebuttals, and survivor-support resources are linked throughout.

---

## Pages

| File | What it is |
|------|----------|
| **`index.html`** | The main dossier — research and analysis introduction. |
| **`research.html`** | A **deep, thematically-organised bibliography** of peer-reviewed works and institutional reports. |
| **`review.html`** | A **Critical Review** that stress-tests the evidence base and contested claims. |
| **`timeline.html`** | A **sourced event chronology** in seven eras, from Pizzagate through 2026. |
| `assets/style.css` | Shared stylesheet (the "forensic OSINT dossier" design system). |
| `assets/app.js` | Shared JS (scrollspy, mobile nav, reveal-on-scroll). |
| `.nojekyll` | Tells GitHub Pages to serve files as-is. |

All pages share one stylesheet and one script and are cross-linked via the navigation in the left rail.

---

## View it locally

Because the pages load a shared `assets/` folder, open them through a tiny local server:

```bash
# from the project folder
python3 -m http.server 8000
# then visit http://localhost:8000 in your browser
```

---

## Publish it as a GitHub Page

You can do this entirely from the GitHub website, or from the command line.

### Option A — command line (fastest)

1. **Create an empty repo on GitHub** (no README/license — this folder already has one).

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

### Option B — all in the browser

1. Create a new repository on GitHub.
2. Click **Add file → Upload files**, then drag in all HTML, `README.md`, `.nojekyll`, and the `assets/` folder. Commit.
3. **Settings → Pages → Source: Deploy from a branch → `main` / root → Save.**
4. Visit `https://<YOUR-USERNAME>.github.io/<YOUR-REPO>/`.

> **Tip:** all internal links are **relative** (`assets/style.css`, `research.html`, …), so the site works both at a project URL and at a user/organization URL. No paths need changing.

---

## Notes on sourcing

- Peer-reviewed venues include **ICWSM**, **The Web Conference (WWW)**, **CSCW**, **ACL**, **CogSci**, and journals such as *First Monday*, *Current Sociology*, *Sociological Perspectives*.
- Two figures in the dossier correct commonly-repeated numbers against primary filings.
- Framework scores (BITE, Lifton, Langone) are **analytical assessments** — interpretive, not measured facts.

---

*Compiled 2026 · For academic and educational use.*
