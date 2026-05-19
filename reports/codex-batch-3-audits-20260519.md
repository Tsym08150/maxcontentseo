# Codex Batch Report: 3 Audits

Datum: 2026-05-19

## Goal

Pipeline v2 Batch mit drei Audits:

1. `hautkultur.de` - Hamburg-Harvestehude
2. `babor-uhlenhorst.de` - Hamburg-Uhlenhorst
3. `studiombogenhausen.com` - Muenchen-Bogenhausen

## Geaenderte Dateien

- `reports/audit-hautkultur-de-20260519.md`
- `reports/outreach-hautkultur-de-20260519.txt`
- `reports/codex-audit-hautkultur-de.md`
- `reports/audit-babor-uhlenhorst-de-20260519.md`
- `reports/outreach-babor-uhlenhorst-de-20260519.txt`
- `reports/codex-audit-babor-uhlenhorst-de.md`
- `reports/audit-studiombogenhausen-com-20260519.md`
- `reports/outreach-studiombogenhausen-com-20260519.txt`
- `reports/codex-audit-studiombogenhausen-com.md`
- `reports/codex-batch-3-audits-20260519.md`

## Untracked Dateien

- `reports/codex-audit-hautkultur-de.md`
- `reports/codex-audit-babor-uhlenhorst-de.md`
- `reports/codex-audit-studiombogenhausen-com.md`
- `reports/codex-batch-3-audits-20260519.md`

Zusaetzlich war `reports/codex-vitaminbude-verify.md` bereits vor diesem Batch untracked.

Hinweis: Die `audit-*.md`- und `outreach-*.txt`-Dateien wurden angelegt, sind aber durch `.gitignore` ignoriert.

## Was wurde geaendert

- Drei lokale Stufe-1-Audits erstellt.
- Pro Lead Ubersuggest, Firecrawl, Sistrix, Redirect, Index-Check und Website-Befunde ausgewertet.
- Pro Lead Outreach-Datei erstellt.
- Pro Lead eigener Codex-Report erstellt.

## Was wurde bewusst nicht geaendert

- Keine Website-Dateien.
- Keine Assets.
- Keine GitHub-, DNS-, Hosting- oder Deployment-Dateien.
- Kein Commit und kein Push. Grund: AGENTS.md verbietet Codex ausdruecklich Commits und Pushes.

## Tool- und Datenhinweise

- Ubersuggest: erfolgreich fuer alle drei Input-Domains.
- Firecrawl: erfolgreich fuer Website-Crawls und `site:`-Search.
- Sistrix: erfolgreich ueber Sistrix-Free-Tool via Firecrawl Scrape.
- PageSpeed: nicht verfuegbar, API antwortete mit HTTP 429 / Quota exceeded.

## Kurzwerte

| Domain | DA | Traffic | Keywords | Sistrix SI | Hook-Profil |
|---|---:|---:|---:|---:|---|
| hautkultur.de | 20 | 761 | 190 | 0,0136 | B |
| babor-uhlenhorst.de | 1 | 0 | 0 | 0,0000 | A |
| studiombogenhausen.com | 5 | 13 | 33 | 0,0000 | A |

## Offene Fragen fuer Human Review

- Darf der Mensch trotz Projektregel manuell committen und pushen? Codex hat es nicht getan.
- Soll fuer `babor-uhlenhorst.de` die alte Domain oder die aktive Hauptdomain kontaktiert werden?
- Bei HautKultur ist der Lead nicht schwach, sondern eher Profil B. Outreach bitte besonders kritisch pruefen.
- Bei Studio M und HautKultur Medical-Beauty-/HWG-Wording vor Verwendung vorsichtig pruefen.

## Asset- und Lizenzhinweise

Keine Assets verwendet.

## Lighthouse-Score

Nicht erhoben, da PageSpeed API quota-blockiert war. Keine Performance-relevanten Website-Dateien geaendert.
