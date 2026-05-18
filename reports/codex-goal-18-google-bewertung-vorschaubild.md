# Goal 18 - Google-Bewertung-Vorschaubild

Datum: 2026-05-18

## Geänderte Dateien

- `index.html`
- `blog/index.html`
- `assets/google-bewertung-loeschen.png`
- `reports/codex-goal-18-google-bewertung-vorschaubild.md`

## Untracked Dateien

- `assets/google-bewertung-loeschen.png`
- `reports/codex-goal-18-google-bewertung-vorschaubild.md`

Hinweis: `reports/codex-goal-17-live-view.md` war bereits vor diesem Goal untracked.

## Was wurde geändert

- `index.html`: Der Platzhalter im Blog-Vorschaubild für „Google Bewertung löschen“ wurde durch das bereitgestellte PNG ersetzt.
- `blog/index.html`: Der Platzhalter im Blog-Listing für denselben Artikel wurde durch dasselbe PNG ersetzt.
- `assets/google-bewertung-loeschen.png`: Bild aus dem Anhang wurde mit ASCII-Dateinamen ins Repo übernommen.
- Für dieses Vorschaubild wurde eine kleine `contain`-Variante ergänzt, damit der Screenshot nicht abgeschnitten wird.

## Was wurde bewusst nicht geändert

- Keine Texte, CTAs, Navigation oder sonstigen Layout-Bereiche außerhalb der betroffenen Blog-Vorschaubilder.
- Keine externen Assets, Fonts, CDNs, Frameworks oder Build-Schritte.
- Keine Änderungen an Deployment-Dateien.

## Offene Fragen für Human Review

- Bitte visuell prüfen, ob das Vorschaubild in der gewünschten Größe und mit genügend Rand wirkt.

## Asset- und Lizenzhinweise

- Verwendet wurde ausschließlich das vom Nutzer bereitgestellte Bild `googleBewertunglöschen.PNG`.
- Keine neuen externen Bildquellen oder Fonts.

## Lighthouse-Score

- Nicht gemessen. Änderung ist klein und betrifft ein lokales PNG-Asset; die lokale Erreichbarkeit wurde mit HTTP 200 für Startseite, Blog-Übersicht und Bild geprüft. Zusätzlich wurde ein temporärer Browser-Screenshot zur Sichtprüfung erzeugt und danach wieder entfernt.
