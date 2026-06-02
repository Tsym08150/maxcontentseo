# Codex Hotfix Mai 18 — 2026-05-18

## Geänderte Dateien

- `index.html`
- `index-backup-20260515.html`
- `reports/codex-hotfix-mai18.md`

## Untracked Dateien

- `reports/codex-hotfix-mai18.md`

## Was wurde geändert

- `index.html`
  - Kontaktformular im Abschnitt `#kontakt` auf Formspree gesetzt: `action="https://formspree.io/f/mqenpryl"` und `method="POST"`.
  - Hidden Fields für `_subject` und `_next` ergänzt.
  - Adresse im Impressum und Datenschutz auf `85551 Kirchheim b. München` umgestellt.
  - Impressum-Accordion geschlossen gesetzt, indem `open` entfernt wurde. Datenschutz war bereits geschlossen.
  - Sektion `Bereits vertraut von` inklusive Platzhalter-Logos entfernt.
  - Pricing-Karte 1 auf `Premium-Audit` mit 490€ Referenzaktion und den gewünschten Leistungsdetails geändert.
  - Quick-Fix-Hinweis unter den Pricing-Karten ergänzt.
- `index-backup-20260515.html`
  - Alte Ortsangabe in den dort vorhandenen Legal-Texten auf `Kirchheim b. München` umgestellt.
  - Alte `Bereits vertraut von`-Logo-Platzhaltersektion entfernt.
- `reports/codex-hotfix-mai18.md`
  - Dieser Run-Report wurde neu angelegt.

## Was wurde bewusst nicht geändert

- `audit-beispiel.html` wurde nicht angefasst. Die dortige Formspree-Form blieb unverändert.
- Die Google-Bewertung-Blog-Card in `index.html` bekam noch kein Bild, weil in `assets/` kein `google-bewertung-loeschen.png` und kein anderes erkennbares Bild für diesen Artikel vorhanden ist. Ein kaputtes Bild oder ein externes Asset wurde bewusst nicht eingebaut.
- CSS-Regeln für die entfernte Logo-Leiste wurden nicht entfernt, um keine zusätzlichen globalen Style-Änderungen in diesem Hotfix zu machen.

## Offene Fragen für Human Review

- Bitte das freigegebene Bild für den Artikel `Google Bewertung löschen` unter `assets/` ablegen, z. B. `assets/google-bewertung-loeschen.png`. Danach kann die Card in `index.html` mit `<img src="/assets/google-bewertung-loeschen.png" alt="Google Bewertung löschen Kosmetikstudio">` ergänzt werden.

## Asset- und Lizenzhinweise

- Keine neuen Bilder, Fonts, Icons oder externen Assets eingebunden.
- Kein externes Bild für die Google-Bewertung-Card verwendet, da kein passendes Repo-Asset vorhanden war.
- Bestehende System-Fonts und vorhandene Assets bleiben unverändert.

## Lighthouse-Score

- Nicht gemessen. Die Änderungen sind statische HTML-Text-/Markup-Anpassungen ohne neue externe Ressourcen oder Build-Step.

## Checks

- `git pull origin main`: `Already up to date`.
- `rg -n "Drogen|Schmölln|04626" -g "*.html"`: keine Treffer.
- Kontaktformular in `index.html` enthält Formspree-Action, `method="POST"`, `_subject` und `_next`.
- `audit-beispiel.html` enthält weiterhin nur die bestehende Audit-Form; keine neuen Hidden Fields ergänzt.
