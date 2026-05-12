# Firecrawl CLI — Usage Guide

**Binary:** `bin/firecrawl-pp-cli.exe`
**Source:** `C:\Users\myste\printing-press\library\firecrawl\`
**Built:** 2026-05-12 via CLI Printing Press v4.4.0
**Scorecard:** 84/100 (Grade A)

## Auth

Liest aus zwei Env-Vars (in dieser Reihenfolge):
1. `FIRECRAWL_BEARER_AUTH` (CLI-native Konvention)
2. `FIRECRAWL_API_KEY` (Firecrawl-Doku-Konvention) — `config.ps1`-kompatibel

PowerShell-Setup:
```powershell
. "D:\000 SEO Business\Tools\config.ps1"
$env:FIRECRAWL_API_KEY = $FIRECRAWL_API_KEY
```

## Primary Command: `audit <domain>`

Compound-Pipeline für Lead-Recherche. Macht in einem Call:
1. `/v2/map` → Sitemap entdecken
2. Priorisiert Impressum, Kontakt, Datenschutz + Root
3. `/v2/scrape` parallel (5 Worker default) für die Top-URLs
4. Extrahiert SEO (title, meta, h1, h2[], canonical, internal_links) + Business (phone, email, address, services)
5. Output: NDJSON, eine Zeile pro URL — agent-/stream-tauglich

```powershell
.\bin\firecrawl-pp-cli.exe audit vitaminbude.de --limit 10 --quiet
.\bin\firecrawl-pp-cli.exe audit example.de --format json
.\bin\firecrawl-pp-cli.exe audit example.de --format md --quiet > report.md
```

### Flags

| Flag | Default | Beschreibung |
|---|---|---|
| `--limit` | 20 | Max URLs aus Sitemap |
| `--concurrency` | 5 | Parallele Scrape-Worker |
| `--format` | `ndjson` | `ndjson` \| `json` \| `md` |
| `--only-main-content` | true | Header/Nav/Footer strippen |
| `--include-subdomains` | false | Subdomains mitnehmen |
| `--scrape-timeout` | 30000 | Per-Page-Timeout (ms) |
| `--search` | "" | Such-Hint an `/map` |
| `--quiet` | false | Stderr unterdrücken (nur Data) |

## Andere Commands

| Command | Zweck |
|---|---|
| `scrape <url>` | Einzelne URL → Markdown |
| `map <domain>` | Sitemap als JSON |
| `firecrawl-search <query>` | Web-Suche |
| `api batch …` | Batch-Scrape |
| `api crawl …` | Async Domain-Crawl |
| `api extract …` | LLM-strukturierte Extraktion |
| `api deep-research …` | Tiefenrecherche |
| `api llmstxt …` | llms.txt generieren |
| `doctor` | Auth/Connectivity-Check |
| `workflow` | Kombinations-Workflows |

`firecrawl-pp-cli.exe --help` für alle.

## Agent-Integration (MCP)

Alle Commands sind als MCP-Tools verfügbar:
```powershell
.\bin\firecrawl-pp-cli.exe mcp serve
```

`audit` ist als `mcp:read-only` annotiert — primäres Tool für Agent-Lead-Recherche.

## Beispiel: Lead-Profil für Outreach

```powershell
$domains = Get-Content leads.txt
foreach ($d in $domains) {
  $profile = & .\bin\firecrawl-pp-cli.exe audit $d --limit 5 --quiet --format json | ConvertFrom-Json
  # $profile.entries[*] enthält title/meta/h1/h2/business pro Seite
}
```

## Verification

Getestet gegen `vitaminbude.de` am 2026-05-12:
- ✅ Auth via `FIRECRAWL_API_KEY` aus config.ps1
- ✅ NDJSON-Output korrekt strukturiert
- ✅ Title + meta_description + word_count extrahiert
