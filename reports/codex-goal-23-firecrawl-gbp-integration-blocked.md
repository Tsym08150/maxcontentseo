# Goal 23 — Firecrawl-GBP-Integration (blocked, 2026-05-20)

## Geaenderte Dateien

- `reports/codex-goal-23-firecrawl-gbp-integration-blocked.md`

## Untracked Dateien

- `reports/codex-goal-23-firecrawl-gbp-integration-blocked.md`

## Was wurde geaendert

- Kein Produktivcode geaendert.
- Dieser Report dokumentiert den Blocker: `firecrawl_score_engine.ps1` ist lokal nicht vorhanden.

## Was wurde bewusst nicht geaendert

- `.claude/commands/audit.md` wurde nicht angefasst.
- `tools/places_lookup.ps1` wurde nicht angefasst.
- `tools/places_lookup_from_impressum.ps1` wurde nicht angefasst.
- Es wurde keine neue `firecrawl_score_engine.ps1` erfunden, weil die Aufgabe eine minimale Ergaenzung der bestehenden Datei verlangt.
- Es wurde kein Sheet-Write ausgefuehrt.

## Analyse

- `Tools/Firecrawl/firecrawl_score_engine.ps1` beziehungsweise `tools/Firecrawl/firecrawl_score_engine.ps1` existiert im Repo nicht.
- Eine Suche unter `C:\Users\MaxContentSeO` und `D:\` fand keine Datei mit dem Namen `firecrawl_score_engine.ps1`.
- Daher kann nicht festgestellt werden:
  - wie der bestehende Flow den Impressum-Scrape weitergibt,
  - welche Variable den Impressum-Markdown enthaelt,
  - wo der bestehende Sheet-Row-Write sitzt,
  - wie GBP-Felder minimal an denselben Write angehaengt werden sollen.

## Offene Fragen fuer Human Review

- Bitte die bestehende `firecrawl_score_engine.ps1` bereitstellen oder den korrekten Pfad nennen.
- Sobald die Datei vorhanden ist, kann die Integration minimal an der Stelle nach dem Impressum-Scrape erfolgen:
  - Impressum-Markdown in eine temporaere UTF-8-Datei schreiben oder an einen Wrapper uebergeben,
  - `places_lookup_from_impressum.ps1` mit Studioname, Stadt, Domain und Impressum-Scrape aufrufen,
  - `GBP_*`-Felder an den bestehenden Row-Payload anhaengen,
  - GBP-Fehler abfangen, ohne den Firecrawl-Write abzubrechen.

## Asset- und Lizenzhinweise

- Keine neuen Assets, Schriften, Bilder oder externen Dateien verwendet.

## Lighthouse-Score

- Nicht ausgefuehrt; keine Frontend-Aenderung.
