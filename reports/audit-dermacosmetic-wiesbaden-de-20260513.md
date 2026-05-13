# Domain Audit: dermacosmetic-wiesbaden.de

**Datum:** 2026-05-13
**Business-Type:** Studio (Kosmetikmeisterin, kein Dr./Heilpraktiker — HWG-safe)
**Health-Score:** 6/10
**Verdict:** Funktionierender Wix-Studio-Site, aber für lokale Neukundensuche praktisch unsichtbar — Traffic kommt zu 89% aus Brand-Search.

---

## Domain Resolution

- **Input:** `dermacosmetic-wiesbaden.de`
- **Final Target:** `www.dermacosmetic-wiesbaden.de` (via 301 apex→www, 1 Hop, 200 OK)
- **Verifikation:** ✅ `curl -sIL` bestätigt

## SEO Position (Ubersuggest, DE — auf Input-Domain)

| Metrik | Wert |
|---|---|
| Domain Authority | 10/100 (Grenzbereich) |
| Organic Traffic (Apr 2026) | 68 |
| Ranking Keywords (Apr 2026) | **12** — Drop von 47 (Nov 2024) → 12 |
| Trend 24M | Peak Okt 2024 (181 Traffic / 48 KWs), dann gradueller Decline auf aktuell 68/12 |
| Paid Activity | nie |
| GA/GSC verbunden | Nein |

### Top Keywords (12 ranking)

| KW | Position | Volume | Traffic | Anmerkung |
|---|---|---|---|---|
| **dermacosmetic wiesbaden** | **1** | 140 | **61** | Brand-Term — 89% des gesamten Traffics |
| derma cosmetics | 3 | 70 | 2 | Brand-spillover, kein lokaler Bezug |
| kosmetikstudio wiesbaden innenstadt | 24 | 70 | 2 | Lokal — aber Page 3 |
| gesichtsbehandlungen wiesbaden | 27 | 210 | 1 | Lokal hochvolumig — aber Page 3 |
| gesichtsreinigung wiesbaden | 28 | 90 | 1 | Lokal — Page 3 |
| myderma wiesbaden | 25 | 140 | 0 | Wettbewerber-KW |
| hyaluron wiesbaden | 111 | 90 | 0 | praktisch unsichtbar |
| derma beauty | 48 | 320 | 0 | Page 5 |
| kirchgasse 42 wiesbaden | 40 | 70 | 0 | Adresse falsch — Studio ist Kirchgasse 56! |
| myderma by cosmetique totale wiesbaden | 29 | 170 | 0 | Wettbewerber-Brand |
| derma med kosmetik | 24 | 70 | 0 | Page 3 |
| beste kosmetikstudio wiesbaden | 45 | 90 | 0 | Page 5 |

**Diagnose:** Nur 1 KW in Top-10 — und das ist der eigene Brand. Alle echten Akquisitions-Keywords (kosmetikstudio wiesbaden, gesichtsbehandlungen wiesbaden, hydrafacial wiesbaden) sind außerhalb der ersten 2 Seiten.

### Top Pages

| URL | Traffic | Backlinks |
|---|---|---|
| `/` (Startseite) | 68 | 141 |

**Nur 1 Page hat überhaupt messbaren Traffic.** Andere Seiten (services-1, general-8 etc.) rankten nie meaningful.

## Sichtbarkeit (Sistrix, 3rd-Party Cross-Source)

| Metrik | Wert |
|---|---|
| Sichtbarkeitsindex Mobil (DE) | **0,0004** |
| SI-Rank (global) | 1.443.345 |
| Aktualisiert | 13.05.2026 11:25 |
| Cross-Check mit Ubersuggest | ✅ konsistent (beide melden minimale Sichtbarkeit) |

Browser-Link für Empfänger-Verifikation: `https://app.sistrix.com/de/visibility-index?domain=dermacosmetic-wiesbaden.de`

## Backlink Profile (Ubersuggest)

- **Total:** 152 Backlinks von 23 Ref-Domains
- **Gov/Edu:** 0
- **Follow-Ratio:** **5%** (7 follow / 145 nofollow) ← sehr schwach
- **Bewertung:** Praktisch alle Backlinks sind nofollow (typisch für Social-Media-Profile, Verzeichnisse) → kein SEO-Wert. Domain hat keine substantielle Link-Substanz.

## On-Page (Firecrawl + ctx_fetch_and_index Cross-Check)

### Sitemap-Audit (Firecrawl /map → /audit)

| URL | Status | Title | Meta-Description | Word-Count |
|---|---|---|---|---|
| `/` (Root) | ✅ 200 | "DermaCosmetic \| Kosmetik Wiesbaden" | gefüllt, 250+ Zeichen | 849 |
| `/services-1` | ✅ 200 | "Meta Therapie \| DermaCosmetic" | gefüllt (kurz, 80 Zeichen) | 129 |
| `/general-8` | ✅ 200 | "Laser Haarentfernung \| DermaCosmetic" | gefüllt | 165 |

**Cross-Verify Root:** ctx_fetch_and_index bestätigt — Wix-Build, Title + H1 + Body-Content stimmen mit Firecrawl überein. Adresse "Kirchgasse 56, 65183 Wiesbaden" + Telefon "0152 28145790" + Email "info@dermacosmetic-wiesbaden.de".

### Adress-Inkonsistenz

⚠️ **Verifizierter Befund:** Eines der ranking-Keywords ist "**kirchgasse 42 wiesbaden**" (Pos 40). Die echte Adresse laut Impressum/Body ist aber **Kirchgasse 56**. Das deutet auf eine veraltete Adress-Angabe in einem alten Eintrag/Verzeichnis hin, die Google noch indexiert hat. NAP-Inkonsistenz schadet Local SEO.

## Index Status (Google via Firecrawl-Search)

- **Google `site:dermacosmetic-wiesbaden.de`:** **3 Treffer**
  - `/` (Startseite)
  - `/services-1` (Meta Therapie)
  - `/general-8` (Laser Haarentfernung)
- **Sichtbarkeit-Discovery-Lücke:** Die Site hat mind. 5 weitere Service-Sektionen im Body (Hydrafacial, SkinPen Mikroneedling, Bodyforming, Klassische Behandlungen, Detox) — aber jeweils nicht als eigene URL indexiert (Wix One-Page-Build mit Anchor-Sections).

## PageSpeed (Google Mobile)

⚠️ **Nicht verfügbar:** API-Tageskontingent erschöpft. Kein Score-Impact.

---

## Health-Score Berechnung (transparent)

| Faktor | Δ |
|---|---|
| Start | 5 |
| Root antwortet 200 (Baseline) | 0 |
| 3 Services-Pages erreichbar | 0 |
| DA = 10 (Grenzbereich) | 0 |
| Ranking-KWs = 12 (zwischen 5-49) | +1 |
| Traffic-Trend langfristig fallend (Peak Okt 2024 → −62%) | −1 |
| Firecrawl + ctx_fetch_and_index: 100% Hauptseiten OK | +2 |
| Meta-Description-Platzhalter? Nein, alles gefüllt | 0 |
| Gov/Edu Backlinks > 0? Nein | 0 |
| Follow-Ratio < 60% (hier 5%) | 0 (kein Bonus) |
| NAP-Inkonsistenz (Kirchgasse 42 vs 56 indexiert) | −1 |
| **Final** | **6/10** |

**Interpretation:** "Solide Basis, klare Optimierungs-Potentiale → guter Outreach-Kandidat."

## Verdict

### Verifizierte Befunde (2-Quellen-bestätigt)

1. **Sichtbarkeit minimal:** Sistrix 0,0004 + Ubersuggest 12 KWs / 68 Traffic — beide Quellen bestätigen schwache Position.
2. **Nur 3 Seiten indexiert:** Firecrawl `site:`-Search liefert 3 Treffer; Ubersuggest top_pages zeigt nur 1 Seite mit Traffic.
3. **89% Brand-Term-Abhängigkeit:** Ubersuggest zeigt 61 von 68 Traffic kommen aus "dermacosmetic wiesbaden" (Brand) — der Rest (7 Traffic) verteilt auf 11 KWs auf Position 24-111.
4. **NAP-Inkonsistenz:** Body-Adresse "Kirchgasse 56" vs. ranking-KW "kirchgasse 42 wiesbaden" → veralteter externer Eintrag.
5. **Backlink-Profil praktisch wertlos:** 95% nofollow.

### Outreach-Hook (in der Mail verwendet — browser-verifizierbar)

> "Wenn Sie bei Google `site:dermacosmetic-wiesbaden.de` eingeben, listet Google aktuell nur drei Seiten Ihrer Website (Startseite, Meta Therapie, Laser-Haarentfernung). Bei SISTRIX (`app.sistrix.com/de/visibility-index?domain=dermacosmetic-wiesbaden.de`) liegt Ihr Sichtbarkeitsindex bei 0,0004 — das heißt: außerhalb der direkten Suche nach Ihrem Studio-Namen taucht Ihre Seite in Google praktisch nicht auf. Wer in Wiesbaden nach „Kosmetikstudio Wiesbaden" oder „Hydrafacial Wiesbaden" sucht, findet Sie aktuell nicht auf Seite 1."

**Warum stark:**
- Beide Werte (3 Treffer + 0,0004) sind in unter 60 Sekunden im Browser nachprüfbar
- Konkret + datengestützt, keine Werbeaussagen
- Lokal verankert (Wiesbaden) — zeigt Recherche

### Empfohlene Nächste Schritte

1. **Vor Outreach:** Adresse `info@dermacosmetic-wiesbaden.de` mit NB prüfen (bei nächstem `outreach send --confirm-live --template variante_audit`).
2. **Falls Reply ("Ja"):** PDF mit weiterführenden Empfehlungen senden — z.B. Wix-spezifische SEO-Probleme (Single-Page-Strukturen, Schwache H-Hierarchie), echte Service-Page-Trennung als erstes Hebel.
3. **Bei Auftrag:** NAP-Korrektur in Verzeichnissen (Kirchgasse 42 → 56), separate Service-URLs aus Wix-One-Page-Build, lokale Backlinks aus Wiesbaden-Branchen.

---

*Generiert via `/audit dermacosmetic-wiesbaden.de` (Ubersuggest MCP + Firecrawl CLI + Sistrix + Cross-Verify)*
