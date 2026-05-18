# Pipeline v2 Scoring - 2026-05-18

## Goal
Neues Google-Sheet-Tab `Pipeline_v2_Qualified` im bestehenden Sheet `Lead_Tracker_Gesamt` anlegen und den Test-Batch mit Pipeline-v2-Scoring eintragen.

## Geaenderte Dateien
- `reports/codex-pipeline-v2-scoring.md`

## Untracked Dateien
- `reports/codex-pipeline-v2-scoring.md`

## Sheet-Aenderung
- Neues Tab `Pipeline_v2_Qualified` per Apps-Script-Webhook angelegt.
- Header-Zeile gemaess Vorgabe gesetzt.
- 13 Test-Leads eingetragen.
- Readback aus Google Sheets erfolgreich: Bereich `Pipeline_v2_Qualified!A1:O14`.

## Datenquellen und Methodik
- `AGENTS.md` gelesen.
- `git pull origin main` ausgefuehrt: Repository war bereits aktuell.
- Ubersuggest: DA und organischer Traffic je Domain.
- Firecrawl CLI: je Domain bis zu 8 Seiten gecrawlt, Blog-Hinweis und technische Auffaelligkeiten ausgewertet.
- SERP-/Ranking-Schwach-Signal: Ubersuggest-Keyworddaten plus Live-SERP-Checks aus der laufenden Pipeline-Recherche.
- GMB-Schwach-Signal: nur als `JA` gewertet, wenn Review-Anzahl oder Sterne oeffentlich belegbar unter der Schwelle lagen. Nicht sicher belegte Faelle sind im Sheet als `UNGEPRUEFT` markiert und nicht als Pluspunkt gezaehlt.

## Firecrawl-Score-Hinweis
Der Firecrawl-CLI gibt keinen nativen numerischen Crawl-Score aus. Fuer `FIRECRAWL_SCORE` wurde deshalb eine transparente Heuristik genutzt:

`100 - 20 Punkte pro fehlgeschlagener Seite - 5 Punkte pro fehlendem Title/Meta/H1 im Sample`, Minimum 0.

Damit wird die Regel "Technische Fehler bei Crawl <60" nachvollziehbar anwendbar.

## Eingetragene Empfehlungen
- `Pipeline v2 Audit`: Carries Cosmetic, D&E Elixier, Esthetic Center Nordend, Green Mama Bio Spa, Beyond Skincare, SecretSkin
- `Variante C`: Medicosmet, Medeia Praxis, Hautgefuehl, NARGIS, Hautsache Schoen
- `Nicht kontaktieren`: Bellapelle, HautKultur GmbH

## Was wurde bewusst nicht geaendert
- Keine Website-Dateien geaendert.
- Kein Commit, kein Push.
- Kein bestehendes Lead-Tab ueberschrieben.

## Offene Fragen fuer Human Review
- GMB-Daten bei D&E Elixier, SecretSkin, NARGIS und Hautsache Schoen sollten vor Live-Outreach manuell in Google Maps final gegengeprueft werden.
- Bei Bellapelle und HautKultur ist das Pipeline-v2-Scoring niedrig, obwohl einzelne SEO-Chancen existieren. Vor erneuter Ansprache besser strategisch entscheiden.

## Asset- und Lizenzhinweise
- Keine Assets, Bilder oder Fonts verwendet.

## Lighthouse-Score
- Nicht relevant, keine Website-Performance-Aenderung.
