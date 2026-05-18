# Sammel-Fixes 2 — 2026-05-18

## Geänderte Dateien

- `index.html`
- `audit-beispiel.html`
- `cases.html`
- `cases/index.html`
- `cases/lingqi.html`
- `blog/index.html`
- `blog/google-bewertung-loeschen.html`
- `blog/lingqi-haarausfall.html`
- `branchen/kosmetikstudios.html`
- `danke.html`
- `index-backup-20260515.html`
- `tools/seo-check.html`
- `reports/codex-sammel-fixes-2.md`

## Untracked Dateien

- `reports/codex-sammel-fixes-2.md`

## Was wurde geändert

- Footer-/Datenschutz-Links in HTML-Dateien
  - Impressum-Links auf `/index.html#impressum` vereinheitlicht.
  - Datenschutz-/Datenschutzerklärung-Links auf `/index.html#datenschutz` vereinheitlicht.
- `index.html`
  - Trust-Metriken aktualisiert:
    - `1` / `Referenz veröffentlicht` / `LingQi TCM München`
    - `ab 499€` / `Audit-Einstieg` / `Ohne Agentur-Vertrag`
    - `48h` / `Analyse-Lieferzeit` / `Kein Verkaufsgespräch`
  - Quick-Fix-Hinweis auf `Nach dem Premium-Audit optional: Quick Fix — Umsetzung der Top-3-Hebel für 699€.` geändert.
  - Proof-Points unter den Hero-CTAs auf `font-size: 14px`, `font-weight: 500` und `color: var(--color-text-primary, var(--text))` gesetzt.

## Was wurde bewusst nicht geändert

- Keine Inhalte außerhalb der genannten Link-, Trust-, Quick-Fix- und Proof-Point-Anpassungen umformuliert.
- Keine externen Assets, Fonts, Skripte oder Build-Schritte hinzugefügt.
- Kein Commit, kein Push, kein Deployment.

## Offene Fragen für Human Review

- Keine.

## Asset- und Lizenzhinweise

- Keine neuen Assets verwendet.

## Lighthouse-Score

- Nicht neu gemessen, da nur Text-, Link- und kleine CSS-Anpassungen vorgenommen wurden.
- Lokale Link-Prüfung über interne HTML-Links: `TOTAL_BROKEN=0`.
- Browser-Prüfung der Startseite: Pflichttexte vorhanden, Proof-Points rendern mit `14px` und `font-weight: 500`, Console-Logs für `error`/`warn` waren leer.
