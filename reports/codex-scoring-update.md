# Pipeline-v2 Scoring-Update — 2026-05-18 (Gegencheck-Stand)

## Goal
Scoring-System in `docs/pipeline-v2.md` um Kriterium 7 `Brand-Traffic-Abhängigkeit` erweitern, neue Prioritätsbänder einführen, `Pipeline_v2_Qualified` (Google Sheet) entsprechend nachziehen.

## Geänderte Dateien (diese Session)
- `docs/pipeline-v2.md` — Umlaute im neuen Scoring-Abschnitt repariert (ASCII-Fallbacks `Abhaengigkeit`, `ueber`, `Begruendung`, `unterschaetzt`, `Luecke`, `Prioritaet` → richtige Umlaute, konsistent zum Rest der Datei).
- `reports/codex-scoring-update.md` — diese Datei (Verifikations-Report nach Pull).

## Vorgefundene Änderungen aus Codex-Laptop-Run (via git pull)
- `docs/pipeline-v2.md` Abschnitt `Pipeline-v2-Scoring` (Zeilen 141-167) war bereits eingefügt mit:
  - Kriterien 1-7 inkl. Kriterium 7 `Brand-Traffic-Abhängigkeit: +1`
  - Erklärung Kriterium 7 (>80 % Brand-Traffic UND wichtige Service-KW nicht Seite 1)
  - Begründung-Block
  - Prioritätsbänder: Score 6-8 → Pipeline v2 Audit, 4-5 → Variante C, <4 → Nicht kontaktieren
  - Maximaler Score: 8 Punkte
- `reports/codex-pipeline-v2-scoring.md` (zusätzlicher Report aus Laptop-Run).

## Verifikation gegen Auftrag
| Anforderung | Soll | Ist (`docs/pipeline-v2.md`) | Status |
|---|---|---|---|
| Kriterium 7 Brand-Traffic-Abhängigkeit | +1 bei >80 % Brand-Traffic UND Service-KW nicht Seite 1 | Wörtlich umgesetzt | OK |
| Begründung "alte System unterschätzt sie" | Pflicht | Vorhanden | OK |
| Max-Score | 8 Punkte | Zeile 167 | OK |
| Priorität 6-8 | Pipeline v2 Audit | Zeile 163 | OK |
| Priorität 4-5 | Variante C | Zeile 164 | OK |
| Priorität <4 | Nicht kontaktieren | Zeile 165 | OK |
| Umlaut-Konsistenz | Datei nutzt sonst Umlaute (`Realitäts-Check`, `Lücke`) | nach Edit konsistent | OK |

## Pipeline_v2_Qualified (Google Sheet) — nicht angefasst
Pipeline_v2_Qualified ist **kein lokales File** im Repo (Glob `**/Pipeline_v2_Qualified*` → 0 Treffer). Sheet-Updates erfolgen laut `AGENTS.md` ausschließlich über `outreach-cli`. Aus dieser Codex-Session heraus ist kein Schreibzugriff auf das Google Sheet erfolgt.

Der Vorgänger-Report (Laptop-Codex) behauptet einen Schreibvorgang gegen das Sheet (`Neue Spalte BRAND_TRAFFIC als Spalte P angelegt`, Bellapelle-Update). Diese Behauptung lässt sich aus dieser Umgebung nicht verifizieren und sollte vom Menschen im Sheet geprüft werden.

### Empfohlener Sheet-Status (zur manuellen Verifikation/Nacharbeit)
- Neue Spalte `BRAND_TRAFFIC` ergänzen, falls noch nicht vorhanden.
- Bellapelle-Zeile:
  - `BRAND_TRAFFIC` = `JA — 94 % Brand-Traffic; Service-Keywords (Jetpeel Hamburg, Microneedling Hamburg, Dauerhafte Haarentfernung Hamburg) nicht Seite 1`
  - `SCORE_V2` neu berechnen (alter Score + 1)
- Score-5-Leads neu klassifizieren: per neuer Logik → `Variante C` (zuvor evtl. anderes Band).

## Offene Fragen für Human Review
- **Bellapelle Scoring-Widerspruch:** Auftrag nennt „Neuer Score_v2 = 3 → Variante C (oder manuell prüfen)". Score 3 liegt nach neuer Logik unter dem Variante-C-Band (4-5) und fällt damit in „Nicht kontaktieren". Die explizite manuelle Freigabe sticht das Band — Empfehlung: Bellapelle als manuell freigegebenen Sonderfall im Sheet markieren, sonst Logik-Bruch.
- **Sheet-Schreibvorgang verifizieren:** Vorgänger-Report (Laptop) behauptet Spalten-Anlage und Bellapelle-Update im Google Sheet. Bitte im Sheet selbst prüfen, dass der Stand tatsächlich existiert (kein outreach-cli-Run in dieser Session sichtbar).
- **Brand-Traffic-Anteil aller weiteren Leads** ist noch nicht erhoben — Spalte `BRAND_TRAFFIC` für Rest-Leads bleibt `UNGEPRÜFT`, bis Daten aus Ubersuggest/Sistrix vorliegen.

## Was bewusst nicht geändert
- Keine Website-Dateien angefasst.
- Kein Commit, kein Push (gemäß AGENTS.md Git-Sicherheit).
- Keine Werte erfunden — Bellapelle-Brand-Traffic-Wert (94 %) stammt aus dem vorherigen Codex-Run; in dieser Session nicht erneut gemessen.
- Vorgänger-Report `reports/codex-pipeline-v2-scoring.md` nicht überschrieben.

## Asset- und Lizenzhinweise
Keine Assets, Bilder oder Fonts berührt.

## Lighthouse-Score
Nicht relevant (Doku- und Sheet-Vorbereitung, kein Frontend-Change).
