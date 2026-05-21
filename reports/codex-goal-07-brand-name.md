# Codex Goal 07: Markenname vereinheitlichen

**Datum:** 2026-05-21

## Geänderte Dateien

- `audit-beispiel.html`
- `danke.html`
- `cases/lingqi.html`
- `blog/index.html`
- `index.html`
- `cases/index.html`
- `branchen/kosmetikstudios.html`
- `reports/codex-goal-07-brand-name.md`

## Untracked Dateien

- Neu durch diesen Task: `reports/codex-goal-07-brand-name.md`
- Bereits aus dieser Task-Gruppe vorhanden: `datenschutz.html`, `impressum.html`, `robots.txt`, `reports/codex-goal-01-canonical-fix.md`, `reports/codex-goal-02-internal-links.md`, `reports/codex-goal-03-cases-consolidation.md`, `reports/codex-goal-05-legal-pages.md`, `reports/codex-goal-06-robots.md`
- Bereits vor dieser Task-Gruppe untracked vorhanden laut früherer Prüfung: `.claude/commands/audit-gbp.md`, `reports/_stage1_scrape/`, `reports/codex-goal-21-gbp-automation.md`, `reports/codex-goal-22-impressum-plz-places.md`, `reports/codex-goal-23-firecrawl-gbp-integration-blocked.md`, `reports/codex-goal-24-copy-firecrawl-engine-blocked.md`, `tools/places_lookup.ps1`, `tools/places_lookup_from_impressum.ps1`

## Was wurde geändert

- In sieben freigegebenen HTML-Dateien wurde die Footer-Schreibweise `Max Content SEO` zu `MaxContentSEO` geändert.

## Warum

Der Markenname soll konsistent als `MaxContentSEO` geschrieben werden.

## Bewusst nicht geändert

- `index-backup-20260515.html` wurde nicht geändert, weil die Datei den historischen Stand vom 15.05. konservieren soll.
- `blog/lingqi-haarausfall.html` wurde nicht geändert, weil die Datei für Task 4 vorgemerkt ist und erst nach separatem GO gelöscht wird.
- Keine anderen Texte, Layouts oder Links geändert.
- Kein Commit, kein Push, kein Deployment.

## Offene Fragen für Human Review

- Keine.

## Asset- und Lizenzhinweise

- Keine Assets verwendet.

## Lighthouse-Score

- Nicht gemessen. Die Änderung betrifft nur Footer-Text.

## Empfohlene Tests nach dem Push

- `grep -r "MaxContent SEO\\|Max Content SEO" . | grep -v ".backups\\|reports"`
- Footer auf Startseite, Blog-Übersicht, Cases und Branchen-Seite kurz prüfen.
