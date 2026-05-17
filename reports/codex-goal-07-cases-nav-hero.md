# Goal 03/04/07/09 — Hero, Cases, Asset-Pfad, Navigation, 17.05.2026

## Geänderte Dateien

- `index.html`
- `cases/index.html`
- `cases/lingqi.html`
- `cases.html`
- `audit-beispiel.html`
- `blog/index.html`
- `blog/lingqi-haarausfall.html`
- `blog/google-bewertung-loeschen.html`
- `branchen/kosmetikstudios.html`
- `reports/codex-goal-07-cases-nav-hero.md`

## Untracked Dateien

- `cases/index.html`
- `reports/codex-goal-07-cases-nav-hero.md`

## Was wurde geändert

- `index.html`
  - Hero-Grid auf `minmax(0, 1.1fr) minmax(0, 400px)` angepasst.
  - Hero-H1 auf `clamp(2rem, 3.5vw, 3.2rem)` angepasst.
  - Bestehende Hero-Visual-Mindesthöhe geprüft: `clamp(240px, 30vw, 380px)` war bereits gesetzt.
  - Navigation auf `Cases` mit Ziel `cases/` geändert.
  - LingQi-Sektion zu einem schlankeren Teaser mit Links auf `cases/lingqi.html` und `cases/` gekürzt.
  - Hero-Foto-Referenz geprüft: `src="/assets/georg.jpg"` ist bereits korrekt.

- `cases/index.html`
  - Neue Cases-Übersicht mit Navigation, Hero, Card-Grid, LingQi-Card, Platzhalter-Card und Footer angelegt.
  - Keine erfundenen Kundenstimmen, Logos oder zusätzlichen Cases ergänzt.

- `cases/lingqi.html`
  - Navigation auf `Cases` mit Ziel `./` geändert.
  - Breadcrumb ergänzt.
  - Case-Übersichtslinks auf `./` geändert.

- `cases.html`
  - Bestehende ältere Case-Übersicht in der Navigation und im Footer auf `cases/` verlinkt.

- `audit-beispiel.html`, `blog/index.html`, `blog/lingqi-haarausfall.html`, `blog/google-bewertung-loeschen.html`, `branchen/kosmetikstudios.html`
  - Navigations- bzw. Footer-Links von `Referenzen`/`cases.html` auf `Cases`/`cases/` angepasst, soweit diese Seiten eine entsprechende Navigation oder Footer-Navigation enthalten.

## Was wurde bewusst nicht geändert

- GitHub Pages `Enforce HTTPS` wurde nicht aktiviert. Das ist eine Hosting-Einstellung und fällt laut AGENTS.md unter Deployment-/Hosting-Konfiguration, die Codex nicht ändern darf.
- `assets/georg.jpg.png` wurde nicht umbenannt, weil diese Datei im Repo nicht mehr vorhanden ist. `assets/georg.jpg` existiert bereits und `index.html` referenziert diese Datei.
- Keine externen Fonts, Icons, Bilder oder CDN-Skripte ergänzt.
- `index-backup-20260515.html` wurde als Backup-Datei nicht angepasst.

## Offene Fragen für Human Review

- Soll die alte Root-Datei `cases.html` später entfernt, weitergeleitet oder als Kompatibilitätsseite behalten werden?
- Soll die GitHub-Pages-Einstellung `Enforce HTTPS` manuell in den Repository Settings aktiviert werden?

## Asset- und Lizenzhinweise

- Verwendete Bilder bleiben lokale Repo-Assets:
  - `assets/georg.jpg`
  - `assets/lingqi-foto.webp`
- Die Platzhalter-Card in `cases/index.html` nutzt reine CSS-Flächen.
- Keine neuen Fonts oder externen Assets hinzugefügt.

## Verification

- Lokale Datei-/Asset-Prüfung:
  - `cases/index.html` vorhanden
  - `cases/lingqi.html` vorhanden
  - `assets/georg.jpg` vorhanden
  - `assets/lingqi-foto.webp` vorhanden
- Fokussierter Linkcheck für die geänderten Live-Seiten: alle geprüften lokalen `href`-/`src`-Ziele existieren.
- Suche nach `cases.html` und `georg.jpg.png` im Änderungs-Scope: keine Treffer.
- Brand-Voice-Check auf verbotene Begriffe sowie `Du`/`Dir` in den betroffenen Dateien: keine Treffer.
- Lokaler HTTP-Check über `python -m http.server`:
  - `/` → `200 OK`
  - `/cases/` → `200 OK`
  - `/cases/lingqi.html` → `200 OK`
- Browser-/Playwright-Rendercheck konnte nicht abgeschlossen werden, weil in der verfügbaren Node-Umgebung `playwright-core` fehlt.
- Ein allgemeiner Linkcheck über alle geprüften Seiten meldete bestehende fehlende Export-Assets in `blog/google-bewertung-loeschen.html`; diese Dateien wurden nicht durch diesen Run verursacht.

## Lighthouse-Score

- Nicht gemessen. Die Änderungen sind statische HTML/CSS-Anpassungen ohne neue externe Assets oder Skripte.
