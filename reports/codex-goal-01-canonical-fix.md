# Codex Goal 01: Canonical-Fix

**Datum:** 2026-05-21

## Geänderte Dateien

- `blog/google-bewertung-loeschen.html`
- `reports/codex-goal-01-canonical-fix.md`

## Untracked Dateien

- Neu durch diesen Task: `reports/codex-goal-01-canonical-fix.md`
- Bereits vor diesem Task untracked vorhanden laut `git status`: `.claude/commands/audit-gbp.md`, `reports/_stage1_scrape/`, `reports/codex-goal-21-gbp-automation.md`, `reports/codex-goal-22-impressum-plz-places.md`, `reports/codex-goal-23-firecrawl-gbp-integration-blocked.md`, `reports/codex-goal-24-copy-firecrawl-engine-blocked.md`, `tools/places_lookup.ps1`, `tools/places_lookup_from_impressum.ps1`

## Was wurde geändert

- Die Staging-Domain-Bild-Meta-Tags `og:image`, `og:image:secure_url` und `twitter:image` wurden aus `blog/google-bewertung-loeschen.html` entfernt.
- Die zugehörigen verwaisten `og:image:*` Detail-Tags (`width`, `height`, `alt`, `type`) wurden ebenfalls entfernt.
- `canonical` und `og:url` waren bereits korrekt auf `https://maxcontentseo.de/blog/google-bewertung-loeschen.html` gesetzt und wurden nicht verändert.

## Warum

Die entfernten Meta-Tags zeigten auf `https://maxcontentseo-dfkesda1v3.live-website.com/...`. Dadurch konnten Social-/Crawler-Metadaten weiterhin die Staging-Domain referenzieren. Da kein lokal lizenziertes Ersatzbild im Task genannt war, ist Entfernen die konservative Variante gemäß Asset-Regeln.

## Bewusst nicht geändert

- Keine JSON-LD-/Schema-Daten angepasst; das ist nicht Teil von Task 1.
- Keine weiteren Staging-Domain-Vorkommen im Artikel bereinigt; das ist Aufgabe von Task 2.
- Kein Commit, kein Push, kein Deployment.

## Offene Fragen für Human Review

- Soll später ein eigenes lokal gehostetes OG-Bild ergänzt werden? Das wäre ein separater Task mit geklärtem Asset.

## Asset- und Lizenzhinweise

- Keine neuen Bilder, Fonts, Icons oder externen Assets hinzugefügt.
- Externe Staging-Bildreferenzen wurden entfernt.

## Lighthouse-Score

- Nicht gemessen. Die Änderung betrifft nur Meta-Tags im `<head>` und ist nicht performance-relevant.

## Empfohlene Tests nach dem Push

- `curl -s https://maxcontentseo.de/blog/google-bewertung-loeschen.html | grep canonical`
- `curl -s https://maxcontentseo.de/blog/google-bewertung-loeschen.html | grep -E "og:image|twitter:image|live-website.com"`
- Seite im Browser öffnen und prüfen, dass der Artikel weiterhin normal lädt.
