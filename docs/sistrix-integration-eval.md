# Sistrix-Integration für /audit — Evaluation & Entscheidung

**Datum:** 2026-05-12
**Status:** ✅ Integriert (Skill v5)

## TL;DR

- **API paid-only** (Plus-Paket+, Credit-System) → für unsere Use-Case unbrauchbar
- **`sichtbarkeitsindex.de`** ist nur ein **Lead-Capture-Formular** (kein Daten-HTML)
- **`app.sistrix.com/de/visibility-index?domain=X`** liefert den **Sichtbarkeitsindex direkt im gerenderten HTML** — kostenlos, 25 Abfragen/IP/Tag, mehr nach Free-Registrierung
- ✅ **Integration via Firecrawl-Scrape** umgesetzt — wird als 3rd-Source-Cross-Verify gegen Ubersuggest geschaltet

## Recherche-Ergebnisse

### 1. Sistrix-API (api.sistrix.com)

| Aspekt | Befund |
|---|---|
| Verfügbar ab | Plus-Paket (kostenpflichtig) |
| Auth | Personal API Key (im Account-Bereich generierbar) |
| Pricing | Credit-System, wöchentliche Allokation |
| Free-Tier | **Keine** — kein Free-Quota für API-Zugang |
| Relevante Endpunkte | `/credits`, `/domain`, `/keyword`, `/links`, `/ai`, `/project` |
| Wirklich für Plus? | "Basic functions including visibility index" laut Doku — aber Plus selbst kostet ~100€+/Monat |

**Verdict:** ❌ Nicht für unsere Use-Case. Wir wollen 3rd-source-Cross-Verify, nicht primäre Datenquelle. Cost/Benefit stimmt nicht.

### 2. Öffentliche Tools

#### 2a. `sichtbarkeitsindex.de` — ❌ Useless

- HTML enthält **keine echten Daten**, selbst mit `?d=domain.de` URL-Parameter
- Das Formular ist nur ein Funnel zu `app.sistrix.com/de/visibility-index?domain=X`, das in neuem Tab geöffnet wird
- Reines Lead-Capture für die Sistrix-Toolbox

#### 2b. `app.sistrix.com/de/visibility-index?domain=X` — ✅ **GOLDFUND**

Firecrawl-Scrape mit `--wait-for 4000` liefert (am Beispiel `vitaminbude.de`):

```
Sichtbarkeitsindex Mobil
0,0000
0%
| Aktualisiert | 12.05.2026 13:50 |
```

| Daten-Punkt | Wert (vitaminbude.de) |
|---|---|
| Sichtbarkeitsindex Mobil (DE) | **0,0000** |
| Update-Frische | 12.05.2026 13:50 (heute, taggleich) |
| Länder-Support | 40 (de, at, ch, nl, fr, it, es, pl, gb, us, ...) via Country-Selector |
| Frei-Quota | **25 Abfragen/IP/Tag ohne Login**, mehr mit Free-Account |
| Rate-Limit-Verhalten | Zeigt Registrierungs-Aufforderung statt Daten |

**Validierung gegen unsere bestehenden Daten:**
- Ubersuggest: 0 Ranking-KWs, 0 Traffic → Sistrix: 0,0000 Sichtbarkeitsindex ✅ **konsistent**
- Triple-Source-Verifikation: Ubersuggest + Google `site:`-Search + Sistrix → höchste Confidence

#### 2c. Andere kostenlose Sistrix-Tools

- `sistrix.de/kostenlose-tools/` — Sammlung Free-Tools (SERP-Snippet-Generator, Hreflang-Validator, etc.). Für unsere Audit-Pipeline nicht direkt relevant — die liefern keine Domain-Bewertung, sondern Utilities.

### 3. Firecrawl-Kompatibilität

- ✅ Page lädt mit `wait-for=4000ms` → Sichtbarkeits-Werte werden via JS gerendert
- ✅ Markdown-Output enthält die Werte parsebar
- ✅ Firecrawl-Cost: 1 Credit pro Abfrage (Standard-Scrape)
- ⚠️ Bei `--only-main-content=true` werden Werte teilweise rausgestrippt — `--only-main-content=false` setzen

## Entscheidung

**INTEGRATION JA** — Sistrix-Sichtbarkeitsindex als 3. Datenquelle in /audit-Phase-1.

### Implementierung (im Skill v5)

In `.claude/skills/audit.md` ergänzt:

1. **Phase 1, Call 8:** Firecrawl-Scrape auf `https://app.sistrix.com/de/visibility-index?domain=<input>` mit `--wait-for 4000`
2. **Cross-Verify-Matrix:** Neue Zeile "Sichtbarkeit-Verlust (Triple-Source)" — Ubersuggest=0 + Sistrix=0 → höchstes Vertrauen
3. **Report-Template:** Neue Sektion "Sichtbarkeit (Sistrix, 3rd-Party Cross-Source)" mit Sichtbarkeitsindex + Update-Datum
4. **Browser-Verifiability-Filter:** Sistrix-Befund ist ✅ browser-verifiable in <30s (Empfänger öffnet die URL und sieht 0,0000)
5. **Befund-Template:** "Wenn Sie Ihre Domain bei `app.sistrix.com/de/visibility-index?domain=[input]` prüfen, zeigt SISTRIX einen Sichtbarkeitsindex von 0,0000 an — Google rankt Ihre Seite aktuell für keine messbaren Suchbegriffe."

### Was Sistrix in der Outreach-Mail bringt

Für die Hook-Generierung ist Sistrix **wertvoll**, weil:
- Browser-verifizierbar (Empfänger kann selbst auf die Sistrix-URL klicken)
- 3rd-Party-Quelle (nicht "unser Tool", sondern Marktführer-Tool)
- Sistrix ist **Sistrix-Trademark** im SEO-Bereich → emotionaler Wert höher als "Ubersuggest sagt..."

**Konkret für vitaminbude.de:** Der Hook könnte jetzt zusätzlich enthalten:
> "Auch bei SISTRIX (`app.sistrix.com/de/visibility-index?domain=vitaminbude.de`) zeigt der Sichtbarkeitsindex aktuell 0,0000 — also keine messbare Sichtbarkeit in Google."

Das wäre der **bisher stärkste, public-verifizierbare Befund**, weil:
- Quelle = der wichtigste SEO-Wert im DACH-Raum
- Hyperlink direkt in der Mail
- Wert ist eindeutig, nicht-interpretierbar (0,0000 = kein Argument)

## Rate-Limit-Strategie

| Use-Case | Tagesabfragen | Strategie |
|---|---|---|
| 1 Audit/Tag | 1 | ✅ ohne Login |
| 5-10 Audits/Tag | 5-10 | ✅ ohne Login (Buffer für Re-Audits) |
| 20-25 Audits/Tag | 20-25 | ⚠️ Grenze — Free-Account registrieren |
| > 25 Audits/Tag | > 25 | ❌ Free-Account + ggf. Plus für API |

Für maxcontentseo aktuell (ca. 1-3 Outreach-Audits/Tag) ist das **kein Bottleneck**.

## Risiken

1. **Anti-Scraping:** Sistrix könnte JS-Challenges einbauen — Firecrawl-Scrape würde scheitern. Bisher (12.05.2026) funktioniert es.
2. **HTML-Struktur-Änderung:** Wenn Sistrix das Layout ändert, müssen wir den Parser anpassen. Skill enthält jetzt das aktuelle Pattern — Update bei Bedarf.
3. **TOS-Konformität:** Public-Page-Scraping ist rechtlich graustabil. Bei sehr hoher Last über mehrere IPs kann das Sistrix verärgern. **Bei 1-3 Abfragen/Tag** — uninteressant für sie.

## Nächste Schritte (optional, nicht autorun-pflicht)

1. ✅ Skill v5 integriert
2. ⏳ Beim nächsten echten /audit-Run testen ob die Sistrix-Daten korrekt geparst werden
3. ⏳ Wenn ja: Sistrix-Hook in die nächste Outreach-Mail einbauen (vitaminbude-de-v4)
4. ⏳ Bei Bedarf: Free-Account auf sistrix.de registrieren für höhere Quota

---

*Recherchiert + integriert via `/autorun`-Mode am 2026-05-12*
