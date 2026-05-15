# Goal Rebuild V1B — Hero Grid Fix, 15.05.2026

## 1. Goal-Bezeichnung und Datum
- Hero-Grid-Bug beheben, bei dem das Foto auf Desktop-Auflösungen in den H1-Bereich hineinwirkte
- Datum: 15.05.2026

## 2. Geänderte Dateien
- `D:\AITools\maxcontentseo\index.html`

## 3. Untracked Dateien
- `D:\AITools\maxcontentseo\reports\codex-goal-rebuild-v1b-hero-fix.md`

## 4. Was wurde geändert
- `index.html`
  - Desktop-Grid des Hero-Bereichs auf `minmax(0, 1fr) minmax(0, 420px)` gesetzt
  - Maximalbreite der Hero-H1 auf `100%` gesetzt

## 5. Was wurde bewusst nicht geändert
- Kein HTML verändert
- Keine anderen CSS-Bereiche außerhalb des Hero-Fixes verändert
- Kein `overflow: hidden` auf der Textspalte entfernt, weil dort in der aktuellen Datei kein solches Rule vorhanden war
- `hero__visual` nicht weiter geändert, weil die aktuelle Datei dort bereits `position: relative` verwendet und kein absolutes Layout auf dem Container selbst gesetzt war

## 6. Offene Fragen für Human Review
- Bitte auf Desktop-Breiten rund um 1024–1280px kurz prüfen, ob die neue Spaltenaufteilung für die gewünschte visuelle Balance passt

## 7. Asset- und Lizenzhinweise
- Keine neuen Assets
- Keine neuen Fonts

## 8. Lighthouse-Score
- Nicht gemessen in diesem Run
