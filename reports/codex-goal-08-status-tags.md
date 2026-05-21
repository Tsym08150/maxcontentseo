# Codex Goal 08: Status- und NEU-Tags prüfen

**Datum:** 2026-05-21

## Geänderte Dateien

- `reports/codex-goal-08-status-tags.md`

## Untracked Dateien

- Neu durch diesen Task: `reports/codex-goal-08-status-tags.md`
- Bereits aus dieser Task-Gruppe vorhanden: `datenschutz.html`, `impressum.html`, `robots.txt`, `reports/codex-goal-01-canonical-fix.md`, `reports/codex-goal-02-internal-links.md`, `reports/codex-goal-03-cases-consolidation.md`, `reports/codex-goal-05-legal-pages.md`, `reports/codex-goal-06-robots.md`, `reports/codex-goal-07-brand-name.md`
- Bereits vor dieser Task-Gruppe untracked vorhanden laut früherer Prüfung: `.claude/commands/audit-gbp.md`, `reports/_stage1_scrape/`, `reports/codex-goal-21-gbp-automation.md`, `reports/codex-goal-22-impressum-plz-places.md`, `reports/codex-goal-23-firecrawl-gbp-integration-blocked.md`, `reports/codex-goal-24-copy-firecrawl-engine-blocked.md`, `tools/places_lookup.ps1`, `tools/places_lookup_from_impressum.ps1`

## Was wurde geändert

- Keine Code-Änderung.
- Dieser Report dokumentiert die IST-Zustands-Prüfung und die bewusste Entscheidung, nichts zu ändern.

## IST-Zustand

- `blog/google-bewertung-loeschen.html` enthält den Text `Status: In Prüfung` innerhalb eines selbst gebauten SVG-Hero-Mockups.
- Der umgebende HTML-Kommentar lautet `Mock Google Review Card`; der Text ist damit Illustrationsinhalt und kein versehentlicher Workflow-Marker.
- `blog/lingqi-haarausfall.html` enthält weiterhin den `NEU`-Tag in der Überschrift `Welche Arten von Haarausfall gibt es?`.

## Warum bewusst nicht geändert

- Das SVG-Mockup bleibt unverändert, weil `Status: In Prüfung` Teil der Illustration einer gemeldeten Google-Bewertung ist.
- `blog/lingqi-haarausfall.html` bleibt unverändert, weil die Datei in Task 4 nach separatem GO gelöscht werden soll. Falls die Datei später migriert oder anonymisiert wird, wird der `NEU`-Tag separat geprüft.

## Bewusst nicht geändert

- Keine Änderung an `blog/google-bewertung-loeschen.html`.
- Keine Änderung an `blog/lingqi-haarausfall.html`.
- Kein Commit, kein Push, kein Deployment.

## Offene Fragen für Human Review

- Keine für Task 8. Task 4 bleibt abhängig von der Rückmeldung zur LingQi-Haarausfall-Datei.

## Asset- und Lizenzhinweise

- Keine Assets verwendet oder geändert.

## Lighthouse-Score

- Nicht gemessen. Es gab keine Änderung an ausgeliefertem HTML.

## Empfohlene Tests nach dem Push

- Nicht erforderlich für Task 8, da keine Code-Änderung erfolgt ist.
