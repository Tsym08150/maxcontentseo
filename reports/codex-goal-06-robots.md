# Codex Goal 06: robots.txt erstellen

**Datum:** 2026-05-21

## Geänderte Dateien

- `robots.txt`
- `reports/codex-goal-06-robots.md`

## Untracked Dateien

- Neu durch diesen Task: `robots.txt`, `reports/codex-goal-06-robots.md`
- Bereits aus dieser Task-Gruppe vorhanden: `datenschutz.html`, `impressum.html`, `reports/codex-goal-01-canonical-fix.md`, `reports/codex-goal-02-internal-links.md`, `reports/codex-goal-03-cases-consolidation.md`, `reports/codex-goal-05-legal-pages.md`
- Bereits vor dieser Task-Gruppe untracked vorhanden laut früherer Prüfung: `.claude/commands/audit-gbp.md`, `reports/_stage1_scrape/`, `reports/codex-goal-21-gbp-automation.md`, `reports/codex-goal-22-impressum-plz-places.md`, `reports/codex-goal-23-firecrawl-gbp-integration-blocked.md`, `reports/codex-goal-24-copy-firecrawl-engine-blocked.md`, `tools/places_lookup.ps1`, `tools/places_lookup_from_impressum.ps1`

## Was wurde geändert

- `robots.txt` wurde im Repo-Root mit den drei vorgegebenen Zeilen angelegt:
  - `User-agent: *`
  - `Allow: /`
  - `Sitemap: https://maxcontentseo.de/sitemap.xml`

## Warum

`robots.txt` fehlte bisher im Repo-Root. Die neue Datei erlaubt Crawling der Website und verweist auf die Sitemap.

## Bewusst nicht geändert

- Keine Sitemap-Datei erstellt oder geändert.
- Keine weiteren SEO-Metadaten angepasst.
- Kein Commit, kein Push, kein Deployment.

## Offene Fragen für Human Review

- Prüfen, ob `sitemap.xml` live existiert oder separat erstellt werden soll.

## Asset- und Lizenzhinweise

- Keine Assets verwendet.

## Lighthouse-Score

- Nicht gemessen. Die Änderung betrifft nur `robots.txt`.

## Empfohlene Tests nach dem Push

- `curl -I https://maxcontentseo.de/robots.txt`
- `curl -s https://maxcontentseo.de/robots.txt`
