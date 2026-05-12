# Firecrawl CLI Design

**Date:** 2026-05-12
**Tool:** CLI Printing Press (`/printing-press Firecrawl`)
**Output:** `firecrawl-pp-cli` + `firecrawl-pp-mcp`

## Use Case

Firecrawl CLI für den maxcontentseo Outreach-Workflow:
- Lead-Domains crawlen und Business-Daten extrahieren (Impressum, Kontakt, Services)
- SEO On-Page-Audit (title, meta, H1-H3, canonicals, interne Links)
- Kombination beider Daten in einem Agent-nativen Compound-Command

## Commands

| Command | Endpoint | Beschreibung |
|---|---|---|
| `scrape <url>` | POST /scrape | Einzelne URL → Markdown + Metadata |
| `crawl <domain>` | POST /crawl | Async Domain-Crawl, polling bis fertig |
| `map <domain>` | POST /map | Sitemap als JSON |
| `extract <url> --schema <json>` | POST /extract | LLM-strukturierte Extraktion |
| `search <domain> <query>` | POST /search | Suche im gecrawlten Content |
| `profile <domain>` | compound | SEO + Business-Daten kombiniert → NDJSON |

## Compound Command: `profile <domain>`

Pipeline:
1. `map <domain>` → Sitemap (max. 20 URLs)
2. `scrape` jede URL parallel (max. 5 concurrent)
3. Extraktion pro Seite: `title`, `meta_description`, `h1`, `h2[]`, `canonical`, `internal_links[]`
4. Heuristik: Impressum/Kontakt-Seiten → `extract` mit Business-Schema (`phone`, `email`, `address`, `services[]`)
5. Output: kompaktes NDJSON, eine Zeile pro URL

## Output-Design

- Default: NDJSON (agent-native, streamable)
- `--format json`: vollständiges strukturiertes JSON
- `--format md`: Markdown-Report
- `--quiet`: reiner Data-Output, kein Logging
- Exit codes: `0` = Erfolg, `1` = API-Fehler, `2` = keine Daten

## Auth

`FIRECRAWL_API_KEY` env var. Kein Hardcode. `auth` Command prüft Connectivity.

## MCP Surface

Alle Commands automatisch als MCP-Tools via Cobra-Tree Walker.
`profile` ist das primäre Agent-Tool für den Outreach-Workflow.
Annotationen: alle read-only (`mcp:read-only = true`), kein mutativer State.

## Seed-Prompt für Printing Press

```
Firecrawl API — https://docs.firecrawl.dev/api-reference
Auth: Bearer token via FIRECRAWL_API_KEY env var
Primary compound command: `profile <domain>` — map site, scrape top pages, extract SEO metadata
(title, meta, h1, h2[], canonical, internal_links) and business data (phone, email, address,
services[]) from Impressum/contact pages. Output: NDJSON, one line per URL.
Agent-native: --quiet flag, compact output, all tools exposed as MCP.
```
