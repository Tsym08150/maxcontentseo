# Goal 5: SEO-Chancen-Check Tool - 2026-05-04

## 1. Goal and date

Goal: Build an interactive "SEO-Chancen-Check" tool that gives visitors a non-binding visibility estimate based on a few inputs, then captures their email after the result with explicit consent.

Date: 2026-05-04

## 2. New files created

- `tools/seo-check.html`
- `tools/seo-check.css`
- `tools/seo-check.js`
- `reports/codex-goal-05-rechner.md`

## 3. Changes to `index.html`

- Added one secondary hero CTA linking to `/tools/seo-check.html`.
- No other homepage structure, copy, deployment files, or settings were changed.

## 4. Scoring logic documentation

- Branche gives no points and is used for recommendations only.
- Stadt-Größe: Großstadt = 3, Mittelstadt = 2, Kleinstadt = 1.
- Sichtbarkeit: Seite 1 = 3, Manchmal = 2, Nur Name = 1, Weiß nicht = 0.
- Google Business Profile: Vollständig + Beiträge = 3, Selten = 2, Unvollständig = 1, Nicht vorhanden = 0.
- Bewertungen: 50+ = 3, 20-49 = 2, 5-19 = 1, 0-4 = 0.
- Total score maps to:
  - 0-4: Großes Potenzial
  - 5-8: Mittleres Potenzial
  - 9-12: Solide Basis
- The same inputs produce the same score and bucket.

## 5. Edge cases handled

- Missing or manipulated scoring values fall back to 0 points in JavaScript.
- Negative review values are clamped to 0.
- The result form is not shown until the visitor calculates a result.
- The submit button is disabled until the consent checkbox is checked.
- The Google Business Profile recommendation is first whenever the visitor says no profile exists or they do not know.
- Recommendations are de-duplicated and limited to three items.
- At least one content recommendation is included, including the Kosmetikstudio branch case where behandlungsspezifische Keywords are mentioned.
- Failed Formspree submissions show an inline error instead of redirecting.

## 6. DSGVO compliance confirmation

- No data is stored in `localStorage`, `sessionStorage`, or IndexedDB.
- No data is submitted before the visitor clicks submit.
- No analytics, tracking pixels, cookies, third-party scripts, or external CDN resources were added.
- No health data, revenue data, or sensitive business details are requested.
- No fields are pre-filled from any source.

## 7. Privacy link target used

- `/#datenschutz`

## 8. Formspree endpoint used

- `https://formspree.io/f/xwvylgqe`

## 9. Open questions for human review

- Please test whether Formspree accepts the submission payload as expected in production.
- Please review whether the three recommendations feel specific enough without implying a real audit.

## 10. Lighthouse score if measurable

- Not measured in this run. The tool is static HTML/CSS/vanilla JS and adds no external scripts, fonts, analytics, images, or build step.
