# Codex Goal 10: Zweite H1 im Blog-Artikel auflösen

**Datum:** 2026-05-21

## Geänderte Dateien

- `blog/google-bewertung-loeschen.html`
- `reports/codex-goal-10-h1-duplicate.md`

## Untracked Dateien

- Neu durch diesen Task: `reports/codex-goal-10-h1-duplicate.md`
- Bereits aus dieser Task-Gruppe vorhanden: `datenschutz.html`, `impressum.html`, `robots.txt`, `reports/codex-goal-01-canonical-fix.md`, `reports/codex-goal-02-internal-links.md`, `reports/codex-goal-03-cases-consolidation.md`, `reports/codex-goal-05-legal-pages.md`, `reports/codex-goal-06-robots.md`, `reports/codex-goal-07-brand-name.md`, `reports/codex-goal-08-status-tags.md`, `reports/codex-goal-09-navigation-labels.md`
- Bereits vor dieser Task-Gruppe untracked vorhanden laut früherer Prüfung: `.claude/commands/audit-gbp.md`, `reports/_stage1_scrape/`, `reports/codex-goal-21-gbp-automation.md`, `reports/codex-goal-22-impressum-plz-places.md`, `reports/codex-goal-23-firecrawl-gbp-integration-blocked.md`, `reports/codex-goal-24-copy-firecrawl-engine-blocked.md`, `tools/places_lookup.ps1`, `tools/places_lookup_from_impressum.ps1`

## Was wurde geändert

- In `blog/google-bewertung-loeschen.html` wurde der WordPress-Post-Title von `<h1>` zu `<h2>` geändert:
  - `Google Bewertung löschen lassen im Kosmetikstudio`
- Die keyword-stärkere Artikelüberschrift bleibt als `<h1>` erhalten:
  - `Negative Google-Bewertung löschen lassen? Der ehrliche Leitfaden für Kosmetikstudios`

## Warum

Der Artikel enthielt zwei Artikel-H1s. Die erste, generische WordPress-Post-Title-Überschrift wurde auf `<h2>` herabgestuft, damit die eigentliche Artikelüberschrift die Haupt-H1 bleibt.

## Bewusst nicht geändert

- Site-Title-H1s aus dem WordPress-Export im Header/Footer wurden nicht verändert, weil Task 10 konkret die doppelte Artikel-H1 adressiert.
- Keine Texte umformuliert.
- Kein Commit, kein Push, kein Deployment.

## Offene Fragen für Human Review

- Optional später prüfen, ob die WordPress-Export-Site-Title-H1s im Header/Footer ebenfalls semantisch bereinigt werden sollen.

## Asset- und Lizenzhinweise

- Keine Assets verwendet.

## Lighthouse-Score

- Nicht gemessen. Die Änderung betrifft nur Überschriften-Markup.

## Empfohlene Tests nach dem Push

- `curl -s https://maxcontentseo.de/blog/google-bewertung-loeschen.html | grep -n "<h1"`
- Artikel im Browser öffnen und prüfen, ob das Layout unverändert wirkt.
