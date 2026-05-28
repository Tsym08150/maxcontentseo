# Goal: LingQi-Bild in Cases-Übersicht vollständig anzeigen

Datum: 2026-05-28

## Geänderte Dateien

- `cases/index.html`

## Untracked Dateien

- `reports/codex-goal-29-cases-lingqi-image-crop.md`

Bereits vor diesem Run untracked vorhanden und nicht angefasst:

- `reports/codex-goal-27-frankfurt-umland-handover-blocked.md`
- `reports/codex-goal-27v2-frankfurt-umland-bundle-missing.md`
- `reports/codex-goal-27v2-frankfurt-umland-precheck-unavailable.md`

## Was wurde geändert

- Das LingQi-Bild in der Cases-Übersicht bekam eine eigene CSS-Klasse.
- Das Bild wird jetzt vollständig im natürlichen Seitenverhältnis angezeigt.
- Die Schrift im unteren Bereich des Bild-Assets bleibt dadurch vollständig lesbar.

## Was wurde bewusst nicht geändert

- Keine Texte wurden geändert.
- Kein neues Bild wurde eingebunden.
- Das bestehende Bild-Asset wurde nicht bearbeitet.
- Die zweite Case-Karte und globale Kartenstile wurden nicht verändert.

## Offene Fragen für Human Review

- Keine.

## Asset- und Lizenzhinweise

- Es wurden keine neuen Assets verwendet. Das bestehende lokale Asset `assets/lingqi-foto.webp` bleibt unverändert.

## Lighthouse-Score

- Nicht gemessen. Die Änderung betrifft nur Größe und Zuschnitt eines bestehenden Bildes.

## Prüfung

- Lokaler Server: `http://127.0.0.1:8087/cases/`
- Browser-Prüfung: Das LingQi-Bild misst lokal `256x457` Pixel im Viewport, verwendet `object-fit: contain` und `aspect-ratio: auto`. Die Schrift aus dem unteren Bildbereich ist vollständig sichtbar.
