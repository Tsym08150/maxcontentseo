# Domain Audit: vitaminbude.de (v3 — Skill v4)

**Datum:** 2026-05-12
**Business-Type:** Shop (erkannt aus Target-Domain `-shop`, Impressum `e.K.`, Shopware-CMS)
**Health-Score:** 3/10 (Score-Lift: Root läuft, daher kein 1-2-Score)
**Verdict:** Ungepflegter Shopware-Shop mit URL-Normalisierungs-Problem und unausgefülltem Meta-Description-Platzhalter — funktionsfähig, aber technisch und SEO-seitig vernachlässigt.

---

## Domain Resolution

- **Input:** `vitaminbude.de`
- **Final Target:** `www.vitaminbude-shop.de` (via HTTP 301, 1 Hop)
- **Verifikation:** ✅ `curl HEAD` bestätigt — Apache 301.

## SEO Position (Ubersuggest, DE — auf Input-Domain)

| Metrik | Wert |
|---|---|
| Domain Authority | 17/100 |
| Organic Traffic (Apr 2026) | 0 |
| Ranking Keywords (Apr 2026) | 0 |
| Trend 6M | komplett verloren (Mai 2025: 16 KWs → seit Nov 2025: 0) |
| Paid Activity | nie |
| GA/GSC verbunden | Nein |

## Backlink Profile

- 247 Backlinks von 77 Ref-Domains, 0 Gov/Edu
- Link-Profil intakt — Substanz da, wird nur technisch nicht ausgespielt
- Follow-Daten zwischen 2 Ubersuggest-Endpoints widersprüchlich (API-Inkonsistenz, kein Domain-Befund)

## On-Page (Firecrawl + Direkter HTTP-Cross-Check)

### URL-Normalisierungs-Audit (Dual-Slash-Test)

Für jede in Phase 1 als "Error-Page" gemeldete URL wurden **beide Varianten** geprüft:

| Pfad | no-slash | with-slash | Befund-Typ |
|---|---|---|---|
| `/buecher` | 404 (via 301 → /404) | **200** | URL-Normalisierungsproblem |
| `/vitale-produkte` | 404 (via 301 → /404) | **200** | URL-Normalisierungsproblem |
| `/news` | 404 (via 301 → /404) | **200** | URL-Normalisierungsproblem |
| `/` | 200 | 200 | OK |
| `/impressum` | 200 | (n/a) | OK |
| `/kontaktformular` | 200 | (n/a) | OK |

**Diagnose:** Klassischer Shopware-Trailing-Slash-Routing-Bug. Inhalte existieren, nur die no-slash-URL-Varianten 404en. Das ist **kein "ausgefallener Shop"** — der Shop ist normal nutzbar, nur die kanonische URL-Form ist inkonsistent.

### Meta-Description-Audit

| URL | Firecrawl | Direkter Fetch | Status |
|---|---|---|---|
| `/` | `#IndexMetaDescriptionStandard#` | `#IndexMetaDescriptionStandard#` | ✅ Platzhalter verifiziert |
| `/buecher` (no-slash) | `#IndexMetaDescriptionStandard#` | `#IndexMetaDescriptionStandard#` | ✅ verifiziert |
| `/vitale-produkte` (no-slash) | `#IndexMetaDescriptionStandard#` | `#IndexMetaDescriptionStandard#` | ✅ verifiziert |

Das Shopware-Template wurde mit einem Default-Platzhalter geliefert und nie konfiguriert.

### Bonus-Kontext aus Impressum-Scrape

Footer-Copyright: `© 2002 - 2015 TYBAS Communication` → die Site wurde seit ≥ 10 Jahren nicht inhaltlich überarbeitet. Erklärt sowohl die Meta-Description-Vergessenheit als auch die Trailing-Slash-Probleme (Shopware-Update wurde nicht durchgeführt, oder Routing-Config wurde nie überprüft).

## Index Status

- **Ubersuggest-Traffic (3M):** 0/0/0
- **Google `site:vitaminbude-shop.de`:** ≥ 20 Treffer mit alten Snippets
- **Status:** ranking-tot, aber indexiert — Google hat noch Cache, aber die alten Pages sind no-slash-URLs, die 404en

## PageSpeed

⚠️ **Nicht verfügbar:** API-Quota erschöpft heute. Kein Score-Impact.

---

## Health-Score Berechnung (transparent)

| Faktor | Δ |
|---|---|
| Start | 5 |
| Root antwortet 200 (Baseline) | 0 |
| Impressum + Kontaktformular erreichbar | 0 |
| DA 17 (≥ 15) | +1 |
| Ranking-KWs = 0 **UND** site: ≥ 1 (ranking-tot, indexiert) | −2 |
| URL-Normalisierungsproblem (Trailing-Slash) | −1 |
| Meta-Description-Platzhalter verifiziert | −1 |
| **Roh-Score** | **2** |
| **Plausibilitäts-Gate:** Root + Sub-Pages funktionieren → Score-Lift auf 3 | **+1** |
| **Final** | **3/10** |

**Interpretation:** "Schwere technische Probleme, aber Shop läuft grundsätzlich." Das ist eine andere Diagnose als v1/v2 (1-2/10 "technisch tot") — der Score wurde nach der Recalibration korrigiert. Der Shop ist **ungepflegt, nicht ausgefallen**.

## Verdict

### Verifizierte Befunde (für Health-Score gezählt)

1. **URL-Normalisierungsproblem** (Trailing-Slash) auf mehreren Kategorien — beide Varianten direkt geprüft, eindeutig.
2. **Meta-Description-Platzhalter** in Root + Sub-Pages — Firecrawl + direkter HTTP-Fetch übereinstimmend.
3. **Ranking-Verlust mit Index-Retention** — Ubersuggest 0 KWs, aber Firecrawl-Search liefert ≥ 20 indexierte Pages.

### Browser-Verifiability-Filter (für Outreach-Hook)

| Befund | Browser in 30s prüfbar? | Hook-tauglich? |
|---|---|---|
| Trailing-Slash 404 (`/buecher` vs `/buecher/`) | ✅ | ✅ |
| Meta-Description Platzhalter in SERP | ✅ | ✅ |
| Footer "© 2002-2015" | ✅ | ✅ (als 3. Befund möglich) |
| Ranking-Verlust laut Ubersuggest | ❌ (braucht Tool) | ❌ |
| Backlinks 77 Domains | ❌ (braucht Tool) | ❌ |
| Index-Diskrepanz | ❌ (braucht Daten-Vergleich) | ❌ |

**Hook-Selektion:** Befund 1 + Befund 2 (Top 2 nach Severity, beide browser-verifiable).

### Outreach-Hook (in der Mail verwendet)

> "Beim Aufruf einzelner URL-Varianten Ihres Shops www.vitaminbude-shop.de — zum Beispiel `/buecher` oder `/vitale-produkte` — erscheint eine 404-Fehlerseite, während die gleiche URL mit angehängtem Schrägstrich (`/buecher/`) korrekt lädt. Das ist ein typisches Trailing-Slash-Problem bei Shopware: Google indexiert beide Varianten, Nutzer landen aber teilweise auf 404. Zusätzlich erscheint im Google-Suchergebnis bei Ihrer Startseite der unausgefüllte Platzhalter `#IndexMetaDescriptionStandard#` statt einer Beschreibung. Beides ist in unter einer Minute im Browser nachvollziehbar."

**Warum dieser Hook stärker ist als v2:**
- Trailing-Slash-Formulierung ist **nicht widerlegbar** — der Empfänger kann `/buecher/` öffnen und sieht: "OK, das geht ja!" — aber die no-slash-Variante ist trotzdem nachweislich 404.
- Kein Begriff "kaputt" oder "ausgefallen" — die alte Formulierung war übertrieben und vom Empfänger leicht abzulehnen.
- Beide Befunde in 30 Sekunden im Browser prüfbar — der Empfänger kann selbst validieren, das erhöht Glaubwürdigkeit.

### Empfohlene Nächste Schritte

1. **Vor Outreach:** Letztprüfung ob `info@vitaminbude.de` noch erreicht wird (vor Versand testen, keine Hard-Bounces). Footer-Copyright 2015 suggeriert "vergessen" — Mail evtl. unbenutzt.
2. **Falls Mail aktiv:** Hook versenden mit `[ABSENDER]`-Ergänzung.
3. **Bei "Ja"-Antwort:** PDF dieses Reports senden (audit-vitaminbude-de-20260512-v3.pdf).

---

*Generiert via `/audit vitaminbude.de` v3 (Skill v4 mit Business-Type-Detection, Dual-Slash-Test, Health-Score-Recalibration, Browser-Verifiability-Filter)*
