# Codex Goal 05: Datenschutz- und Impressum-Seiten

**Datum:** 2026-05-21

## Geänderte Dateien

- `datenschutz.html`
- `impressum.html`
- `reports/codex-goal-05-legal-pages.md`

## Untracked Dateien

- Neu durch diesen Task: `datenschutz.html`, `impressum.html`, `reports/codex-goal-05-legal-pages.md`
- Bereits aus dieser Task-Gruppe vorhanden: `reports/codex-goal-01-canonical-fix.md`, `reports/codex-goal-02-internal-links.md`, `reports/codex-goal-03-cases-consolidation.md`
- Bereits vor dieser Task-Gruppe untracked vorhanden laut früherer Prüfung: `.claude/commands/audit-gbp.md`, `reports/_stage1_scrape/`, `reports/codex-goal-21-gbp-automation.md`, `reports/codex-goal-22-impressum-plz-places.md`, `reports/codex-goal-23-firecrawl-gbp-integration-blocked.md`, `reports/codex-goal-24-copy-firecrawl-engine-blocked.md`, `tools/places_lookup.ps1`, `tools/places_lookup_from_impressum.ps1`

## Was wurde geändert

- `datenschutz.html` wurde als eigene statische Seite im Root angelegt.
- `impressum.html` wurde als eigene statische Seite im Root angelegt.
- Beide Seiten verwenden Header, Navigation, Footer und System-Font/CSS-Struktur angelehnt an `cases/index.html`.
- `datenschutz.html` enthält die sieben vorgegebenen Abschnitte: Verantwortlicher, personenbezogene Daten, Formspree, Hosting, Cookies/Tracking, Rechte und Beschwerderecht.
- `impressum.html` übernimmt die Inhalte aus dem Inline-Impressum der Startseite.

## Warum

`/datenschutz.html` und `/impressum.html` fehlten bisher als eigene URLs. Die Inhalte existierten nur als Inline-Bereiche auf der Startseite. Eigene Seiten verhindern 404-Aufrufe auf diesen Standardpfaden.

## Bewusst nicht geändert

- Die bestehenden Inline-Bereiche in `index.html` wurden nicht entfernt oder umformuliert.
- Keine Steuernummer, keine USt-ID und kein Streitschlichtungs-Hinweis ergänzt.
- Keine Bilder, Icons, externen Fonts oder externen Scripts hinzugefügt.
- Kein Commit, kein Push, kein Deployment.

## Offene Fragen für Human Review

- Juristische Prüfung der neuen Datenschutzseite vor Live-Schaltung empfohlen.
- Optional später entscheiden, ob Footer-Links global von `/index.html#impressum` und `/index.html#datenschutz` auf die neuen Seiten umgestellt werden sollen.

## Asset- und Lizenzhinweise

- Es wurden keine neuen Assets verwendet.
- Fonts bleiben System-Fonts.

## Lighthouse-Score

- Nicht gemessen. Die neuen Seiten sind statisches HTML/CSS ohne externe Assets.

## Empfohlene Tests nach dem Push

- `curl -I https://maxcontentseo.de/datenschutz.html`
- `curl -I https://maxcontentseo.de/impressum.html`
- `curl -s https://maxcontentseo.de/datenschutz.html | grep canonical`
- `curl -s https://maxcontentseo.de/impressum.html | grep canonical`
- Beide Seiten im Browser öffnen und mobile bei 375px sowie Desktop bei 1440px prüfen.
