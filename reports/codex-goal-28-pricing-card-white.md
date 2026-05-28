# Goal: Preis-Karte "Kostenlose Erstanalyse" auf weißen Hintergrund setzen

Datum: 2026-05-28

## Geänderte Dateien

- `index.html`

## Untracked Dateien

- `reports/codex-goal-28-pricing-card-white.md`

Bereits vor diesem Run untracked vorhanden und nicht angefasst:

- `reports/codex-goal-27-frankfurt-umland-handover-blocked.md`
- `reports/codex-goal-27v2-frankfurt-umland-bundle-missing.md`
- `reports/codex-goal-27v2-frankfurt-umland-precheck-unavailable.md`

## Was wurde geändert

- In `index.html` wurde die CSS-Regel `.pricing-card--secondary` von `background: var(--bg-alt);` auf `background: var(--white);` geändert.
- Dadurch hat die Karte "Kostenlose Erstanalyse" in der Sektion "Einmaliger Einstieg" denselben weißen Hintergrund wie die anderen Preis-Karten.

## Was wurde bewusst nicht geändert

- Keine Texte wurden geändert.
- Keine Layout-Struktur wurde geändert.
- Keine anderen Preis-Karten, Buttons oder globalen Theme-Werte wurden angepasst.

## Offene Fragen für Human Review

- Keine.

## Asset- und Lizenzhinweise

- Keine neuen Bilder, Icons, Fonts oder externen Assets verwendet.

## Lighthouse-Score

- Nicht gemessen. Die Änderung betrifft nur eine einzelne CSS-Farbzuweisung und ist nicht performance-relevant.

## Prüfung

- Lokaler Server: `http://127.0.0.1:8087/`
- Browser-Prüfung: Die drei Karten unter "Einmaliger Einstieg" haben nach Reload jeweils `rgb(255, 255, 255)` als berechneten Hintergrund.
