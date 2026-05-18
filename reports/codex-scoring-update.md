# Pipeline-v2 Scoring-Update - 2026-05-18

## Goal
Scoring-System in `docs/pipeline-v2.md` um Kriterium 7 `Brand-Traffic-Abhaengigkeit` erweitern und `Pipeline_v2_Qualified` im Google Sheet aktualisieren.

## Geaenderte Dateien
- `docs/pipeline-v2.md`
- `reports/codex-scoring-update.md`

## Untracked Dateien
- `reports/codex-scoring-update.md`

## Was wurde geaendert
- `docs/pipeline-v2.md`: Neuer Abschnitt `Pipeline-v2-Scoring` ergaenzt.
- `docs/pipeline-v2.md`: Kriterium 7 `Brand-Traffic-Abhaengigkeit` dokumentiert.
- `docs/pipeline-v2.md`: Maximaler Score auf 8 Punkte gesetzt.
- `docs/pipeline-v2.md`: Prioritaeten angepasst:
  - Score 6-8: Pipeline v2 Audit
  - Score 4-5: Variante C
  - Score < 4: Nicht kontaktieren
- Google Sheet `Pipeline_v2_Qualified`: Neue Spalte `BRAND_TRAFFIC` als Spalte P angelegt.
- Google Sheet `Pipeline_v2_Qualified`: Bellapelle aktualisiert:
  - `BRAND_TRAFFIC`: `JA - 94% Brand-Traffic; Service-Keywords nicht Seite 1`
  - `SCORE_V2`: `3`
  - `AUDIT_EMPFEHLUNG`: `Variante C (manuell pruefen)`
- Google Sheet `Pipeline_v2_Qualified`: Bestehende Score-5-Zeilen auf die neue Prioritaetslogik `Variante C` angepasst.

## Was wurde bewusst nicht geaendert
- Keine Website-Dateien geaendert.
- Kein Commit, kein Push.
- Keine weiteren Brand-Traffic-Werte erfunden; alle nicht belegten Leads stehen in der neuen Spalte auf `UNGEPRUEFT`.

## Offene Fragen fuer Human Review
- Bellapelle ist nach numerischer Logik mit Score 3 eigentlich unterhalb der neuen Variante-C-Schwelle. Die Sheet-Empfehlung wurde gemaess Auftrag als manuelle Pruefung auf `Variante C (manuell pruefen)` gesetzt.
- Brand-Traffic-Anteile fuer die restlichen Leads sollten bei Bedarf separat nachgezogen werden.

## Asset- und Lizenzhinweise
- Keine Assets, Bilder oder Fonts verwendet.

## Lighthouse-Score
- Nicht relevant, keine Website-Performance-Aenderung.
