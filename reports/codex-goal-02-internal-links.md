# Codex Goal 02: Interne Links im Blog-Artikel

**Datum:** 2026-05-21

## Geänderte Dateien

- `reports/codex-goal-02-internal-links.md`

## Untracked Dateien

- Neu durch diesen Task: `reports/codex-goal-02-internal-links.md`
- Bereits vor diesem Task untracked vorhanden laut vorheriger Prüfung: `.claude/commands/audit-gbp.md`, `reports/_stage1_scrape/`, `reports/codex-goal-21-gbp-automation.md`, `reports/codex-goal-22-impressum-plz-places.md`, `reports/codex-goal-23-firecrawl-gbp-integration-blocked.md`, `reports/codex-goal-24-copy-firecrawl-engine-blocked.md`, `tools/places_lookup.ps1`, `tools/places_lookup_from_impressum.ps1`

## Was wurde geändert

- Bereits umgesetzt — keine Änderung an `blog/google-bewertung-loeschen.html` nötig.
- Dieser Report dokumentiert die IST-Zustands-Prüfung.

## Warum keine Änderung nötig war

Die Prüfung der `href`-Attribute in `blog/google-bewertung-loeschen.html` ergab keine internen Links mehr auf `https://maxcontentseo-dfkesda1v3.live-website.com`.

Aktueller Zustand wichtiger Linkziele:

- Zeile 31: Canonical-Link zeigt auf `https://maxcontentseo.de/blog/google-bewertung-loeschen.html`.
- Zeile 710: Logo-Link zeigt auf `../index.html`.
- Zeile 722: Navigation zeigt auf `../cases/`, `index.html` und `/audit-beispiel.html`.
- Zeile 1172 und 1179: CTA-Links zeigen auf `../index.html#kontakt`.
- Zeile 1293: Footer-Links zeigen auf `/index.html#impressum` und `/index.html#datenschutz`.

Die in `codex_todo_v2.md` genannten nicht existierenden Ziele `/kontakt/`, `/impressum/`, `/datenschutzerklaerung/`, `/seo-audit-lingqi-head-spa-muenchen/` und `/blog/` wurden in `href`-Attributen nicht gefunden.

## Bewusst nicht geändert

- Sonstige Staging-Domain-Vorkommen in JSON-LD, CSS-`sourceURL`-Kommentaren, Font-URLs, Script-Modul-Importen und Emoji-Script-Referenzen wurden nicht geändert, weil Task 2 ausdrücklich interne Links im Artikel betrifft.
- Keine Pfad-Normalisierung von bereits funktionierenden relativen Links vorgenommen.
- Kein Commit, kein Push, kein Deployment.

## Offene Fragen für Human Review

- Sollen die verbleibenden Staging-Domain-Vorkommen außerhalb von `href`-Links in einem separaten Task gebündelt bereinigt werden?

## Asset- und Lizenzhinweise

- Keine neuen Bilder, Fonts, Icons oder externen Assets hinzugefügt.

## Lighthouse-Score

- Nicht gemessen. Es gab keine Änderung an ausgeliefertem HTML außer diesem Report.

## Empfohlene Tests nach dem Push

- `curl -s https://maxcontentseo.de/blog/google-bewertung-loeschen.html | grep -o 'href="[^"]*"' | grep 'live-website.com'`
- Blog-Artikel öffnen und Header-Navigation, Kontakt-CTAs sowie Footer-Links manuell anklicken.
