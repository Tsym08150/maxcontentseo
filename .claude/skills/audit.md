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
| Firecrawl Meta-Description enthält `#`, `{{`, `%`, `[`, oder `<` als Auftakt (Template-Platzhalter-Pattern) | `ctx_execute` direkter HTTP-GET, prüfe ob `<meta name="description"` content das exakt gleiche Pattern hat |
| Firecrawl URL `ok: false` ODER Title enthält Error-Pattern ("Fehler", "Error", "404", "503") | **Doppel-Check mit beiden URL-Varianten:** `curl -sI <url>` UND `curl -sI <url>/` — vergleiche Status der Slash- und Non-Slash-Variante getrennt |
| Ubersuggest Traffic = 0 für 3+ Monate | Schon in Phase 1 via Firecrawl-Search abgedeckt — auswerten ob count > 0 oder = 0 |
| Phase-1-Firecrawl-Sitemap nur 1 URL | `ctx_fetch_and_index` auf Root, extrahiere alle internen Links aus HTML |

**Trailing-Slash-Diagnose (Pflicht bei Error-Befund):**

Für JEDE URL die in Phase 1 als kaputt/error verifiziert wird, immer beide Varianten testen:

```bash
curl -sI --max-time 10 "https://<target>/<pfad>"   # ohne Slash
curl -sI --max-time 10 "https://<target>/<pfad>/"  # mit Slash
```

Vier mögliche Outcomes — pro Outcome anderer Befund-Typ:

| no-slash | with-slash | Befund-Typ | Severity-Mapping |
|---|---|---|---|
| 404 | 200 | **URL-Normalisierungsproblem** | Mittel — Inhalte existieren, nur Routing kaputt |
| 200 | 200 | URL funktioniert | Kein Befund |
| 404 | 404 | **Echte 404 / Inhalt entfernt** | Hoch — Inhalte fehlen |
| 200 | 404 | Inverses Slash-Problem (selten) | Mittel — Routing-Bug |

Verwende `URL-Normalisierungsproblem`-Wording NIEMALS synonym mit "broken pages" oder "ausgefallen" — das wäre faktisch falsch und im Browser nachprüfbar.

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

**Schritt 1: Business-Type-Detection (Pflicht vor Subject-Wahl)**

Bestimme den Business-Typ aus drei Signalquellen (Reihenfolge = Priorität):

| Priorität | Quelle | Match | Typ |
|---|---|---|---|
| 1 | Input- oder Target-Domain enthält Substring | `studio` | **Studio** |
| 1 | " | `shop`, `kaufen`, `store`, `versand` | **Shop** |
| 1 | " | `praxis` | **Praxis** |
| 1 | " | `salon` | **Salon** |
| 1 | " | `spa` | **Spa** |
| 1 | " | `center`, `zentrum` | **Center** |
| 2 | Impressum Rechtsform | `e.K.`, `GmbH & Co. KG` mit Shop-Kontext | **Shop** |
| 2 | Impressum Berufsbezeichnung | "Heilpraktiker", "Physiotherapeut", "Arzt", "Zahnarzt", "TCM" | **Praxis** |
| 2 | Impressum Berufsbezeichnung | "Friseurmeister", "Friseur", "Nagelstylist" | **Salon** |
| 3 | Firecrawl Root-Page Body | "Onlineshop", "Warenkorb", "Versandkosten", "in den Warenkorb" | **Shop** |
| 3 | Firecrawl Root-Page Body | "Termin buchen", "Sprechzeiten" | **Praxis** |
| 3 | Firecrawl Root-Page Body | "Kosmetikbehandlung", "Fitnesskurse", "Fotoshooting" | **Studio** |
| 3 | Firecrawl Root-Page Body | "Wellness", "Massage", "Sauna" | **Spa** |
| 3 | Firecrawl detected CMS | `Shopware`, `WooCommerce`, `Shopify`, `Magento` | **Shop** |
| Default | (kein Match) | — | **Unternehmen** |

Bei mehreren Treffern: höhere Priorität gewinnt. Bei Gleichstand auf Priorität 1: das spezifischere Token (`praxis` > `shop`, weil enger umrissen).

**Schritt 2: Subject + Anrede-Wording pro Typ**

| Typ | Subject | Body-Wording für "Ihr X" |
|---|---|---|
| Studio | `Kurze Frage zu Ihrem Studio in [ORT]` | "Ihr Studio" / "Ihres Studios" |
| Shop | `Kurze Frage zu Ihrem Shop in [ORT]` | "Ihr Shop" / "Ihres Shops" |
| Praxis | `Kurze Frage zu Ihrer Praxis in [ORT]` | "Ihre Praxis" / "Ihrer Praxis" |
| Salon | `Kurze Frage zu Ihrem Salon in [ORT]` | "Ihr Salon" / "Ihres Salons" |
| Spa | `Kurze Frage zu Ihrem Spa in [ORT]` | "Ihr Spa" / "Ihres Spas" |
| Center | `Kurze Frage zu Ihrem Center in [ORT]` | "Ihr Center" / "Ihres Centers" |
| Unternehmen | `Kurze Frage zu Ihrer Website` *(kein [ORT])* | "Ihre Website" / "Ihrer Website" |

**Strikte Regel:** NIEMALS "Studio" für einen Shop / "Shop" für eine Praxis verwenden — der Empfänger merkt sofort, dass die Mail nicht personalisiert ist. Im Zweifel "Unternehmen" + "Ihre Website" verwenden.

**Schritt 3: Format (Variante C)**

```
Betreff: <Subject aus Tabelle, mit [ORT] eingesetzt>

Sehr geehrte/r [NAME],

<2-3 stärkste verifizierte Befunde, formuliert als Beobachtungen — keine Wertung, keine Heilversprechen, keine Produkt-Aussagen. Jeder Befund 25-35 Wörter. Verwende Body-Wording aus der Typ-Tabelle wo es natürlich passt.>

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

**Befund-Selektion für Outreach-Hook (3 Filter, in dieser Reihenfolge):**

**Filter 1 — Verification:** Nur 2-Quellen-bestätigte Befunde qualifizieren. Unverifizierte raus.

**Filter 2 — Browser-Verifiability-Test (NEU, Pflicht):**

Für JEDEN Befund-Kandidaten beantworte: *"Kann der Empfänger das in unter 30 Sekunden im Browser selbst nachprüfen, ohne ein Tool oder eine API zu nutzen?"*

Zulässige Verifikations-Wege für den Empfänger:
- ✅ URL im Browser öffnen und HTTP-Antwort/Inhalt sehen
- ✅ Google-Suche `site:domain.de` oder den Domain-Namen suchen, SERP-Snippet anschauen
- ✅ Rechtsklick → "Seitenquelltext anzeigen" + Strg+F nach Pattern suchen
- ✅ DevTools öffnen und Network-Tab anschauen

NICHT zulässig (Befund-Out):
- ❌ Ubersuggest/Ahrefs/Semrush öffnen müssen
- ❌ PageSpeed-Insights laufen lassen müssen
- ❌ Crawl-Tool/Sitemap-Parser benutzen müssen
- ❌ API-Daten interpretieren müssen
- ❌ Daten über mehrere Monate vergleichen müssen ("vor 6 Monaten war es noch X")

**Beispiele:**

| Befund | Browser-verifizierbar in 30s? | Hook-tauglich? |
|---|---|---|
| Trailing-Slash 404: `/buecher` öffnen → 404 | ✅ ja | ✅ ja |
| Meta-Description-Platzhalter `#IndexMeta...#` in SERP | ✅ ja (google domain.de + SERP anschauen) | ✅ ja |
| Ubersuggest meldet Traffic 0 für 6 Monate | ❌ nein (braucht Ubersuggest) | ❌ nein (höchstens als "laut Tool-Analyse" framing) |
| PageSpeed LCP > 5s | ❌ nein (braucht PageSpeed API/Tool) | ❌ nein |
| DA 17 + nur 77 Ref-Domains | ❌ nein (braucht SEO-Tool) | ❌ nein |
| Footer "© 2002-2015" auf der Seite | ✅ ja (root öffnen, footer anschauen) | ✅ ja |
| Title-Tag generisch ("Startseite") | ✅ ja (Tab-Titel im Browser) | ✅ ja |

**Filter 3 — Severity-Sortierung** (für die verbleibenden Kandidaten):

```
severity_score = impact_weight + visibility_weight

impact_weight:
  + 3 wenn betrifft kritische Funktionalität (Routing/Auth/Kontakt kaputt)
  + 2 wenn betrifft Suchsichtbarkeit (Meta, Index, falsche URL-Varianten)
  + 1 wenn betrifft Wartung/Aktualität (alter Footer, alte Snippets)
visibility_weight:
  + 2 wenn in Google-SERP direkt sichtbar
  + 1 wenn beim direkten Domain-Besuch sichtbar
  + 0 wenn nur bei spezifischen URL-Tests sichtbar
```

Wähle die Top 2-3 nach `severity_score`. Bei Gleichstand bevorzuge unterschiedliche Befund-Kategorien.

**Self-Plausibility-Check (Pflicht vor Schreiben des Hook-Texts):**

Nachdem 2-3 Befunde selektiert sind, für JEDEN Befund einen letzten Check durchführen:

1. **"Kann der Empfänger das sofort selbst prüfen und bestätigen?"** → wenn NEIN: Befund aus Hook entfernen, oder mit "laut SEO-Analyse" / "laut Crawl-Daten" kennzeichnen (dann ist es transparenter, aber schwächer)
2. **"Würde der Empfänger nach der eigenen Prüfung sagen 'stimmt'?"** → wenn NEIN: Befund-Formulierung präzisieren. Beispiel: "Alle Kategorien kaputt" ist widerlegbar (Slash-Variante geht), `"Einige URL-Varianten laufen ins Leere"` ist nicht widerlegbar.
3. **"Ist die Formulierung HWG-konform?"** → wenn NEIN: umformulieren oder Befund streichen.
4. **"Klingt das nach Beobachtung oder nach Wertung?"** → Beobachtungen werden eher akzeptiert ("Die Domain leitet auf X weiter") als Wertungen ("Ihre SEO ist kaputt").

Falls nach allen Filtern nur 1 Befund übrigbleibt: Outreach-Mail trotzdem schreiben, mit nur 1 Befund + stärkerer Ausarbeitung. Falls 0 Befunde: Outreach-Mail nicht generieren (siehe Edge-Case).

**Befund-Formulierungs-Templates:**

Jeder Befund wird konkret und prüfbar formuliert:

| Befund-Typ | Template |
|---|---|
| Trailing-Slash-Problem (Shopware) | "Einige URL-Varianten Ihres Shops laufen ins Leere — Google kann diese Kategorien nicht direkt crawlen, obwohl die Navigation über die Startseite funktioniert. Das ist ein typisches Trailing-Slash-Problem bei Shopware." |
| Trailing-Slash-Problem (generisch) | "Einige URL-Varianten Ihrer Website laufen ins Leere — wenn Nutzer oder Google die Kategorien direkt aufrufen, erscheint eine Fehlerseite, obwohl die Navigation über die Startseite funktioniert." |
| Kaputte URLs (kein Slash-Workaround, beide Varianten 404) | "Beim Aufruf von <code>www.[domain]/[pfad]</code> erscheint statt der Inhalts-Seite eine 404-Fehlerseite — das betrifft auch <code>/[pfad2]</code> und [n] weitere Bereiche." |
| Meta-Description Platzhalter | "In der Google-Suche zeigt sich bei Ihrer Startseite der unausgefüllte Platzhalter-Text <code>#IndexMetaDescriptionStandard#</code> statt einer Beschreibung." |
| Deindexed | "Ihre Domain rankt aktuell für 0 Keywords bei Google — vor [N] Monaten waren es noch [M]." |
| PageSpeed kritisch | "Die mobile Ladezeit Ihrer Startseite liegt bei [LCP] (Empfehlung: < 2,5 s)." |
| Redirect-Inkonsistenz | "Die Domain <code>[input]</code> leitet weiter zu <code>[target]</code> — Nutzer und Backlinks landen auf einer anderen URL als erwartet." |

**Trailing-Slash-Detection (vor Befund-Formulierung):**

Wenn eine URL ohne trailing Slash als kaputt verifiziert wurde, prüfe IMMER ob die Variante mit Slash funktioniert:

```bash
curl -sI --max-time 10 "https://<target>/<pfad>"  # ohne Slash
curl -sI --max-time 10 "https://<target>/<pfad>/" # mit Slash
```

Wenn no-slash 404 **und** with-slash 200 → **Trailing-Slash-Problem-Template** verwenden, NICHT "URL kaputt"-Template. Das ist faktisch korrekter und nicht widerlegbar — der Empfänger kann mit Slash öffnen und sieht, dass es geht, aber das ändert nichts daran, dass die no-slash-Variante in Google-SERPs/Backlinks/direkten Aufrufen 404 wirft.

CMS-Detection für Template-Wahl:
- Shopware: `x-content-digest`-Header oder `/shopware`-Pfade oder Footer "Powered by Shopware"
- WooCommerce: `?wc-ajax=` URLs oder `/wp-content/plugins/woocommerce`
- Falls keins erkannt → generische Template-Variante verwenden

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

## Health-Score Heuristik (0-10) — Recalibrated

**Kern-Regel:** Nur **verifizierte** Befunde gehen in den Score. Unverifizierte Befunde werden im Report transparent gemacht, beeinflussen den Score aber nicht.

**Score-Skala (Trennschärfe wichtig):**

| Score | Bedeutung |
|---|---|
| **1-2/10** | **Domain technisch tot** — Root antwortet nicht, kein Index, keine erreichbare Hauptseite |
| **3-4/10** | **Schwere technische Probleme**, aber Shop/Website läuft grundsätzlich (Hauptseite erreichbar, Kontakt möglich) |
| **5-6/10** | **Ungepflegt**, mehrere SEO-Fehler, technische Schwächen — aber funktionsfähig und nutzbar |
| **7-8/10** | **Kleinere Probleme**, grundsätzlich solide aufgestellt |
| **9-10/10** | **Gut aufgestellt**, kaum Verbesserungspotential |

**Wichtig:** "ungepflegt ≠ ausgefallen". Eine Domain mit kaputtem Meta-Tag, Trailing-Slash-Problem, aber funktionierendem Shop ist 4-5/10, nicht 1-2/10.

Start bei 5, addiere/subtrahiere:

| Signal | Δ |
|---|---|
| **Verfügbarkeit** | |
| Root-Page antwortet HTTP 200 mit echtem Inhalt | +0 (Baseline-Voraussetzung) |
| Root-Page antwortet nicht oder 5xx | −5 (= technisch tot) |
| Kontakt-Seite / Impressum erreichbar | +0 (Baseline) |
| Kontakt nicht erreichbar | −2 |
| **Authority** | |
| DA ≥ 30 | +2 |
| DA ≥ 15 | +1 |
| DA < 10 | −1 |
| **Ranking** | |
| Ranking-KWs ≥ 50 | +2 |
| Ranking-KWs 5-49 | +1 |
| Ranking-KWs = 0 **UND** Google `site:` = 0 (verifiziert deindexiert) | −3 |
| Ranking-KWs = 0 **aber** Google `site:` ≥ 1 (ranking-tot, indexiert) | −2 |
| Traffic-Trend wachsend (+15% MoM) | +1 |
| Traffic-Trend fallend (−15% MoM) | −1 |
| **On-Page** | |
| URL-Normalisierungsproblem (Trailing-Slash, no-slash 404, with-slash 200) | −1 (mittel, Inhalte da) |
| Echte 404 auf Haupt-Bereichen (beide URL-Varianten 404) | −3 (hoch, Inhalte fehlen) |
| Meta-Description-Platzhalter verifiziert | −1 |
| Title-Tag generisch oder leer auf Haupt-Pages | −1 |
| **Performance** | |
| PageSpeed Performance < 30 | −1 |
| PageSpeed Performance > 80 | +1 |
| **Link-Profil** | |
| Gov/Edu Backlinks > 0 | +1 |
| Follow-Ratio > 60% (bei ≥ 30 Ref-Domains) | +1 |

Cap bei 0 und 10.

**Plausibilitäts-Gate nach Berechnung:**

Nach Score-Berechnung prüfe:
- Wenn Root-Page funktioniert UND mindestens eine Sub-Page (Impressum/Kontakt) erreichbar → Score MUSS ≥ 3 sein (egal wie viele SEO-Probleme). Domain ist nicht "tot".
- Wenn Score < 3 und Root antwortet 200 → Score auf 3 anheben + im Verdict notieren "Score-Lift: Hauptseite funktioniert, daher kein 1-2-Score".

Diese Korrektur verhindert dass ungepflegte aber lauffähige Shops als "tot" eingestuft werden.

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
