# Microeconomics study site — project context

Read this file first when starting a new session on this project. It holds everything needed to continue the work.

- **Live site:** https://simoneatt11.github.io/microeconomics/
- **Repo:** `simoneatt11/microeconomics` (public). GitHub Pages builds from branch `main`, root folder, with `.nojekyll`.
- **Course:** Microeconomics, MSG 1st year, SBS / ULB (Solvay), Prof. Thierry Lallemand.
- **Purpose:** a personal study companion in English and French. It has a left-side index, a syllabus, and one page per lesson with custom SVG diagrams, interactive widgets and self-check questions.
- **Last updated:** 2026-11-11.

---

## 1. Workflow (how a new session gets added)

1. Simone drops the session's slide PDFs into `~/Downloads/microeconomics/`. PDFs are **gitignored** and never committed.
2. Extract the text with PyMuPDF (`fitz`) or `pypdf`. `pdftotext` is not installed.
3. Write the new page functions in `tools/build.py`, in both EN and FR. Better diagrams than the slides are welcome.
4. Update all of these:
   - the `NAV` array in `assets/nav.js`
   - the home cards (`page_home`)
   - the syllabus sessions table (`page_syllabus`)
   - the `MIT` companion dict (see §5)
5. Build: `python3 -I tools/build.py /Users/3bio_attanasio/Downloads/microeconomics` (prints `ok`).
6. Preview locally with `python3 -m http.server 8765` and Claude in Chrome. Check every chart for label overlaps, and check that the widgets work.
7. Commit and push. Then check the Pages build and the live URLs:
   - `gh api repos/simoneatt11/microeconomics/pages/builds/latest --jq .status` should return `built`
   - `curl` each live URL and expect HTTP 200
8. If CSS or JS changed, bump `V` in `build.py` for cache busting (`style.css?v=N`, `nav.js?v=N`). It is currently **6**. Pages caches files for 10 minutes.

## 2. Repository structure

```
index.html, syllabus.html        generated
lessons/*.html                   generated
assets/style.css                 tokens + dark mode, layout, components, SVG classes, .gx (MIT cards)
assets/nav.js                    sidebar index (NAV), prev/next pager, mobile menu, EN/FR switch
tools/build.py                   the generator (single source of truth for all pages)
.gitignore                       .DS_Store, *.pdf
PROJECT.md                       this file
```

### Conventions in `build.py`
- `write(path, (title_en, title_fr), blocks, root, extra)` writes one page.
  - Each block is either a shared string or an `(en, fr)` tuple. `L(en, fr)` builds a tuple.
  - `write()` calls `apply_mit(path, blocks)`, which injects the MIT companion automatically.
- Bilingual markup: the two languages go in `<div class="en">…</div><div class="fr">…</div>`, and the CSS hides the inactive one.
  - The language is stored in `localStorage("lang")` and applied by an early inline script.
  - The page title carries `data-en` / `data-fr` attributes.
- `chart(lang, xmax, ymax, xticks, yticks, series, marks, xl, yl, title, W, H, extra, aria)` draws economics charts, with Q on the horizontal axis and P on the vertical.
  - Each series takes `pts, cls (line1/line2/lineT), dash, label, lpos, dx, dy, anchor`.
  - Each mark takes `q, p, label, cls, kind="open", guides`.
- Other helpers: `curve(f, x0, x1, n, ymax)`, `num()` (French decimal comma), `frac()`, `vbar`, `hbar`, `marker`, `case_panel`/`cases_grid`.
- Chart colours were validated with the dataviz validator:
  - light mode: `--c1 #007f60`, `--c2 #c2551a`
  - dark mode: `--c1 #3fa886`, `--c2 #cc743c`
  - `.lineT` (text colour) is used as a third series.
- CSS components: `.callout`, `.grid` / `.grid.g4`, `.card`, `.tag`, `.badge`, tables (`.num`, `tr.hl`), `figure`, `.flow` / `.step`, `.timeline`, `.stats`, `details.q` (quiz), `.tot` (widgets), `.toc`, `.formula`, `.kicker`, `.gx` (MIT example cards).

## 3. Current content

| # | Page | Source PDF | Interactive |
|---|------|-----------|-------------|
| 1.1 | `s1-pensee-economique.html`: history of economic thought | pensee_eco_complet.pdf | — |
| 1.2 | `s1-principes.html`: the 7 principles | seance1_Introduction.pdf | — |
| 1.3 | `s1-echange.html`: trade & comparative advantage | seance1_Introduction.pdf | terms-of-trade explorer |
| 2.1 | `s2-offre-demande.html`: supply, demand & equilibrium | seance2_od_FINAL.pdf | equilibrium price slider |
| 2.2 | `s2-elasticite.html`: elasticity | seance2_elasticite.pdf | elasticity / revenue explorer |
| 3.1 | `s3-consommateur.html`: consumer choice | seance3_consommateur.pdf | consumer optimum on the budget line |
| 4.1 | `s4-couts.html`: production costs | seance4_conc_pfte.pdf (part 1) | — |
| 4.2 | `s4-concurrence-parfaite.html`: firm in perfect competition | seance4_conc_pfte.pdf (part 2) | firm decision vs price (shutdown rule) |
| · | `monopole.html`, `oligopole-jeux.html` | *placeholders, "Coming up"* | — |

### Key verified numbers (kept consistent across pages)
- **Session 2 comparative statics** (curves rebuilt to match the slide numbers):
  - Curves: D1 Q = 19 − 6P, S1 Q = 4P − 1, D2 = 24 − 6P, S2 = 4P − 6.
  - Equilibria (P; Q): E1 (2; 7), heatwave (2.5; 9), Covid (2.5; 4), both shocks (3; 6).
- **Session 3:**
  - Indifference curve U1: H = 10 + 400/N.
  - Budget: 2H + N = 80.
  - Optimum: (N 40, H 20), U = 800. Point B ≈ (26.7, 26.7), U ≈ 711.
- **Session 4 cost table:**
  - Fixed cost CF = 50. Variable cost CV = [0, 50, 78, 98, 112, 130, 150, 175, 204, 242, 300, 385].
  - Minima: marginal cost Cm = 14 (Q 4); average variable cost CVM = 25 (Q 6–7); average total cost CTM = 31.75 (Q 8).
  - Profit-maximising output by price: p 20 → 0; p 28 → Q 7 (π −29); p 35 → Q 8; p 50 → Q 9 (π 158); p 80 → Q 10.
- **T-shirt isocosts:** 460 / 380 / 420 / 660 when machines cost €100; 410 / 280 / 270 / 360 when they cost €50.
- **Exercise:**
  - CVM = Cm = 38 at Q 80.
  - At Q 100: CVM 42, Cm 58.
  - Decisions: p 35 → 0; p 50 → 80 (variable profit 960); p 80 → 100 (3,800).
- **Industry chart:**
  - D1 p = 70 − q, S1 p = q − 6.5, D2 p = 106.5 − q, S3 p = q − 43.
  - A (38.25, 31.75), B (56.5, 50), C (74.75, 31.75).
- **Electricity:** CCGT marginal cost ≈ 102.7 €/MWh. Belpex July 2026: €105.64/MWh. The capacity widths in the merit-order chart are illustrative.

### Choices that differ from the slides (tell Simone / check with the professor)
- **Economic profit.** Slide 22 says "profit économique = profit comptable **+** coûts d'opportunité". The site uses the standard **−**.
- **Firm interactive (4.2).** It works on whole units from the cost table, so Q* = 9 at p = 50. The slide's continuous curve gives ≈ 9.4.
- **Session 2 comparative-statics curves.** They were reconstructed so the drawn equilibria match the slide numbers.

## 4. Session history (what was asked and done)
1. Created the public repo `microeconomics` and set up GitHub Pages. The home page and 10 placeholder lessons were later replaced by real content.
2. Added the EN/FR language switch. A visibility issue turned out to be browser caching, fixed with `?v=` cache busting.
3. Session 1 (intro + history of economic thought) → pages 1.1–1.3, with custom SVGs (Kalundborg, PPFs, …).
4. Session 2 → pages 2.1–2.2 with interactives.
5. Sessions 3 & 4 → pages 3.1, 4.1, 4.2 with interactives.
6. Added the MIT 14.01 companion (Prof. Jonathan Gruber) to every lesson (see §5).

## 5. MIT 14.01 companion (Gruber, Fall 2023, OCW, CC BY-NC-SA 4.0)
Simone likes Gruber's style and examples, so every lesson includes them. The material lives in `build.py`:
- `LEC` dict: for each lecture, its slug, transcript id, YouTube id, length in seconds, EN/FR titles and whether a handout exists.
- `gx()`: one example card, with a "▶ Watch from mm:ss" YouTube link. The timestamp is estimated as the example's position in the transcript × the video length, minus 20 s.
- `mit_top()`: the callout at the top of each lesson.
- `mit_head()`: the example section, inserted just before "Check yourself".
- `mit_more()`: the "Go further" table with Video, Transcript and Handout links, plus the credit line.
- `MIT` dict: the per-page examples. `MIT_UPCOMING`: links only for Lec 11–14.

| Session | MIT lectures |
|---|---|
| 1.1 | Lec 1 (water–diamond paradox, capitalism vs planning) |
| 1.2 | Lec 1 (opportunity cost, eBay kidney), Lec 2 end (drink-size pricing) |
| 1.3 | Lec 18 (Colombia/US roses & computers, LeBron, Pokémon deficit) |
| 2.1 | Lec 1 (roses: Q = 1800 − 400P, Q = 200P → P 3, Q 600), Lec 9 (shocks, Kardashian corsets, consumer surplus, price ceiling), Lec 10 (1970s gas lines, ticket scalping, taxi medallions/Uber) |
| 2.2 | Lec 4 (insulin vs burgers, income elasticity), Lec 9 (consumer surplus vs elasticity); exercise with roses elasticity −2 / +1 |
| 3.1 | Lec 2 (U = √(SC), MRS), Lec 3 (4S + 2C = 24 → (6, 3), Weight Watchers, SNAP vs cash), Lec 4 (demand C = 12/p, substitution −1.10 / income −0.90), Lec 25 (β–δ: $100 vs $125) |
| 4.1 | Lec 5 (shovel, MRTS = −K/L, Malthus), Lec 6 (C = 10 + 5q², sunk-cost Journey tickets, Tesla, isocost w 5 r 10 → L 5 K 2.5) |
| 4.2 | Lec 7 (eBay / Eiffel keychains, p 30 → q 3 π 35, tax → q 2 π 10, p 10 → keep producing, market p 30 Q 18), Lec 8 (Dell/IBM entry–exit, cotton rent $0.85/kg), Lec 6 end (start-up economic profit −$81,000) |
| Monopoly / Oligopoly | Lec 11–12 / Lec 13–14 (links only for now) |

**Corrections to Gruber's spoken numbers** (flagged on the site):
- L7: the profit at p = 30 is **35**, not 40.
- L6: AC is minimised at q = √2 ≈ 1.41, not 1.5.
- L6: expansion-path points are (L 5, K 2.5), (10, 5), (15, 7.5), taken from the handout.

**Technical notes:**
- WebFetch cannot read the OCW PDFs. Download them with `curl` into the scratchpad and extract them with `fitz`.
- Transcripts have no timestamps; video lengths came from YouTube.
- Transcript URLs are `https://ocw.mit.edu/courses/14-01-principles-of-microeconomics-fall-2023/<id>_transcript.pdf`.
- Handout URLs are `…/mit14_01_f23_handout<N>.pdf`. There is no handout for Lec 25.

## 6. Next steps
- When the monopoly and oligopoly / game-theory slides arrive:
  - Replace the two placeholders and add the sessions to `NAV`, home and syllabus.
  - Read the MIT Lec 11–14 transcripts. Their transcript ids are already in `LEC`.
  - Move those pages from `MIT_UPCOMING` to full `MIT` entries with examples.
- Simone will go through the pages and ask about anything unclear. Add clearer explanations or extra worked examples to the relevant page when that happens.
