# Codex Goal 09: Navigations-Bezeichnung vereinheitlichen

**Datum:** 2026-05-21

## Geänderte Dateien

- `cases/index.html`
- `reports/codex-goal-09-navigation-labels.md`

## Untracked Dateien

- Neu durch diesen Task: `reports/codex-goal-09-navigation-labels.md`
- Bereits aus dieser Task-Gruppe vorhanden: `datenschutz.html`, `impressum.html`, `robots.txt`, `reports/codex-goal-01-canonical-fix.md`, `reports/codex-goal-02-internal-links.md`, `reports/codex-goal-03-cases-consolidation.md`, `reports/codex-goal-05-legal-pages.md`, `reports/codex-goal-06-robots.md`, `reports/codex-goal-07-brand-name.md`, `reports/codex-goal-08-status-tags.md`
- Bereits vor dieser Task-Gruppe untracked vorhanden laut früherer Prüfung: `.claude/commands/audit-gbp.md`, `reports/_stage1_scrape/`, `reports/codex-goal-21-gbp-automation.md`, `reports/codex-goal-22-impressum-plz-places.md`, `reports/codex-goal-23-firecrawl-gbp-integration-blocked.md`, `reports/codex-goal-24-copy-firecrawl-engine-blocked.md`, `tools/places_lookup.ps1`, `tools/places_lookup_from_impressum.ps1`

## Was wurde geändert

- In `cases/index.html` wurde der Linktext `Cases` in zwei Navigations-/Footer-Links zu `Referenzen` geändert.
- Die Link-Attribute blieben unverändert:
  - `<a href="/cases/" aria-current="page">...`
  - `<a href="/cases/">...`

## Warum

Die Navigation soll einheitlich die deutsche Bezeichnung `Referenzen` verwenden.

## Bewusst nicht geändert

- Keine H1-, H2- oder Section-Titel geändert.
- Keine Linkziele geändert.
- Kein Commit, kein Push, kein Deployment.

## Offene Fragen für Human Review

- Keine.

## Asset- und Lizenzhinweise

- Keine Assets verwendet.

## Lighthouse-Score

- Nicht gemessen. Die Änderung betrifft nur Linktext.

## Empfohlene Tests nach dem Push

- `/cases/` im Browser öffnen und prüfen, ob Navigation und Footer `Referenzen` anzeigen.
- `grep -r '<a [^>]*>Cases</a>' . --include='*.html'`
