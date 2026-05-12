---
name: audit
description: Domain-Audit für Outreach-Vorbereitung. Kombiniert Ubersuggest MCP (DA, Traffic, Keywords, Backlinks), Firecrawl CLI (Sitemap, On-Page), PageSpeed API und Cross-Verification via WebFetch + Google-Index-Check. Use when user types `/audit <domain>`, `audit domain X`, oder bittet um SEO+On-Page-Bewertung einer Domain für Lead-Recherche. Schreibt Report ins Chat UND nach `reports/audit-<domain>-<YYYYMMDD>.md`.
---

# Domain Audit Skill

## Inputs
- Args: `<domain>` (z.B. `vitaminbude.de`, ohne `https://`)
- Defaults: DE-Locale (`locId=2276, language=de`), Firecrawl `--limit 10`

## Core-Prinzip: Zwei-Quellen-Regel

**Jeder kritische Befund im Report muss durch mindestens 2 unabhängige Quellen bestätigt sein.** Nicht-bestätigte Befunde werden explizit als `⚠️ nicht verifiziert` gekennzeichnet, nie unterdrückt.

Verifikations-Matrix:

| Befund | Quelle 1 | Quelle 2 | Verified wenn |
|---|---|---|---|
| URL kaputt | Firecrawl meldet Error/Timeout | WebFetch HTTP 4xx/5xx | beide fehlschlagen |
| Meta-Description ist Platzhalter | Firecrawl `meta_description`-Feld | WebFetch HTML `<meta name="description">` | beide enthalten Platzhalter-Pattern |
| Domain deindexiert | Ubersuggest Traffic = 0 für ≥ 3 Monate | Google `site:domain` Index-Count = 0 | beide melden 0 |
| Domain ranking-tot, aber indexiert | Ubersuggest Traffic = 0 | Google `site:` ≥ 1 Treffer | beide bestätigen Diskrepanz |
| Domain redirected | Curl HEAD Location-Header | WebFetch Final-URL | beide zeigen gleiches Target |

PageSpeed-Score bekommt **keine Cross-Verification** (single source, neutrale Diagnostik) — wird mit Hinweis `(single source: Google PageSpeed API)` ausgewiesen.

## Workflow

### Phase 0 — Redirect Resolution (sequentiell, MUST RUN FIRST)

Bevor irgendetwas anderes passiert, prüfe ob die Input-Domain weiterleitet:

```bash
curl -sIL -o /dev/null -w "%{url_effective}\n%{http_code}\n" "https://<input-domain>" --max-time 15
```

Auswerten:
- Wenn `url_effective` host == input-host → kein Redirect, `target = input`
- Wenn `url_effective` host != input-host → Redirect detected, `target = redirect-host`, dokumentiere die Redirect-Chain im Report

**Cross-verify Redirect:** Falls Redirect detektiert, lade `WebFetch` mit der Input-URL und prüfe ob die Final-URL übereinstimmt. Bei Mismatch: `⚠️ Redirect nicht verifiziert (curl: X, WebFetch: Y)`.

**Wichtig:** `input` = Domain auf der Ubersuggest läuft (hostname-gebunden). `target` = Domain auf der Firecrawl + PageSpeed + Index-Check laufen (Content-Location).

### Phase 1 — Parallel Data Collection (eine Tool-Invocation)

In **einem** Assistant-Turn alle Calls parallel feuern:

1. `mcp__ubersuggest__domain_overview` — `{domain: <input>, language: "de", locId: 2276}`
2. `mcp__ubersuggest__domain_keywords` — `{domain: <input>, language: "de", locId: 2276, limit: 50}`
3. `mcp__ubersuggest__domain_top_pages` — `{domain: <input>, language: "de", locId: 2276, limit: 20}`
4. `mcp__ubersuggest__backlinks_overview` — `{domain: <input>}`
5. `Bash` — Firecrawl-Audit auf **target**:
   ```bash
   cd "D:/000 SEO Business/maxcontentseo" && \
   FIRECRAWL_API_KEY=$(grep FIRECRAWL_API_KEY "D:/000 SEO Business/Tools/config.ps1" | awk -F'"' '{print $2}') \
   ./bin/firecrawl-pp-cli.exe audit <target> --limit 10 --concurrency 5 --quiet 2>&1
   ```
   Timeout: 300000ms
6. `Bash` — Google-Index-Check via Firecrawl-Search:
   ```bash
   cd "D:/000 SEO Business/maxcontentseo" && \
   FIRECRAWL_API_KEY=$(grep FIRECRAWL_API_KEY "D:/000 SEO Business/Tools/config.ps1" | awk -F'"' '{print $2}') \
   ./bin/firecrawl-pp-cli.exe firecrawl-search --query "site:<target>" --limit 20 2>&1
   ```
   Timeout: 120000ms
7. `Bash` — PageSpeed Insights (kein Key nötig, public):
   ```bash
   curl -s "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://<target>&strategy=mobile&category=performance&category=seo" --max-time 60
   ```
   Falls Antwort > 50KB: pipe durch `jq '{score: .lighthouseResult.categories.performance.score, seo: .lighthouseResult.categories.seo.score, lcp: .lighthouseResult.audits["largest-contentful-paint"].displayValue, cls: .lighthouseResult.audits["cumulative-layout-shift"].displayValue}'`

**Wenn Ubersuggest-Tools nicht geladen sind**, vorher mit `ToolSearch` `select:mcp__ubersuggest__domain_overview,mcp__ubersuggest__domain_keywords,mcp__ubersuggest__domain_top_pages,mcp__ubersuggest__backlinks_overview` laden.

**Wenn WebFetch nicht geladen ist**, vorher mit `ToolSearch` `select:WebFetch` laden.

### Phase 1.5 — Verification Round (parallel, gezielt)

Werte Phase-1-Output aus und identifiziere zu verifizierende Behauptungen. Feuere in einem Turn parallel:

**Pflicht-Verification:**
- `WebFetch` auf `https://<target>` → vergleiche HTML mit Firecrawl-Root-Befund (Title, Meta-Description, Status)

**Conditional Verifications (nur wenn Phase 1 entsprechende Befunde liefert):**

| Trigger aus Phase 1 | Verifikations-Call |
|---|---|
| Firecrawl Meta-Description enthält `#`, `{{`, `%`, `[`, oder `<` als Auftakt (Template-Platzhalter-Pattern) | `WebFetch` auf URL, prüfe ob `<meta name="description"` content das exakt gleiche Pattern hat |
| Firecrawl URL `ok: false` (Error/Timeout) | `WebFetch` auf URL, prüfe HTTP-Status + Body |
| Firecrawl Title enthält "Fehler", "Error", "404", "Not Found", "503" | `WebFetch` auf URL, prüfe HTML-Status + visible Text |
| Ubersuggest Traffic = 0 für 3+ Monate | Schon in Phase 1 via Firecrawl-Search abgedeckt — auswerten ob count > 0 oder = 0 |
| Phase-1-Firecrawl-Sitemap nur 1 URL | `WebFetch` auf Root, extrahiere alle internen Links manuell aus HTML |

**Anti-Pattern:** Nicht jede URL pauschal verifizieren — nur die mit Befund. Sonst Token-Explosion.

### Phase 2 — Synthese

Nach Phase 0 + 1 + 1.5 hast du für jeden Befund:
- **Raw-Wert** (was Firecrawl/Ubersuggest sagt)
- **Verification-Wert** (was WebFetch/curl/PageSpeed/Google sagt)
- **Status:** `✅ verifiziert`, `❌ widersprüchlich`, `⚠️ nicht verifiziert` (single source)

Erstelle Markdown-Report nach dem Template. Health-Score berechnet sich **nur aus verifizierten Befunden** — unverifizierte Befunde gehen nicht in den Score ein, werden aber im Report gelistet.

Identifiziere den **stärksten Outreach-Hook** (das auffälligste, verifizierte Signal in 1 Satz).

### Phase 3 — Dual Output

1. Schreibe Report nach `reports/audit-<sanitized-domain>-<YYYYMMDD>.md`.
2. Gib im Chat kompakten Summary zurück (Top-Level-Tabelle + Verdict + Datei-Pfad).

## Report Template

````markdown
# Domain Audit: <input-domain>

**Datum:** YYYY-MM-DD
**Health-Score:** X/10 (aus N verifizierten Befunden)
**Verdict:** <one-liner>

## Domain Resolution

- **Input:** `<input-domain>`
- **Final Target:** `<target-domain>` <falls Redirect: "(via 301 Redirect)" — sonst "(direkt)">
- **Redirect Chain:** <falls vorhanden: A → B>  ·  Verifikation: ✅ curl + WebFetch übereinstimmend

## SEO Position (Ubersuggest, DE — auf Input-Domain)

| Metrik | Wert |
|---|---|
| Domain Authority | X/100 |
| Organic Traffic (aktuell) | X |
| Ranking Keywords (aktuell) | X |
| Trend 6M | ... |
| Paid Activity | Ja/Nein |

### Top Keywords / Top Pages
(wie zuvor — noData wenn leer)

## Backlink Profile (Ubersuggest)
- Total, Ref-Domains, Gov/Edu, Follow-Ratio, Auffälligkeiten

## On-Page (Firecrawl + WebFetch Cross-Check — auf Target-Domain)

- **Sitemap entdeckt:** X URLs
- **Erfolgreich gescraped:** Y
- **Fehler/Timeout (Firecrawl):** Z

### Per-URL Befund

| URL | Firecrawl | WebFetch | Status |
|---|---|---|---|
| `/path` | ✅ 200 | ✅ 200 | ✅ healthy |
| `/path` | ⚠️ Error-Page | ❌ HTTP 500 | ✅ broken (verifiziert) |
| `/path` | ⏱️ Timeout | ✅ 200 (slow) | ⚠️ unverifiziert (Firecrawl false positive) |
| `/path` | ⚠️ Error-Page | ✅ 200 + content OK | ⚠️ widersprüchlich |

### Meta-Description-Audit

| URL | Firecrawl-Wert | WebFetch-HTML | Status |
|---|---|---|---|
| `/` | `#IndexMetaDescriptionStandard#` | `#IndexMetaDescriptionStandard#` | ✅ Platzhalter bestätigt |

## Index Status (Google)

- **Ubersuggest-Traffic (3M):** 0 / 0 / 0
- **Google `site:<target>` Treffer:** N
- **Status:** ✅ verifiziert deindexiert (beide melden 0) ODER ⚠️ Diskrepanz (Ubersuggest 0, Google N — ranking-tot aber indexiert)

## PageSpeed (Google, Mobile)

*Single source — nicht cross-verifiziert*

| Metrik | Score |
|---|---|
| Performance | X/100 |
| SEO | X/100 |
| LCP | X.X s |
| CLS | X.XX |

## Verdict

**Health-Diagnose:** <Liste aller verifizierten kritischen Befunde>

**Nicht verifizierte / widersprüchliche Befunde:**
- ⚠️ <Befund> — <Grund warum nicht bestätigt>

**Outreach-Hook (für Cold-Mail):**
> <Konkreter Satz auf Basis NUR verifizierter Befunde>

**Empfohlene Nächste Schritte:**
1. ...
2. ...
````

## Health-Score Heuristik (0-10)

**Wichtige Regel:** Nur **verifizierte** Befunde gehen in den Score. Unverifizierte Befunde werden im Report transparent gemacht, beeinflussen den Score aber nicht.

Start bei 5, addiere/subtrahiere:

| Signal | Δ |
|---|---|
| DA ≥ 30 | +2 |
| DA ≥ 15 (aber < 30) | +1 |
| DA < 10 | −1 |
| Traffic-Trend wachsend (+15% MoM) | +2 |
| Traffic-Trend stabil | 0 |
| Traffic-Trend fallend | −1 |
| Traffic komplett verloren (≥ 3 Monate 0) **UND** Google site: = 0 (verifiziert deindexiert) | −3 |
| Traffic-Verlust **ohne** Index-Verlust (Ranking-tot, aber indexiert) | −2 |
| Ranking-KWs ≥ 50 | +2 |
| Ranking-KWs zwischen 5-49 | +1 |
| Ranking-KWs = 0 | −1 (Ergänzung zum Traffic-Penalty, kein Doppel-Punkt) |
| Firecrawl + WebFetch: > 80% Hauptseiten verifiziert OK | +2 |
| Firecrawl + WebFetch: 30-80% verifiziert OK | 0 |
| Firecrawl + WebFetch: < 30% verifiziert OK (broken) | −3 |
| Meta-Description-Platzhalter verifiziert (beide Quellen) | −1 |
| Gov/Edu Backlinks > 0 | +1 |
| Follow-Ratio > 60% | +1 |
| PageSpeed Performance < 30 | −1 (nicht-verifiziert, aber Signal) |
| PageSpeed Performance > 80 | +1 |

Cap bei 0 und 10.

**Score-Interpretation:**
- 8-10: Etablierter, gesunder Lead
- 5-7: Solide Basis, klare Optimierungs-Potentiale → guter Outreach-Kandidat
- 2-4: Domain hat Probleme → Outreach mit Lösungsangebot
- 0-1: Domain technisch/strategisch ausgefallen → Wake-Up-Hook

## Platzhalter-Pattern (für Meta-Description-Detection)

Diese Strings im Meta-Description-Feld signalisieren unausgefüllte CMS-Templates:
- `#...#` (z.B. `#IndexMetaDescriptionStandard#`)
- `{{...}}` (Mustache/Handlebars)
- `${...}` (JS Template Literal)
- `%...%` (URL-Param Style)
- `[insert ...]`, `[default ...]`, `[FIXME]`, `TODO`
- `<...>` außer wenn es valide HTML-Entities enthält
- Leer-String `""` oder reines Whitespace

Bei Match: Phase-1.5 Verifikation triggern.

## Edge Cases

1. **Domain nicht in Ubersuggest:** `noData`-Response → markiere "Domain unbekannt bei Ubersuggest (vermutlich sehr klein oder neu)". Health-Score-Start: 3.
2. **Firecrawl Auth-Fehler (401):** Stoppe, gib Hinweis "FIRECRAWL_API_KEY nicht gesetzt — siehe `docs/firecrawl-cli-usage.md`".
3. **Firecrawl Sitemap leer (nur 1 URL):** WebFetch auf Root, extrahiere alle internen + externen Links. Falls externer Link auf ähnliche Domain (`<name>-shop.<tld>`, `shop.<domain>`): Hinweis im Report + Vorschlag re-audit auf Sub-/Shop-Domain.
4. **Redirect zu einer komplett anderen Domain (z.B. zu Amazon Seller):** Sonderfall — Domain ist verkauft/aufgegeben. Stoppe nach Phase 0, schreibe Kurz-Report mit Diagnose "Domain redirected zu unverwandter Site — kein eigenständiger Lead".
5. **PageSpeed API Rate-Limit (HTTP 429):** Melde "PageSpeed nicht abrufbar (Rate-Limit)" im Report, kein Score-Impact.
6. **Firecrawl-Search liefert keine Treffer aber Domain ist groß:** Search-API könnte rate-limitiert sein — markiere `⚠️ Google-Index-Check unverifiziert`.
7. **Beide Quellen liefern wenig:** Markiere "Lead vermutlich klein/lokal/neu" — Outreach-Hook auf Wachstums-Potential lenken.

## File-Naming

`reports/audit-<sanitized-input-domain>-<YYYYMMDD>.md`
- `<sanitized-input-domain>`: Input-Domain (nicht Target!) mit `.` → `-` ersetzt, lowercase.
- `<YYYYMMDD>`: Heutiges Datum.
- Beispiel: `reports/audit-vitaminbude-de-20260512.md`

Wenn Re-Audit am gleichen Tag: Hänge `-v2`, `-v3` etc. an.

## Anti-Patterns

- ❌ Sequentielle Tool-Calls — IMMER parallel in einem Turn (außer Phase 0 muss vor Phase 1 laufen)
- ❌ Befunde als bestätigt ausgeben ohne Cross-Check — IMMER Verifikation-Status mitschreiben
- ❌ Eigene Berechnungen oder Schätzungen wenn Daten `noData` sind — explizit `noData` im Report
- ❌ Generische Empfehlungen — der Verdict-Block muss konkret und datengetrieben sein
- ❌ Phase 1.5 für jede einzelne URL pauschal triggern — nur für URLs mit auffälligem Befund aus Phase 1
- ❌ Den Report-Text ins Memory schreiben — nur den Datei-Pfad und Top-Level-Metriken merken
- ❌ Unverifizierte Befunde im Health-Score zählen — Score bleibt sauber auf bestätigten Daten
