# Codex Goal: Canonical-, Backup- und Sitemap-Cleanup

Datum: 2026-06-03

## Geänderte Dateien
- _config.yml
- google-bewertung-loeschen-kosmetikstudio/index.html
- index-backup-20260515.html -> backups/index-backup-20260515.html
- reports/codex-goal-canonical-backup-sitemap-cleanup.md

## Was wurde geändert
- Der alte Google-Bewertung-Blogartikel wurde geprüft: `blog/google-bewertung-loeschen.html` hat bereits einen self-referencing Canonical auf `https://maxcontentseo.de/blog/google-bewertung-loeschen.html`.
- Für die alte WordPress-URL `/google-bewertung-loeschen-kosmetikstudio/` wurde ein statischer noindex-Redirect-Alias im gleichen Muster wie der LingQi-Alias angelegt:
  - Canonical: `https://maxcontentseo.de/blog/google-bewertung-loeschen.html`
  - Meta-Refresh-Ziel: `/blog/google-bewertung-loeschen.html`
- `index-backup-20260515.html` wurde aus dem öffentlichen Root nach `backups/index-backup-20260515.html` verschoben.
- `_config.yml` wurde ergänzt, damit `backups/` beim GitHub-Pages/Jekyll-Build ausgeschlossen wird.

## Was wurde bewusst nicht geändert
- Die neuen GEO-Seiten `/ki-sichtbarkeit-studio-geo/` und `/ki-sichtbarkeits-check/` wurden inhaltlich nicht verändert.
- `sitemap.xml` musste nicht geändert werden: sie enthielt bereits keine Backup-Datei und keine alte Google-Bewertung-Duplikat-URL.
- `sitemap_index.xml` existiert im Repo nicht; live war `/sitemap_index.xml` vor der Änderung 404.

## Redirects
- `/google-bewertung-loeschen-kosmetikstudio/` -> `/blog/google-bewertung-loeschen.html`

Hinweis: GitHub Pages ist statisches Hosting. Der Alias nutzt das vorhandene statische Redirect-Muster per Meta-Refresh/noindex/canonical, nicht serverseitige Rewrite-Regeln.

## Finale URL-Liste in sitemap.xml
- https://maxcontentseo.de/
- https://maxcontentseo.de/cases/
- https://maxcontentseo.de/cases/lingqi.html
- https://maxcontentseo.de/branchen/kosmetikstudios.html
- https://maxcontentseo.de/audit-beispiel.html
- https://maxcontentseo.de/blog/
- https://maxcontentseo.de/blog/google-bewertung-loeschen.html
- https://maxcontentseo.de/blog/lingqi-haarausfall.html
- https://maxcontentseo.de/datenschutz.html
- https://maxcontentseo.de/impressum.html
- https://maxcontentseo.de/ki-sichtbarkeit-studio-geo/
- https://maxcontentseo.de/ki-sichtbarkeits-check/

## Tests
- Local sitemap XML geparst und geprüft:
  - GEO-Seiten enthalten.
  - `/branchen/kosmetikstudios.html` enthalten.
  - Backup-Datei nicht enthalten.
  - alte Google-Bewertung-Duplikat-URL nicht enthalten.
- Vor Änderung live geprüft:
  - `/blog/google-bewertung-loeschen.html` lieferte 200 und self-referencing Canonical.
  - `/google-bewertung-loeschen-kosmetikstudio/` lieferte 404.
  - `/sitemap_index.xml` lieferte 404.
  - `/index-backup-20260515.html` lieferte 200.

## Asset- und Lizenzhinweise
- Keine neuen externen Assets, Fonts oder Scripts.

## Lighthouse-Score
- Nicht gemessen. Änderung betrifft Canonical-/Alias-/Sitemap-/Build-Konfiguration, keine Layout- oder Asset-Änderung.
