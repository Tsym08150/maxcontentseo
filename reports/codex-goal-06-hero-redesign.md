# Goal 06 — Hero-Redesign, 15.05.2026

## Geänderte Dateien
- `index.html`
- `reports/codex-goal-06-hero-redesign.md`

## Untracked Dateien
- `reports/codex-goal-06-hero-redesign.md`
- `assets/georg.jpg.png` (vorhandenes Nutzer-Asset, nicht von Codex angelegt)

## Was wurde geändert
- Hero auf zweispaltige Struktur umgebaut: links Eyebrow-Badge, H1, Subheadline und CTAs; rechts `.hero-photo`.
- Vorhandenes lokales Asset `assets/georg.jpg.png` als Hero-Bild eingebunden.
- Inline-SVG-Blob hinter dem Hero-Bildcontainer ergänzt, mit Akzentfarbe und `20%` Opacity.
- Primären CTA auf „Kostenlose Potenzialanalyse“ geändert.
- Sekundären CTA als dezenter Textlink „Fallstudie ansehen“ auf `#resultate` umgesetzt.
- Logo-Leiste „Bereits vertraut von:“ mit drei neutralen SVG-Platzhaltern unter dem Hero ergänzt.
- Logo-Platzhalter auf `120px × 40px` gesetzt.
- Mobile-Regel auf `< 768px` angepasst: Bild steht unter dem Text, Blob skaliert kleiner.
- Externe Google-Font-Links entfernt und vorhandene Font-Variablen auf System-Fonts umgestellt.

## Was wurde bewusst nicht geändert
- Keine echten Kundenlogos oder Stockfotos ergänzt.
- Keine neuen Frameworks, kein NPM, kein JavaScript.
- Bestehende Farbvariablen und Palette wurden beibehalten.
- Sektionen unterhalb der neuen Logo-Leiste wurden inhaltlich nicht umgeschrieben.

## Offene Fragen für Human Review
- Soll das Asset später von `assets/georg.jpg.png` in `assets/georg.jpg` umbenannt werden?
- Soll die Navigation später ebenfalls von „Kostenlose SEO-Erstanalyse“ auf „Kostenlose Potenzialanalyse“ umgestellt werden?
- Die Logo-Leiste enthält bewusst Platzhalter. Echte Logos sollten erst ergänzt werden, wenn Freigabe und Nutzungsrechte geklärt sind.

## Asset- und Lizenzhinweise
- Keine externen Fonts.
- Lokales Bildasset `assets/georg.jpg.png` verwendet.
- Keine externen Bilder.
- SVGs sind inline und als neutrale Platzhalter erstellt.

## Lighthouse-Score
- Nicht erneut gemessen.
- Stattdessen visuelle Playwright-QA mit lokalem HTTP-Server durchgeführt.
- Desktop `1440px`: Hero-Bild lädt, Logo-Platzhalter sind jeweils `120px × 40px`, keine Console-Errors, kein horizontaler Overflow.
- Mobile `375px`: Bild steht unter der Textspalte, Hero-Bild lädt, kein horizontaler Overflow.
- Performance-Risiko reduziert, da externe Google-Font-Requests entfernt wurden.
