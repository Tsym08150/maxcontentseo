# Goal 1: LingQi Case Study Refactor - 2026-05-04

## 1. Goal and date

Goal: Refactor the existing "LingQi - TCM Head Spa Munchen" case study section on the homepage into a visually stronger, more trust-building component.

Date: 2026-05-04

## 2. Changed files

- `index.html`
- `reports/codex-goal-01-lingqi-case.md`

## 3. New CSS classes introduced

- `.case-title-accent`
- `.case-card`
- `.case-grid`
- `.case-aside`
- `.case-label`
- `.case-client`
- `.case-logo`
- `.case-name`
- `.case-meta`
- `.case-content`
- `.case-block`
- `.case-block-label`
- `.case-copy`
- `.case-list`
- `.case-result`
- `.case-result-value`
- `.case-result-note`

## 4. What was changed per file

### `index.html`

- Replaced the old three-metric case card with one larger case component.
- Added a two-column desktop layout with a sticky left column and content-heavy right column.
- Added the LingQi initials placeholder, client name, and `TCM-Praxis · München` subtitle.
- Reworked the right column into `Ausgangslage`, `Vorgehen`, and `Ergebnis`.
- Removed the visible 5-star rating display and the weak `SEO-Basis` metric.
- Added responsive CSS so the case component stacks on tablet and mobile.

### `reports/codex-goal-01-lingqi-case.md`

- Added this implementation report.

## 5. How the mockup reference was interpreted vs adapted

- Reused the mockup's two-column case structure, sticky left column, initials placeholder, right-column content flow, and prominent serif result figure.
- Adapted the mockup to the existing inline CSS architecture in `index.html`.
- Used existing site variables such as `--accent`, `--bg`, `--white`, `--border`, `--serif`, and `--text-muted`.
- Did not copy external font references, mockup wrapper code, bundled preview scripts, or mockup-specific framing.

## 6. What was deliberately NOT changed

- No sections outside the existing case study section were changed.
- No separate CSS file was created.
- No fonts, images, icons, scripts, or external dependencies were added.
- `CNAME`, `README.md`, deployment files, and git settings were not changed.
- No testimonials, logos, star ratings, search-volume numbers, or ranking promises were added.

## 7. Open questions for human review

- Please review whether the condensed case copy is short enough for the intended trust-building rhythm.
- Please check whether the phrase `12+ Keywords mit Ranking-Potenzial` should remain the single prominent result metric.

## 8. Asset and license notes

- No new assets were added.
- No external fonts or font CDNs were added.
- The `LQ` mark is a CSS/text placeholder, not an imported logo or image.

## 9. Lighthouse score before/after if measurable

- Not measured in this run. The change is static HTML/CSS only and adds no external requests, scripts, images, fonts, or build step.
