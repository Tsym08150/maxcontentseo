# Domain Audit Skill Design

**Date:** 2026-05-12
**Location:** `.claude/skills/audit.md`
**Trigger:** `/audit <domain>` or "audit domain X"

## Purpose

Kombiniert Ubersuggest MCP (Off-Page SEO) und Firecrawl CLI (On-Page Crawl) zu einem agent-nativen Domain-Audit für Outreach-Vorbereitung.

## Pipeline

Parallel-Calls in einer Tool-Invocation:

1. **Ubersuggest MCP** (4 Tools, DE-Locale `locId=2276, language=de`):
   - `mcp__ubersuggest__domain_overview` — DA, Traffic-Trend, Keywords
   - `mcp__ubersuggest__domain_keywords` (limit=50) — Top-Ranking-KWs
   - `mcp__ubersuggest__domain_top_pages` (limit=20) — Traffic-Pages
   - `mcp__ubersuggest__backlinks_overview` — Link-Profil

2. **Firecrawl CLI** (Bash):
   - `bin/firecrawl-pp-cli.exe audit <domain> --limit 10 --quiet --format json`
   - Auth via `FIRECRAWL_API_KEY` (aus config.ps1 vorab gesetzt)

## Output

**Dual:** Markdown im Chat + Datei `reports/audit-<domain>-<YYYYMMDD>.md`.

Struktur:
```markdown
# Domain Audit: <domain>
**Datum:** YYYY-MM-DD  •  **Health-Score:** X/10

## SEO Position (Ubersuggest)
| Metrik | Wert |
| DA | ... |
| Organic Traffic (akt.) | ... |
| Ranking KWs (akt.) | ... |
| Trend 6M | ... |

### Top Keywords
(Tabelle: KW, Position, Volume, CPC)

### Top Pages
(Tabelle: URL, Traffic, KW-Count)

## Backlink Profile
- Total / Ref-Domains / Gov-Edu / Follow-Ratio
- Auffälligkeiten (z.B. plötzlicher Link-Loss)

## On-Page (Firecrawl)
- Sitemap-Size (entdeckt / gescraped / Fehler)
- Pro URL: title, meta_description, h1, h2[], canonical
- Error-States (Pages die "Es ist ein Fehler aufgetreten" o.ä. zurückgeben)

## Verdict
- Health-Diagnose (deindexed? broken? abandoned? thriving?)
- **Outreach-Hook:** 1 Satz mit dem auffälligsten Signal
```

## Health-Score Heuristik

Score 0-10, deriviert aus:
- DA ≥ 30: +2 / DA ≥ 15: +1 / DA < 10: 0
- Traffic-Trend stabil/wachsend: +2 / fallend: 0 / komplett verloren: -3
- Ranking-KWs ≥ 50: +2 / ≥ 10: +1 / 0: -3
- Firecrawl: Hauptseiten 200 OK: +2 / Error-Pages > 50%: -3
- Backlink-Profile: Gov/Edu Links: +1 / Follow > 60%: +1

## Skill-Datei-Format

Standard Claude-Skill Markdown mit YAML-Frontmatter:
```yaml
---
name: audit
description: Audit eine Domain via Ubersuggest MCP + Firecrawl CLI. Liefert kombinierten SEO+On-Page-Report. Trigger bei "audit <domain>" oder "/audit".
---
```

Body enthält:
1. Workflow-Beschreibung (4 MCP-Calls parallel + Firecrawl-Subprocess)
2. Output-Template (Markdown)
3. Health-Score-Regeln
4. Edge-Cases (Domain nicht in Ubersuggest, Firecrawl 401, Sitemap leer)

## Rollout

1. Schreibe `.claude/skills/audit.md`
2. Test gegen `vitaminbude.de` (bekannter Edge-Case: Domain ist deindexed)
3. Commit
