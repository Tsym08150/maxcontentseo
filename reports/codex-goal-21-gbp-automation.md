# Goal 21 — GBP-Automation (2026-05-20)

## Geänderte Dateien

- `tools/places_lookup.ps1`
- `.claude/commands/audit-gbp.md`
- `.gitignore`
- `reports/codex-goal-21-gbp-automation.md`

## Untracked Dateien

- `tools/places_lookup.ps1`
- `.claude/commands/audit-gbp.md`
- `reports/codex-goal-21-gbp-automation.md`

## Was wurde geändert

- `tools/places_lookup.ps1`: Neues additives PowerShell-Modul für Google-Places-Find-Place und Place-Details. Das Skript lädt `$GOOGLE_PLACES_API_KEY` aus `tools/config.ps1`, berechnet den Match-Score nach PLZ, Website-Host, Places-Typen und Name-Token-Overlap und gibt die geforderten `GBP_*`-Felder aus. Es schreibt nicht automatisch ins Sheet.
- `.claude/commands/audit-gbp.md`: Neue separate Command-Datei für Phase 1.4 mit Aufruf, Report-Template, Hook-Triggern und Match-Status-Regeln.
- `.gitignore`: `tools/config.ps1` ergänzt, damit der lokale Google-Places-API-Key nicht versehentlich versioniert wird.

## Was wurde bewusst nicht geändert

- `.claude/commands/audit.md` wurde nicht angefasst.
- `docs/pipeline-v2.md` wurde nicht angefasst.
- `Tools/Firecrawl/firecrawl_score_engine.ps1` wurde nicht angefasst; die Datei existiert im Repo unter dem angegebenen Pfad nicht.
- `tools/config.ps1` wurde nicht neu angelegt, weil die Vorgabe ausdrücklich "nur append" lautete und die Datei im Repo aktuell nicht existiert.
- Es wurde keine automatische Sheet-Schreibung eingebaut.

## Offene Fragen für Human Review

- Soll `tools/config.ps1` lokal neu angelegt werden, obwohl die Goal-Vorgabe nur Append erlaubt? Inhalt wäre: `$GOOGLE_PLACES_API_KEY = "PLACEHOLDER_HIER_EINSETZEN"`.
- Welche drei konkreten Sheet-Leads sollen für den ersten Live-Test verwendet werden?
- Soll das spätere Sheet-Update über `outreach-cli` angebunden werden, damit die Projektregel zu Sheet-Operationen eingehalten bleibt?

## Asset- und Lizenzhinweise

- Keine neuen Bilder, Fonts, Icons oder externen Assets verwendet.
- Neues Skript nutzt nur PowerShell-Bordmittel und Google Places API per HTTPS.

## Lighthouse-Score

- Nicht ausgeführt; Änderung betrifft kein Frontend und keine auslieferbare Website-Performance.
