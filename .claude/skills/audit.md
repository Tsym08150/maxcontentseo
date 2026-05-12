---
name: audit
description: Domain-Audit für Outreach-Vorbereitung. Kombiniert Ubersuggest MCP (DA, Traffic, Keywords, Backlinks) und das lokale Firecrawl CLI (Sitemap, On-Page-Daten, Title/Meta/H1). Use when user types `/audit <domain>`, `audit domain X`, oder bittet um SEO+On-Page-Bewertung einer Domain für Lead-Recherche. Schreibt Report ins Chat UND nach `reports/audit-<domain>-<YYYYMMDD>.md`.
---

# Domain Audit Skill

## Inputs
- Args: `<domain>` (z.B. `vitaminbude.de`, ohne `https://`)
- Defaults: DE-Locale (`locId=2276, language=de`), Firecrawl `--limit 10`

## Workflow

### Step 1 — Parallel Data Collection (eine Tool-Invocation)

In **einem** Assistant-Turn alle fünf Calls parallel feuern:

1. `mcp__ubersuggest__domain_overview` — `{domain, language: "de", locId: 2276}`
2. `mcp__ubersuggest__domain_keywords` — `{domain, language: "de", locId: 2276, limit: 50}`
3. `mcp__ubersuggest__domain_top_pages` — `{domain, language: "de", locId: 2276, limit: 20}`
4. `mcp__ubersuggest__backlinks_overview` — `{domain}`
5. `Bash` — Firecrawl-Audit:
   ```bash
   cd "D:/000 SEO Business/maxcontentseo" && \
   FIRECRAWL_API_KEY=$(grep FIRECRAWL_API_KEY "D:/000 SEO Business/Tools/config.ps1" | awk -F'"' '{print $2}') \
   ./bin/firecrawl-pp-cli.exe audit <domain> --limit 10 --concurrency 5 --quiet 2>&1
   ```
   Timeout: 300000ms

**Wenn Ubersuggest-Tools nicht geladen sind**, vorher mit `ToolSearch` `select:mcp__ubersuggest__domain_overview,mcp__ubersuggest__domain_keywords,mcp__ubersuggest__domain_top_pages,mcp__ubersuggest__backlinks_overview` laden.

### Step 2 — Synthese

Erstelle Markdown-Report nach dem Template unten. Berechne Health-Score nach den Regeln. Identifiziere den **stärksten Outreach-Hook** (das auffälligste Signal in 1 Satz).

### Step 3 — Dual Output

1. Schreibe Report nach `reports/audit-<sanitized-domain>-<YYYYMMDD>.md` (Domain ohne Punkte/Slashes).
2. Gib im Chat einen kompakten Summary (Tabelle Top-Level-Metriken + Verdict-Block) zurück, mit Hinweis auf den Datei-Pfad.

## Report Template

````markdown
# Domain Audit: <domain>

**Datum:** YYYY-MM-DD
**Health-Score:** X/10  ·  **Verdict:** <one-liner>

## SEO Position (Ubersuggest, DE)

| Metrik | Wert |
|---|---|
| Domain Authority | X/100 |
| Organic Traffic (aktuell) | X |
| Ranking Keywords (aktuell) | X |
| Trend 6M | "stabil" / "wachsend +X%" / "fallend -X%" / "komplett verloren" |
| Paid Activity | Ja/Nein |

### Top Keywords
| KW | Position | Volume | CPC |
| ... | ... | ... | ... |

(Top 10 nach Volume × inverse Position; "noData" wenn leer)

### Top Pages
| URL | Traffic | KW-Count |
| ... | ... | ... |

(Top 5; "noData" wenn leer)

## Backlink Profile

- **Total:** X Backlinks von Y Ref-Domains
- **Gov/Edu:** Z (Premium-Indikator)
- **Follow-Ratio:** N% (Follow/Total)
- **Auffälligkeit:** <z.B. "plötzlicher Verlust seit Datum X" oder "konstant über Y Monate">

## On-Page (Firecrawl Live-Crawl)

- **Sitemap entdeckt:** X URLs
- **Erfolgreich gescraped:** Y
- **Fehler/Timeout:** Z

### Per-URL Befund
| URL | Status | Title | Notable |
| ... | ✅ 200 | "..." | h1=... |
| ... | ⚠️ Error-Page | "Ups! Fehler" | broken |
| ... | ⏱️ Timeout | — | slow/down |

(Nur auffällige Pages aufgenommen — alle "saubere" Pages zusammengefasst)

## Verdict

**Health-Diagnose:** <konkret. "Domain ist seit Nov 2025 deindexiert, gleichzeitig liefern alle Shop-Unterseiten Fehler — Shop ist technisch ausgefallen.">

**Outreach-Hook (für Cold-Mail):**
> <Ein konkreter Satz, den man wortwörtlich in eine Mail einbauen kann. Beispiel: "Mir ist aufgefallen, dass Ihr Shop unter vitaminbude-shop.de seit Monaten Fehler-Seiten ausliefert und Google ihn deshalb seit November aus dem Index entfernt hat — wussten Sie davon?">

**Empfohlene Nächste Schritte:**
1. ...
2. ...
````

## Health-Score Heuristik (0-10)

Start bei 5, addiere/subtrahiere:

| Signal | Δ |
|---|---|
| DA ≥ 30 | +2 |
| DA ≥ 15 (aber < 30) | +1 |
| DA < 10 | −1 |
| Traffic-Trend wachsend (+15% MoM) | +2 |
| Traffic-Trend stabil | 0 |
| Traffic-Trend fallend | −1 |
| Traffic komplett verloren (≥ 3 Monate 0) | −3 |
| Ranking-KWs ≥ 50 | +2 |
| Ranking-KWs zwischen 5-49 | +1 |
| Ranking-KWs = 0 | −3 |
| Firecrawl: > 80% Hauptseiten OK | +2 |
| Firecrawl: 30-80% OK | 0 |
| Firecrawl: < 30% OK (broken) | −3 |
| Gov/Edu Backlinks > 0 | +1 |
| Follow-Ratio > 60% | +1 |

Cap bei 0 und 10.

**Score-Interpretation:**
- 8-10: Etablierter, gesunder Lead — schwer zu beeindrucken
- 5-7: Solide Basis, aber klare Optimierungs-Potentiale → guter Outreach-Kandidat
- 2-4: Domain hat Probleme → Outreach mit Lösungsangebot
- 0-1: Domain ist technisch oder strategisch ausgefallen → Outreach mit Wake-Up-Hook (siehe vitaminbude-Beispiel)

## Edge Cases

1. **Domain nicht in Ubersuggest:** `noData`-Response → markiere "Domain unbekannt bei Ubersuggest (vermutlich sehr klein oder neu)". Health-Score-Start: 3.
2. **Firecrawl Auth-Fehler (401):** Stoppe, gib Hinweis "FIRECRAWL_API_KEY nicht gesetzt — siehe `docs/firecrawl-cli-usage.md`".
3. **Firecrawl Sitemap leer (nur 1 URL):** Hinweis im Report: "Domain könnte Landingpage-Setup haben — prüfe ob es ein echtes Subdomain-Setup gibt (z.B. `<domain>-shop.de`)". Sammle Links via `scrape --formats '["markdown","links"]'` von der Root-Page und liste interne/externe Targets im Report.
4. **Beide Quellen liefern wenig:** Markiere "Lead vermutlich klein/lokal/neu" — Outreach-Hook auf Wachstums-Potential lenken.

## File-Naming

`reports/audit-<sanitized-domain>-<YYYYMMDD>.md`
- `<sanitized-domain>`: Domain mit `.` → `-` ersetzt, lowercase. Beispiel: `vitaminbude.de` → `vitaminbude-de`
- `<YYYYMMDD>`: Heutiges Datum.
- Beispiel: `reports/audit-vitaminbude-de-20260512.md`

## Anti-Patterns

- ❌ Sequentielle Tool-Calls (1 Call, warten, nächster Call) — IMMER parallel feuern in einem Turn
- ❌ Eigene Berechnungen oder Schätzungen wenn Daten "noData" sind — explizit "noData" im Report melden
- ❌ Generische Empfehlungen wie "verbessern Sie SEO" — der Verdict-Block muss konkret und datengetrieben sein
- ❌ Den Report-Text ins Memory schreiben — nur den Datei-Pfad und Top-Level Metriken merken
