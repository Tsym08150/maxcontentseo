# Codex Goal 11: Staging-Domain-Reste im Bewertungsartikel bereinigen

**Datum:** 2026-05-21

## Geänderte Dateien

- `blog/google-bewertung-loeschen.html`
- `reports/codex-goal-11-staging-domain-cleanup.md`

## Untracked Dateien

- Neu durch diesen Task: `reports/codex-goal-11-staging-domain-cleanup.md`
- Bereits aus der vorherigen Audit-Session vorhanden: `reports/codex-goal-01-canonical-fix.md`, `reports/codex-goal-02-internal-links.md`, `reports/codex-goal-03-cases-consolidation.md`, `reports/codex-goal-05-legal-pages.md`, `reports/codex-goal-06-robots.md`, `reports/codex-goal-07-brand-name.md`, `reports/codex-goal-08-status-tags.md`, `reports/codex-goal-09-navigation-labels.md`, `reports/codex-goal-10-h1-duplicate.md`

## Was wurde geändert

- Der `saved from url`-Kommentar mit Staging-Domain wurde entfernt.
- Das alte Rank-Math-JSON-LD mit Staging- und WordPress-URLs wurde durch ein schlankes statisches `BlogPosting`-Schema ersetzt.
- Staging-Domain-`sourceURL`-Kommentare wurden entfernt.
- Der komplette `<style class="wp-fonts-local">`-Block mit 32 `@font-face`-Regeln wurde entfernt, weil die referenzierten Theme-Fonts nicht lokal im Repo vorhanden sind.
- Der WordPress-`wp-importmap`-Block wurde entfernt.
- WordPress-Emoji-Settings und das auto-generierte Emoji-Modul wurden entfernt.
- Ein restlicher root-relativer WordPress-`sourceURL`-Kommentar sowie der WordPress-`speculationrules`-Block mit `wp-content`-Ausschlüssen wurden entfernt, damit keine `wp-content`-/`wp-includes`-Reste bleiben.

## Warum

Die Datei enthielt nach dem ersten Audit-Fix weiterhin WordPress-Exportreste aus der Staging-Installation. Diese verwiesen auf `maxcontentseo-dfkesda1v3.live-website.com`, auf nicht vorhandene WordPress-Pfade oder auf nicht lokal vorhandene Theme-Fonts. Ein reines Domain-Replacement hätte kaputte `/wp-content/...`-URLs unter `maxcontentseo.de` erzeugt; deshalb wurde das Schema statisch und ohne Bild-URL neu gesetzt.

## Bewusst nicht geändert

- Keine übrigen Artikeltexte oder Layoutabschnitte umformuliert.
- Keine neuen Fonts, Bilder, Scripts oder externen Assets hinzugefügt.
- Kein Commit, kein Push, kein Deployment.

## Offene Fragen für Human Review

- Optional später prüfen, ob der Artikel langfristig aus dem WordPress-Export-Markup in ein schlankes statisches Template überführt werden soll.

## Asset- und Lizenzhinweise

- Keine neuen Assets verwendet.
- Entfernt wurden externe Staging-/WordPress-Fontreferenzen, deren Dateien nicht lokal im Repo liegen.

## Lighthouse-Score

- Nicht gemessen. Die Änderung entfernt externe beziehungsweise nicht vorhandene Font-/Scriptreferenzen und sollte die Seite eher entlasten.

## Diff-Statistik

- `blog/google-bewertung-loeschen.html`: 26 Insertions, 66 Deletions.

## Verifikation

- `live-website.com`: 0 Treffer in `blog/google-bewertung-loeschen.html`
- `wp-content`: 0 Treffer in `blog/google-bewertung-loeschen.html`
- `wp-includes`: 0 Treffer in `blog/google-bewertung-loeschen.html`

## Empfohlene Tests nach dem Push

- `curl -s https://maxcontentseo.de/blog/google-bewertung-loeschen.html | grep -E "live-website.com|wp-content|wp-includes"`
- `curl -s https://maxcontentseo.de/blog/google-bewertung-loeschen.html | grep -n "application/ld+json"`
- Google Rich Results Test für `https://maxcontentseo.de/blog/google-bewertung-loeschen.html`
