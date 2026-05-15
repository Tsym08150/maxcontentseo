# Goal 01 — LingQi Case Study Visual Trust Update, 15.05.2026

## Geänderte Dateien
- `index.html`
- `reports/codex-goal-01-lingqi-case.md`

## Untracked Dateien
- Keine.

## Was wurde geändert
- LingQi-Case-Study visuell stärker gewichtet.
- Drei Trust-/Metric-Cards ergänzt, ausschließlich mit bestehenden Aussagen aus dem Case:
  - `12+ Keywords mit Ranking-Potenzial`
  - `München` aus `TCM-Praxis · München` und der lokalen Wettbewerbsanalyse
  - `Content-Plan` aus dem bestehenden Ergebnistext
- Ausgangslage und Ergebnis in zwei klar getrennte Panels gesetzt.
- Mobile-Regel ergänzt: Metric-Cards und Ausgangslage/Ergebnis stacken unter `768px`.

## Was wurde bewusst nicht geändert
- Kein neues Anchor-Tag.
- Keine neuen Zahlen, Testimonials, Logos oder Case-Ergebnisse.
- Keine externen Fonts, Bilder, Scripts oder Frameworks.
- Keine anderen Sektionen außerhalb der LingQi-Case-Study.

## Offene Fragen für Human Review
- Keine.

## Asset- und Lizenzhinweise
- Keine neuen Assets.
- Bestehende CSS-Variablen wurden verwendet.

## Lighthouse-Score
- Nicht gemessen; Änderung ist statisches HTML/CSS ohne neue externe Requests.
- Stattdessen Playwright-Render-QA mit lokalem HTTP-Server durchgeführt:
  - Desktop `1440px`: 3 Metric-Cards nebeneinander, Ausgangslage/Ergebnis getrennt, keine Console-Errors.
  - Mobile `375px`: Cards und Panels stacken, kein horizontaler Overflow.
