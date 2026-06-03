# Codex Goal: URL-Felder in Formularen normalisieren

Datum: 2026-06-03

## Geänderte Dateien
- index.html
- ki-sichtbarkeits-check/index.html
- tools/seo-check.html
- index-backup-20260515.html

## Untracked Dateien
- reports/codex-goal-url-normalize-form-fields.md

## Was wurde geändert
- Website-/URL-Felder von `type="url"` auf `type="text"` umgestellt.
- `inputmode="url"`, `data-url-normalize="1"` und den einheitlichen Placeholder `z. B. www.ihr-studio.de` ergänzt.
- Required/optional-Status unverändert gelassen.
- Pro betroffener Seite ein Submit-Script ergänzt, das vor dem Absenden `https://` ergänzt, wenn kein Schema vorhanden ist.

## Was wurde bewusst nicht geändert
- `audit-beispiel.html` und `cases/lingqi.html`: kein Website-/Homepage-Eingabefeld im aktuellen Stand.
- Honeypot `company_url` auf der KI-Check-Seite bleibt unverändert und wird nicht normalisiert.

## Tests
- Repo-Scan: kein verbleibendes `type="url"` in HTML-Dateien gefunden.
- Browser-Test mit Playwright gegen lokalen Server:
  - `index.html` Formular: `www.studio.de` validiert und wird als `https://www.studio.de` gesendet.
  - `ki-sichtbarkeits-check/index.html` Formular: `www.studio.de` validiert und wird als `https://www.studio.de` gesendet.
  - `tools/seo-check.html` Leadformular: `www.studio.de` validiert und wird als `https://www.studio.de` gesendet.
- Formspree-Requests wurden zuerst im Browser abgefangen, um den ausgehenden Payload auf `https://www.studio.de` zu prüfen.
- Zusätzlich echte Test-Submissions an Formspree mit klaren Testdaten:
  - `index.html`: Formspree-Response `302` (Redirect nach Danke-Seite).
  - `ki-sichtbarkeits-check/index.html`: Formspree-Response `302` (Redirect nach Danke-Seite).
  - `tools/seo-check.html`: Formspree-Response `200` per Fetch.

## Asset- und Lizenzhinweise
- Keine neuen Assets, Fonts oder externen Scripts.

## Lighthouse-Score
- Nicht gemessen. Änderung betrifft Formular-Markup und ein kleines Inline-Script.
