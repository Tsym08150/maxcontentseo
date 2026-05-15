# Goal Rebuild V1 — 15.05.2026

## 1. Goal-Bezeichnung und Datum
- Vollständiger Neuaufbau von `index.html` bei Erhalt der bestehenden Site-Inhalte
- Datum: 15.05.2026

## 2. Geänderte Dateien
- `D:\AITools\maxcontentseo\index.html`
- `D:\AITools\maxcontentseo\index-backup-20260515.html`

## 3. Untracked Dateien
- `D:\AITools\maxcontentseo\reports\codex-goal-rebuild-v1.md`

## 4. Was wurde geändert
- `index-backup-20260515.html`
  - Bestehende Startseite per `git mv` gesichert, bevor die neue Fassung geschrieben wurde.
- `index.html`
  - HTML- und CSS-Struktur von Grund auf neu aufgebaut.
  - Neue Seitenreihenfolge umgesetzt: Nav, Hero, Logo-Strip, Trust-Metriken, Problems, Solution, Process, Case Study, Pricing, FAQ, Kontakt, Impressum/Datenschutz, Footer.
  - Hero mit 2-Spalten-Grid, Blob-SVG, Foto `/assets/georg.jpg`, Metrik-Ankern und maximalem Whitespace neu aufgebaut.
  - Trust-/Problem-/Solution-/Process-/Pricing-Bereiche als neue Card-Systeme umgesetzt.
  - LingQi-Case-Study visuell neu strukturiert, inklusive Metrik-Cards, Ausgangssituation/Ergebnis-Trennung und Vorgehensliste.
  - FAQ auf Accordion mit plain JavaScript umgestellt.
  - Kontaktbereich als grüne CTA-Sektion mit Formular ohne `action`-Attribut neu gebaut.
  - Impressum und Datenschutz auf `details/summary` umgestellt.
- `reports/codex-goal-rebuild-v1.md`
  - Pflichtreport für diesen Run angelegt.

## 5. Was wurde bewusst nicht geändert
- Keine externen Fonts, keine externen Bilder, keine Frameworks, keine CDN-Skripte.
- Keine neuen Testimonials, keine neuen Logos, keine neuen Case-Zahlen.
- Keine zusätzlichen Seiten oder Build-Tools.

## 6. Offene Fragen für Human Review
- Im Repo liegt keine originale LingQi-Kundenstimme vor. Die gewünschte Quote wurde deshalb bewusst nicht erfunden und durch einen Projekt-Hinweis ersetzt.
- Der Pricing-Block verwendet den von Georg im aktuellen Brief bestätigten Wert `490€ einmalig` für das Audit.
- Lighthouse wurde in diesem Run nicht gemessen.

## 7. Asset- und Lizenzhinweise
- Schrift: nur System-Stacks (`Georgia`, `Times New Roman`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `sans-serif`)
- Bild: lokales Asset `D:\AITools\maxcontentseo\assets\georg.jpg`
- Logos: nur inline SVG-Platzhalter, keine Fremdlogos

## 8. Lighthouse-Score
- Nicht gemessen in diesem Run

## Gebaute Sektionen
- Fixed Nav mit CTA
- Hero mit 2-Spalten-Layout, Blob, Foto und Metrik-Ankern
- Logo-Strip
- Trust-Metriken
- Problems Grid
- Solution Grid
- Process
- LingQi Case Study
- Pricing
- FAQ Accordion
- CTA-Final mit Formular
- Impressum + Datenschutz
- Footer

## Bekannte Einschränkungen
- Keine originale LingQi-Quote im Repo vorhanden
- Keine Lighthouse-Messung im Rahmen dieses Runs

## Screenshots
- Desktop: `C:\Users\MaxContentSeO\maxcontentseo-codex-assets\outputs\rebuild-home-desktop.png`
- Mobile: `C:\Users\MaxContentSeO\maxcontentseo-codex-assets\outputs\rebuild-home-mobile.png`
