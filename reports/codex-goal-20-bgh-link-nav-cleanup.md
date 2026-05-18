# Goal 20 - BGH-Link und obere Leiste

Datum: 2026-05-18

## Geänderte Dateien

- `blog/google-bewertung-loeschen.html`
- `reports/codex-goal-20-bgh-link-nav-cleanup.md`

## Untracked Dateien

- `reports/codex-goal-20-bgh-link-nav-cleanup.md`

## Was wurde geändert

- In `blog/google-bewertung-loeschen.html` wurde der Quellenpunkt `BGH, Urteil vom 09.08.2022 – VI ZR 1244/20` klickbar gemacht.
- Der Link zeigt auf die offizielle Rechtsprechungsseite des Bundesgerichtshofs.
- In der oberen Leiste wurde der dünn gedruckte zusätzliche `MaxContentSEO`-Eintrag entfernt.
- Aus der oberen Navigation wurden `Datenschutzerklärung`, `Impressum`, `SEO-Audit Showcase: LingQi TCM Head Spa München` und `Startseite` entfernt.
- Die Navigation enthält dort nur noch `Cases`, `Blog` und `Premium-Audit Muster`.

## Was wurde bewusst nicht geändert

- Der Footer mit `Impressum` und `Datenschutzerklärung` wurde nicht entfernt, da die Anweisung sich auf die obere Leiste bezog.
- Keine Texte im Artikel, keine CTAs, keine Assets, keine globalen Styles.
- Kein Commit, kein Push, kein Deploy.

## Offene Fragen für Human Review

- Bitte visuell prüfen, ob die obere Leiste nun genau die gewünschte Linkmenge zeigt.

## Asset- und Lizenzhinweise

- Keine Assets, Bilder, Fonts oder externen Quellen hinzugefügt.

## Lighthouse-Score

- Nicht gemessen, da nur Navigation/Link-Markup geändert wurde.
- Lokale Prüfung: `http://127.0.0.1:8080/blog/google-bewertung-loeschen.html` lieferte HTTP 200.
- Der BGH-Ziellink lieferte HTTP 200.
