# Goal 3: Typographic Discipline and Whitespace - 2026-05-04

## 1. Goal and date

Goal: Apply typographic discipline and whitespace improvements to the existing homepage without changing copy, structure, or color palette.

Date: 2026-05-04

## 2. Changed files

- `index.html`
- `reports/codex-goal-03-whitespace.md`

## 3. CSS rules modified or added

- Modified `--section-pad`
- Modified `.hero`
- Modified `.hero-inner`
- Modified `.hero h1`
- Modified `.hero p`
- Modified `nav .cta-sm`
- Modified `.btn-primary`
- Modified `.btn-secondary`
- Modified `.section-title`
- Modified `.section-subtitle`
- Modified `.pricing-cta`
- Modified `.cta-final .section-title`
- Modified `.btn-submit`
- Modified `@media (max-width: 600px)` rules for `section`, `.hero`, and `.hero h1`

## 4. Before/after spacing values where known

- `--section-pad`: from `clamp(4rem, 8vw, 7rem)` vertical to `clamp(6rem, 9vw, 8rem)` vertical.
- `.hero` bottom padding: from `clamp(3rem, 6vw, 5rem)` to `clamp(5rem, 9vw, 7rem)`.
- `.hero-inner` max width: from `800px` to `880px`.
- `.hero h1` font size: from `clamp(2.4rem, 5.5vw, 3.8rem)` to `clamp(2.5rem, 6vw, 5rem)`.
- `.hero h1` line height: from `1.12` to `1.07`.
- `.hero h1` margin bottom: from `1.5rem` to `1.75rem`.
- `.hero p` max width: from `600px` to `65ch`.
- `.hero p` margin bottom: from `2rem` to `2.25rem`.
- `.section-title` margin bottom: from `1.25rem` to `1.5rem`.
- `.section-subtitle` max width: from `600px` to `65ch`.
- `.section-subtitle` margin bottom: from `3rem` to `clamp(3rem, 5vw, 4rem)`.
- Mobile `section` padding: added `clamp(4rem, 12vw, 5rem)` vertical padding.
- Shared CTAs: added `min-height: 44px` to primary, secondary, nav, pricing, and submit buttons.

## 5. What was deliberately NOT changed

- No copy text was changed.
- No HTML structure, section order, or layout grid was changed.
- No colors, fonts, external dependencies, animations, images, or backgrounds were added.
- No fixed viewport heights were introduced.
- `CNAME`, `README.md`, deployment files, and git settings were not changed.

## 6. Open questions for human review

- Please review the larger hero on a real 1440px viewport and confirm the new display scale feels strong without dominating the first screen.
- Please check whether the global section title width feels appropriately disciplined across all German headings.

## 7. Lighthouse score before/after if measurable

- Not measured in this run. The change is CSS-only and adds no external requests, scripts, images, fonts, or build step.
