# Goal: Blog und Referenzen einbinden — 2026-05-16

## Geänderte Dateien
- `index.html`
- `cases.html`
- `cases/lingqi.html`
- `Blog`

## Untracked Dateien
- `blog/index.html`
- `blog/google-bewertung-loeschen.html`
- `blog/lingqi-haarausfall.html`
- `reports/codex-goal-blog-referenzen.md`

## Was wurde geändert
- `lingqi_artikel_v2_optimiert.html` wurde nach `blog/lingqi-haarausfall.html` verschoben.
- `Google Bewertung löschen lassen im Kosmetikstudio - MaxContentSEO.html` wurde nach `blog/google-bewertung-loeschen.html` verschoben.
- Die Root-Originaldateien der beiden Artikel sind nicht mehr vorhanden.
- Die leere Datei `Blog` wurde entfernt, damit der echte Ordner `blog/` angelegt werden konnte.
- In `index.html`, `cases.html` und `cases/lingqi.html` wurde die Navigation auf `Referenzen`, `Blog` und CTA angepasst.
- Die CTA-Schriftfarbe wurde mit `color: #fff !important` gesetzt.
- In `index.html` wurde direkt nach der Hero-Sektion ein 2-Spalten-Bereich für Referenzen und Blog eingefügt.
- `blog/index.html` wurde als statische Blog-Übersicht mit Navigation, zwei Artikel-Cards und Footer erstellt.

## Was wurde bewusst nicht geändert
- Die Inhalte der beiden Artikeldateien wurden nicht umgeschrieben.
- Der Google-Bewertung-Artikel bleibt als vorhandener Original-HTML-Export erhalten.
- Für die Google-Bewertung-Card wurde wegen der Vorgabe „Alle Pfade relativ“ kein externes Header-Bild eingebunden, sondern ein lokaler grauer Platzhalter verwendet.
- Es wurden keine Commits, Pushes oder Deployments ausgeführt.

## Offene Fragen für Human Review
- Soll der Google-Bewertung-Artikel später aus dem WordPress-Export in das gleiche statische Layout wie `blog/index.html` überführt werden?
- Soll für den Google-Bewertung-Artikel ein eigenes lokales Header-Bild ins Repo aufgenommen werden?

## Asset- und Lizenzhinweise
- Verwendet wurden vorhandene lokale Assets aus dem Repo: `assets/linqi.PNG`.
- Es wurden keine externen Fonts eingebunden.
- Es wurden keine neuen Stockfotos oder AI-Bilder erzeugt.

## Lighthouse-Score
- Nicht gemessen. Es wurde kein Browser-Lighthouse-Lauf durchgeführt.
