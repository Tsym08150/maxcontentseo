---
description: Phase 1.4 — GBP Resolution & Pull (optional, additiv)
---

# Phase 1.4 — GBP Resolution & Pull (optional, additiv)

Diese Phase wird nach Phase 1 (Firecrawl/Ubersuggest/Sistrix) und vor Phase 1.5 geladen.
Sie ist additiv: bestehende Audit-Schritte bleiben unverändert.

## Aufruf

Wenn ein Impressum-Scrape aus Phase 1 vorhanden ist, zuerst die PLZ aus dem Scrape ziehen und dann den Lookup ausführen:

```powershell
.\tools\places_lookup_from_impressum.ps1 -StudioName "<Studioname>" -Stadt "<Stadt>" -Domain "<Domain>" -ImpressumScrapePath "reports/_stage1_scrape/impressum/<domain>.md" -AsJson
```

Direktaufruf, wenn die PLZ schon bekannt ist oder leer bleiben soll:

```powershell
.\tools\places_lookup.ps1 -StudioName "<Studioname>" -Stadt "<Stadt>" -Domain "<Domain>" -PLZ "<PLZ>" -AsJson
```

Parameter:
- `StudioName`: Studioname aus dem Sheet
- `Stadt`: Stadt aus dem Sheet
- `Domain`: Domain aus dem Sheet oder Audit-Input
- `PLZ`: optional, aus dem Impressum-Scrape extrahiert; leer erlaubt

Das Skript schreibt beim ersten Test nicht automatisch ins Sheet. Die Ausgabe liefert die Spaltengruppe `GBP_*` für eine spätere manuelle Sichtprüfung.

## Report-Template

Wenn GBP-Daten vorhanden sind, diesen Block in den Audit-MD einfügen:

```markdown
## Google Business Profile (Places API)

| Metrik | Wert | Status |
|---|---|---|
| GBP gefunden | [PLACE_ID] | [✅/⚠️/❌] Match-Score [X]/9 |
| Status | [OPERATIONAL/CLOSED] | [✅/❌] |
| Rating | [X.X] ([N] Bewertungen) | [✅ stark / ⚠️ schwach / ❌ kritisch] |
| Primäre Kategorie | [category] | [✅/⚠️] |
| NAP-Konsistenz | [identisch/Konflikt] | [✅/❌] |
| Öffnungszeiten gepflegt | [ja/nein] | [✅/❌] |
| Maps-URL | [URL] | — |

Hook-Tauglichkeit: [ja/nein] — Begründung in 1 Satz.
```

## Schwellenwerte für Hook-Trigger

- `rating < 4.0` → Hook-kandidat (impact +2)
- `user_ratings_total < 15` → Hook-kandidat (impact +1)
- `NAP-Konflikt` → Hook-kandidat (impact +2)
- `business_status != OPERATIONAL` → Hook-kandidat (impact +3)

## Match-Status

- `GBP_MATCH_SCORE >= 6`: high-confidence, Daten können im Audit verwendet werden.
- `GBP_MATCH_SCORE 4-5`: `NEEDS_REVIEW`, Maps-URL prüfen, Felder im Audit leer lassen.
- `GBP_MATCH_SCORE < 4`: `NOT_FOUND`, nicht als eindeutigen Treffer verwenden.
- API-Fehler: `API_ERROR`, Audit nicht abbrechen.
