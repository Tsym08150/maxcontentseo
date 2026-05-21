# Codex Goal 03: Cases-Seiten konsolidieren

**Datum:** 2026-05-21

## Geänderte Dateien

- `cases.html`
- `cases/index.html`
- `reports/codex-goal-03-cases-consolidation.md`

## Untracked Dateien

- Neu durch diesen Task: `reports/codex-goal-03-cases-consolidation.md`
- Bereits aus Task 1/2 vorhanden: `reports/codex-goal-01-canonical-fix.md`, `reports/codex-goal-02-internal-links.md`
- Bereits vor dieser Task-Gruppe untracked vorhanden laut `git status`: `.claude/commands/audit-gbp.md`, `reports/_stage1_scrape/`, `reports/codex-goal-21-gbp-automation.md`, `reports/codex-goal-22-impressum-plz-places.md`, `reports/codex-goal-23-firecrawl-gbp-integration-blocked.md`, `reports/codex-goal-24-copy-firecrawl-engine-blocked.md`, `tools/places_lookup.ps1`, `tools/places_lookup_from_impressum.ps1`

## Was wurde geändert

- `cases.html` wurde entfernt, weil parallel `cases/index.html` als eigentliche Cases-Übersicht existiert.
- In `cases/index.html` wurde ein Canonical-Tag ergänzt: `https://maxcontentseo.de/cases/`.
- Relative interne Pfade in `cases/index.html` wurden auf root-relative Pfade umgestellt:
  - `../index.html` → `/`
  - `./` → `/cases/`
  - `../blog/index.html` → `/blog/index.html`
  - `../audit-beispiel.html` → `/audit-beispiel.html`
  - `../index.html#kontakt` → `/index.html#kontakt`
  - `lingqi.html` → `/cases/lingqi.html`

## Warum

Die alte Root-Datei `cases.html` war eine parallele Cases-Seite neben `cases/index.html`. Die Konsolidierung reduziert doppelte URLs und macht die interne Verlinkung von `/cases/` unabhängig vom aktuellen Pfad.

## Bewusst nicht geändert

- Die Linktexte `Cases` wurden nicht in `Referenzen` geändert. Das ist Task 9.
- Inhalte, Layout und Texte der Cases-Übersicht wurden nicht umformuliert.
- Kein Commit, kein Push, kein Deployment.

## Offene Fragen für Human Review

- Nach Deployment prüfen, ob `https://maxcontentseo.de/cases.html` wie gewünscht nicht mehr erreichbar ist oder ob GitHub Pages/Browser-Caches noch alte Inhalte ausliefern.

## Asset- und Lizenzhinweise

- Keine neuen Bilder, Fonts, Icons oder externen Assets hinzugefügt.

## Lighthouse-Score

- Nicht gemessen. Die Änderung betrifft URL-/Meta-Hygiene und Linkpfade.

## Empfohlene Tests nach dem Push

- `curl -I https://maxcontentseo.de/cases/`
- `curl -s https://maxcontentseo.de/cases/ | grep canonical`
- `curl -I https://maxcontentseo.de/cases.html`
- `/cases/` im Browser öffnen und Navigation, Footer sowie den Link zum LingQi-Case prüfen.
