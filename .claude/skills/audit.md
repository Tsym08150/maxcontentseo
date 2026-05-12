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

### Phase 3 — Triple Output

Generiere drei Dateien parallel:

1. **Markdown-Report:** `reports/audit-<sanitized-domain>-<YYYYMMDD>.md` — vollständig (alle Phasen, alle Befunde, alle Status).
2. **PDF-Report:** `reports/audit-<sanitized-domain>-<YYYYMMDD>.pdf` — vom MD generiert via Edge Headless (siehe PDF-Generation-Block).
3. **Outreach-Mail:** `reports/outreach-<sanitized-domain>-<YYYYMMDD>.txt` — fertige Cold-Mail nach Variante-C-Format (siehe Outreach-Mail-Block).

Dann Chat-Summary mit den drei Datei-Pfaden + Top-Level-Metriken + Verdict + Vorschau der Outreach-Mail.

### PDF-Generation

Edge Headless rendert HTML → PDF. Pipeline:

```javascript
// In ctx_execute (javascript):
const fs = require('fs');
const { execFileSync } = require('child_process');
const path = require('path');

const md = fs.readFileSync('reports/audit-<domain>-<date>.md', 'utf-8');

// Minimaler MD→HTML-Konverter (keine npm deps, kein Markdown-Spec-Voll-Support, aber für unsere Reports reicht es)
function mdToHtml(md) {
  let h = md
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/^### (.*$)/gm, '<h3>$1</h3>')
    .replace(/^## (.*$)/gm, '<h2>$1</h2>')
    .replace(/^# (.*$)/gm, '<h1>$1</h1>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/^\> (.*$)/gm, '<blockquote>$1</blockquote>')
    .replace(/^\| (.+) \|$/gm, (line) => {
      const cells = line.split('|').slice(1, -1).map(c => c.trim());
      const isSep = cells.every(c => /^[-:\s]+$/.test(c));
      if (isSep) return '<!--sep-->';
      return '<tr>' + cells.map(c => `<td>${c}</td>`).join('') + '</tr>';
    })
    .replace(/(<tr>[\s\S]+?<\/tr>(\s*<!--sep-->\s*<tr>[\s\S]+?<\/tr>)*)/g, '<table>$1</table>')
    .replace(/<!--sep-->/g, '')
    .replace(/\n\n/g, '</p><p>');
  return `<!DOCTYPE html><html><head><meta charset="utf-8"><style>
    body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:780px;margin:40px auto;padding:0 20px;color:#222;line-height:1.55}
    h1{border-bottom:2px solid #333;padding-bottom:8px}
    h2{border-bottom:1px solid #ccc;padding-bottom:4px;margin-top:32px}
    h3{margin-top:24px}
    table{border-collapse:collapse;margin:12px 0;width:100%;font-size:0.95em}
    td,th{border:1px solid #ccc;padding:6px 10px;text-align:left;vertical-align:top}
    code{background:#f4f4f4;padding:1px 5px;border-radius:3px;font-size:0.9em}
    blockquote{border-left:4px solid #888;padding-left:14px;color:#555;margin-left:0;font-style:italic}
    strong{color:#000}
  </style></head><body><p>${h}</p></body></html>`;
}

const html = mdToHtml(md);
const tmpHtml = path.resolve('reports/_tmp-audit.html');
fs.writeFileSync(tmpHtml, html, 'utf-8');

const edge = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const outPdf = path.resolve('reports/audit-<domain>-<date>.pdf');
execFileSync(edge, [
  '--headless', '--disable-gpu', '--no-sandbox',
  `--print-to-pdf=${outPdf}`,
  `file:///${tmpHtml.replace(/\\/g,'/')}`
], { stdio: 'pipe', timeout: 30000 });

fs.unlinkSync(tmpHtml);
console.log('PDF written:', outPdf);
```

Falls Edge nicht verfügbar oder fehlschlägt: Fallback auf `npx markdown-pdf reports/audit-<domain>-<date>.md -o reports/audit-<domain>-<date>.pdf`. Falls auch das fehlschlägt: PDF überspringen, nur MD + TXT ausliefern, Hinweis im Chat-Output.

### Outreach-Mail-Generierung

**Format (Variante C):**

```
Betreff: Kurze Frage zu Ihrem Studio in [ORT]

Sehr geehrte/r [NAME],

<2-3 stärkste verifizierte Befunde, formuliert als Beobachtungen — keine Wertung, keine Heilversprechen, keine Produkt-Aussagen. Jeder Befund 25-35 Wörter.>

<Verbindender Übergangs-Satz, max. 15 Wörter.>

<CTA-Block:>
Wenn Sie möchten, schicke ich Ihnen einen kurzen Befund-Report (1 PDF, 2 Seiten) mit den genauen Stellen und einer 3-Punkte-Empfehlung. Ein kurzes "Ja" per Antwort genügt.

Mit freundlichen Grüßen
[ABSENDER]
```

**Strenge Regeln:**

| Regel | Begründung |
|---|---|
| **Max. 120 Wörter** im Mail-Body (ohne Betreff, Anrede, Gruß) | Cold-Mail-Best-Practice + B2B-Aufmerksamkeitsspanne |
| **Nur 2-3 stärkste verifizierte Befunde** (✅ 2-Quellen-bestätigt) | Mehr → Mail wirkt überfordernd; weniger als 2 → zu dünn |
| **Sie-Form durchgehend** | B2B-Convention DE |
| **HWG-konform** | Keine Aussagen über Heilung, Behandlung, Wirkung, Gesundheit; nur Website-/SEO-Befunde |
| **Keine Produktangebote in der Mail** | CTA ist erst der PDF-Download, nicht die Leistung |
| **Platzhalter `[NAME]`, `[ORT]`, `[ABSENDER]` bleiben** sofern Daten nicht verfügbar | Nutzer füllt manuell auf |
| **Encoding: UTF-8 ohne BOM** | PowerShell-Kompatibilität (siehe `feedback_encoding_hieroglyphen.md`) |
| **Befunde im Mail-Text, nicht im Anhang** | Anhang wird oft nicht geöffnet; Nutzwert muss im Text sein |
| **CTA: "Ein kurzes 'Ja' genügt"** | Niedrigstmögliche Reply-Schwelle |

**Befund-Selektion (Top 2-3):**

Sortiere alle Befunde aus dem Audit nach `severity_score`:

```
severity_score = verification_count * 2 + impact_weight + visibility_weight

verification_count: 2 wenn 2-Quellen-bestätigt, sonst 0 (nicht-bestätigte werden nicht selektiert)
impact_weight:
  + 3 wenn betrifft kritische Funktionalität (Shop tot, Auth tot, Kontaktform tot)
  + 2 wenn betrifft Suchsichtbarkeit (Meta-Tags, Index-Status, 404s)
  + 1 wenn betrifft Performance (PageSpeed, LCP)
visibility_weight:
  + 2 wenn von außen direkt sichtbar (in Google SERP, in URL-Bar)
  + 1 wenn intern aber leicht prüfbar
  + 0 wenn nur in Devtools sichtbar
```

Wähle die Top 2-3 mit den höchsten Scores. Bei Gleichstand bevorzuge unterschiedliche Befund-Kategorien (z.B. nicht 2× "kaputte Kategorien-URLs").

**Befund-Formulierungs-Templates:**

Jeder Befund wird konkret und prüfbar formuliert:

| Befund-Typ | Template |
|---|---|
| Kaputte URLs (verifiziert) | "Beim Aufruf von <code>www.[domain]/[pfad]</code> erscheint statt der Inhalts-Seite eine 404-Fehlerseite — das betrifft auch <code>/[pfad2]</code> und [n] weitere Kategorien." |
| Meta-Description Platzhalter | "In der Google-Suche zeigt sich bei Ihrer Startseite der unausgefüllte Platzhalter-Text <code>#IndexMetaDescriptionStandard#</code> statt einer Beschreibung." |
| Deindexed | "Ihre Domain rankt aktuell für 0 Keywords bei Google — vor [N] Monaten waren es noch [M]." |
| PageSpeed kritisch | "Die mobile Ladezeit Ihrer Startseite liegt bei [LCP] (Empfehlung: < 2,5 s)." |
| Redirect-Inkonsistenz | "Die Domain <code>[input]</code> leitet weiter zu <code>[target]</code> — Nutzer und Backlinks landen auf einer anderen URL als erwartet." |

**HWG-Sperrwörter (NIEMALS verwenden):**
- "heilen", "Heilung", "heilend"
- "Behandlung", "Therapie" (außer im Kontext "SEO-Audit")
- "Gesundheit", "gesund" (außer in der Domain selbst)
- "Wirkung", "wirksam"
- "Patient", "Patientin" (statt: "Besucher", "Interessenten")
- "Erfolg" mit Heilbezug
- Konkrete Symptome / Krankheiten / Diagnosen

**Wenn die Domain weniger als 2 verifizierte Befunde hat:**
Outreach-Mail nicht generieren. Statt-dessen `reports/outreach-<domain>-<date>.txt` mit Inhalt `# Outreach nicht generiert\n\nZu wenig verifizierte Befunde (<2). Manuell prüfen.` schreiben.

**[ORT]- und [NAME]-Extraktion (opportunistisch):**

Wenn Phase 1 die Impressum-Seite erfolgreich gescraped hat, extrahiere via Regex aus dem Markdown:
- `[ORT]`: deutsche PLZ + Ort (`\d{5}\s+[A-ZÄÖÜ][a-zäöüß-]+`)
- `[NAME]`: "Geschäftsführer:?", "Inhaber:?", "vertreten durch:?" gefolgt von Name

Wenn Match: ersetze Platzhalter im Mail-Text. Wenn kein Match: Platzhalter bleibt für manuelle Ergänzung durch Nutzer.

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

Pro Audit-Lauf entstehen drei Dateien (gleicher Stamm):

- `reports/audit-<sanitized-input-domain>-<YYYYMMDD>.md` — Markdown-Report
- `reports/audit-<sanitized-input-domain>-<YYYYMMDD>.pdf` — PDF-Version (für Versand)
- `reports/outreach-<sanitized-input-domain>-<YYYYMMDD>.txt` — fertige Outreach-Mail

Regeln:
- `<sanitized-input-domain>`: Input-Domain (nicht Target!) mit `.` → `-` ersetzt, lowercase.
- `<YYYYMMDD>`: Heutiges Datum.
- Beispiel: `reports/audit-vitaminbude-de-20260512.md` / `.pdf` / `reports/outreach-vitaminbude-de-20260512.txt`
- Wenn Re-Audit am gleichen Tag: Hänge `-v2`, `-v3` etc. an. Alle drei Dateien kriegen das gleiche Suffix.

## Anti-Patterns

- ❌ Sequentielle Tool-Calls — IMMER parallel in einem Turn (außer Phase 0 muss vor Phase 1 laufen)
- ❌ Befunde als bestätigt ausgeben ohne Cross-Check — IMMER Verifikation-Status mitschreiben
- ❌ Eigene Berechnungen oder Schätzungen wenn Daten `noData` sind — explizit `noData` im Report
- ❌ Generische Empfehlungen — der Verdict-Block muss konkret und datengetrieben sein
- ❌ Phase 1.5 für jede einzelne URL pauschal triggern — nur für URLs mit auffälligem Befund aus Phase 1
- ❌ Den Report-Text ins Memory schreiben — nur den Datei-Pfad und Top-Level-Metriken merken
- ❌ Unverifizierte Befunde im Health-Score zählen — Score bleibt sauber auf bestätigten Daten
- ❌ Outreach-Mail mit unverifizierten Befunden schreiben — nur ✅-Befunde landen im Mail-Text
- ❌ Heilversprechen, Produkt-Aussagen, Patient/Krankheit-Begriffe in der Outreach-Mail — HWG-Sperre
- ❌ Outreach-Mail mit >120 Wörtern im Body — strikter Cut, lieber Befund kürzen
- ❌ PDF mit BOM-Encoding oder relativem Pfad an Edge übergeben — Edge braucht `file:///` mit absolutem Pfad und Forward-Slashes
- ❌ `.txt` Mail mit UTF-8-BOM schreiben — PowerShell/Outlook zeigen Hieroglyphen (siehe `feedback_encoding_hieroglyphen.md`)
