# Goal 2: Dedicated Pricing Section - 2026-05-04

## 1. Goal and date

Goal: Extract pricing information from the FAQ and create a dedicated, visible pricing section on the homepage.

Date: 2026-05-04

## 2. Changed files

- `index.html`
- `reports/codex-goal-02-pricing.md`

## 3. New CSS classes introduced

- `.pricing-section`
- `.pricing-grid`
- `.pricing-card`
- `.pricing-card-featured`
- `.pricing-label`
- `.pricing-price`
- `.pricing-period`
- `.pricing-list`
- `.pricing-cta`
- `.pricing-note`

## 4. What was changed per file

### `index.html`

- Added a dedicated pricing section between "Warum mit mir" and FAQ.
- Added three pricing cards for SEO-Audit, SEO-Betreuung, and Premium-Betreuung.
- Emphasized the middle `ab 499 €` card with a subtle accent border and light background.
- Added CTA links from all pricing cards to `#kontakt`.
- Added the pricing disclaimer below the cards.
- Replaced the FAQ entry "Was kostet SEO?" with the requested audit-only FAQ entry.
- Added responsive pricing CSS inside the existing inline `<style>` block.

### `reports/codex-goal-02-pricing.md`

- Added this implementation report.

## 5. What was deliberately NOT changed

- No separate CSS file was created.
- No fonts, images, icons, scripts, toggles, badges, or external dependencies were added.
- No "Custom Plan" or "Enterprise" card was added.
- No sections outside the pricing insertion point and the specified FAQ entry were changed.
- `CNAME`, `README.md`, deployment files, and git settings were not changed.

## 6. Open questions for human review

- Please review whether `Keine Mindestlaufzeit` in the pricing disclaimer should be reconciled with the existing FAQ recommendation of at least 3 months.
- Please confirm whether the middle card emphasis is visible enough while staying deliberately subtle.

## 7. Asset and license notes

- No new assets were added.
- No external fonts or font CDNs were added.
- The section uses only existing text, HTML, and CSS.

## 8. Lighthouse score before/after if measurable

- Not measured in this run. The change is static HTML/CSS only and adds no external requests, scripts, images, fonts, or build step.
