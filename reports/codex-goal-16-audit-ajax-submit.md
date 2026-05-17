# Goal 16 - Audit-Formular AJAX-Submit

Datum: 2026-05-18

## Geänderte Dateien

- `audit-beispiel.html`
- `reports/codex-goal-16-audit-ajax-submit.md`

## Untracked Dateien

- `reports/codex-goal-16-audit-ajax-submit.md`

## Was wurde geändert

- `audit-beispiel.html`
  - Formular-ID von `formular` auf `audit-form` geändert.
  - CTA-Anker von `#formular` auf `#audit-form` angepasst, damit der Sprung zur Formularstelle weiter funktioniert.
  - Hidden Field `_next` entfernt.
  - AJAX-Submit per `fetch` direkt vor `</body>` eingefügt.
  - Erfolgsfall leitet auf `/danke.html` weiter.
  - Fehlerfall zeigt die gewünschte Fehlermeldung per `alert`.

## Was wurde bewusst nicht geändert

- Formularfelder, Button-Text und Formspree-Endpoint blieben unverändert.
- Keine externen Fonts, Bilder oder Assets hinzugefügt.
- Kein Git-Commit und kein Push.

## Offene Fragen für Human Review

- Bitte nach Deployment einmal testen, ob Formspree die AJAX-Anfrage akzeptiert und die Weiterleitung auf `/danke.html` greift.

## Asset- und Lizenzhinweise

- Keine neuen Assets.
- Keine externen Fonts.

## Lighthouse-Score

- Nicht gemessen, da nur das Formular-Submit-Verhalten geändert wurde.
