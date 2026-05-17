# Goal 13 - PDF V17 Pricing-Tabelle

Datum: 2026-05-17

## Geänderte Dateien

- `tools/generate_seo_audit_showcase_v17.js`
- `qa_output/seo_audit_showcase_v17.html`
- `qa_output/qa_report_v17.md`
- `qa_output/v17_qa_report.md`
- `qa_output/v17_extracted_text.txt`
- `qa_output/v17_contactsheet.png`
- `qa_output/v17_pages/page-01.png` bis `qa_output/v17_pages/page-10.png`
- `reports/codex-goal-13-pdf-v17-pricing.md`

## Untracked Dateien

- `tools/generate_seo_audit_showcase_v17.js`
- `qa_output/seo_audit_showcase_v17.html`
- `qa_output/qa_report_v17.md`
- `qa_output/v17_pages/`
- `qa_output/v17_contactsheet.png`
- `qa_output/v17_extracted_text.txt`
- `qa_output/v17_qa_report.md`
- `reports/codex-goal-13-pdf-v17-pricing.md`

## Was wurde geändert

- Neue V17-PDF erzeugt: `C:\Users\MaxContentSeO\Downloads\SEO_Audit_Showcase_v17.pdf`
- Nur die Pricing-Tabelle in Kapitel 11 auf Seite 10 geändert:
  - `Premium-Audit + Quick Fix` getrennt in `Premium-Audit` und `Quick Fix`.
  - `Premium-Audit` auf `1.290 EUR einmalig` gesetzt.
  - `Quick Fix` auf `690 EUR einmalig` gesetzt.
  - `SEO Wachstumspaket` und `Premium SEO` unverändert belassen.
  - Fußnote zur Anrechnung vollständig entfernt.

## Was wurde bewusst nicht geändert

- Keine anderen Inhalte, Tabellen, Layoutbereiche oder fachlichen Aussagen verändert.
- V16-Layout, HTML/CSS-Pipeline und Seitenstruktur beibehalten.
- Kein Commit, Push oder Deployment ausgeführt.

## Offene Fragen für Human Review

- Bitte finale Preislogik auf Seite 10 fachlich freigeben.

## Asset- und Lizenzhinweise

- Keine neuen Assets.
- Keine externen Fonts.

## Lighthouse-Score

- Nicht relevant, da ausschließlich ein lokal erzeugtes PDF betroffen ist.

## Prüfungen

- V17 per HTML/CSS + Chromium/Playwright erzeugt.
- PDF mit `tools/pdf_qa.py` als PNG gerendert.
- Seite 10 visuell geprüft.
- Textprüfung: alte Fragmente `Premium-Audit + Quick Fix`, `490 EUR (Audit)`, `200 EUR Umsetzung`, `Audit-Betrag` und `Effektiver Gesamtpreis` sind nicht mehr enthalten.
- Textprüfung: neue Preise `1.290 EUR einmalig` und `690 EUR einmalig` sind enthalten.
