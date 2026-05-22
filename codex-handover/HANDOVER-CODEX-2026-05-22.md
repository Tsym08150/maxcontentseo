# Codex-Handover — Frankfurt_Umland Tranche 2026-05-22 (v2 — path-portable)

> **Was geändert (v1 → v2, 2026-05-22):**
> v1 referenzierte `D:\000 SEO Business\…`-Pfade, die auf Codex' Maschine nicht existieren. Codex hat den Run korrekt unter den Stop-Regeln gestoppt (siehe `codex-goal-27-frankfurt-umland-handover-blocked.md`). **Diese Version v2** liefert alle nötigen Quellen **inline im `codex-handover/`-Ordner** und verwendet **relative Pfade** innerhalb des `maxcontentseo`-Repos (= `maxcontentseo-website` auf Codex-Maschine).

> **Zweck:** Übergabe an Codex zur (1) Stufe-1-Recherche von 20 Neukontakten und (2) Erstellung von 20 Follow-up-Drafts. Basis: frischer Lead-Tracker-Scan vom 2026-05-22 (Tab `Frankfurt_Umland`, 121 Zeilen).

> **Region-Scope:** Frankfurt_Umland (Fortsetzung Tranche C vom 21.05.2026).

---

## 0. Codex-Environment Map (NEU — bitte lesen, bevor du startest)

Codex und Claude Code arbeiten auf **unterschiedlichen Maschinen** mit unterschiedlichen Mount-Punkten desselben Git-Repos. Das hat den v1-Block ausgelöst.

| Was | Bei Codex (`C:\Users\MaxContentSeO\…`) | Bei Claude Code (`D:\000 SEO Business\…`) |
|-----|-----|-----|
| Haupt-Repo | `maxcontentseo-website\` | `maxcontentseo\` |
| Outreach-CLI | `maxcontentseo-website\outreach-cli\` | `maxcontentseo\outreach-cli\` |
| Diese Handover-Datei | `maxcontentseo-website\codex-handover\HANDOVER-CODEX-2026-05-22.md` | `maxcontentseo\codex-handover\HANDOVER-CODEX-2026-05-22.md` |
| Lead-Tracker-Scan (JSON) | `maxcontentseo-website\codex-handover\_scan_20260522.json` | `maxcontentseo\codex-handover\_scan_20260522.json` |
| Pre-Check-Skript | `maxcontentseo-website\codex-handover\precheck_sheet_status.py` (kopiert vom Original `Tools\precheck_sheet_status.py`) | `maxcontentseo\codex-handover\precheck_sheet_status.py` |
| CLAUDE.md (operativ verbindlich) | **`maxcontentseo-website\codex-handover\CLAUDE-extract.md`** (Inline-Auszug, Stand 2026-05-22) | `D:\000 SEO Business\CLAUDE.md` (Original) |

**Verbindlich:** Bei Konflikt zwischen `maxcontentseo-codex-assets\CLAUDE.md` (alt, Schmölln-Adresse) und `./CLAUDE-extract.md` (in diesem Bundle, neue Kirchheim-Adresse) — **`./CLAUDE-extract.md` gewinnt**. Die alte Assets-Kopie ist nicht synchronisiert.

**Pfad-Konvention in diesem Dokument:**
- `./xyz` = im selben `codex-handover/` Ordner.
- `../xyz` = eine Ebene höher (= im `maxcontentseo[-website]/` Repo-Root).
- Keine absoluten `D:\` oder `C:\`-Pfade als Pflichtquelle.

---

## 0.5 Offene Fragen aus Goal 27 — Antworten

| Codex-Frage | Antwort |
|---|---|
| Liegen CLAUDE.md, _scan, precheck unter anderem Pfad? | Ja — jetzt **inline in diesem Bundle** (relative Pfade siehe oben). |
| Soll ein Ersatz-Precheck verwendet werden? | Nein — `./precheck_sheet_status.py` ist 1:1 das Original. |
| Wie wird Sistrix-Test ausgeführt? | **Defer to Stufe 2.** Codex skipt Krit. 7 und flaggt jeden Lead `sistrix-pending`. Claude Code übernimmt Sistrix-Lookup vor Live-Send. Details §3. |
| Welche Outreach-CLI? | **Codex entscheidet selbst.** Vergleiche per `git log -1 --format=%cd` zwischen `maxcontentseo-website\outreach-cli` und der Schwesterkopie. Die mit dem jüngeren Commit nutzen. Bei Gleichstand: `maxcontentseo-website\outreach-cli`. |

---

## 1. Übersicht

| Bucket | Inhalt | Anzahl | Sortierung | Codex-Aufgabe |
|--------|--------|--------|------------|---------------|
| **A** | Follow-ups fällig (FOLLOWUP_AM ≤ 22.05., Recherche_Status = `Angeschrieben`) | 20 | nach FOLLOWUP_AM aufsteigend | Last-Touch-Drafts nach H5-Template rendern |
| **B** | Neukontakte (Recherche_Status = `Neu`, sendable, nicht im sent_log) | 20 | **Score aufsteigend (niedrigster zuerst)** | Stufe-1-Audit (Ubersuggest + Firecrawl, ohne Sistrix) |

**Sortierregel Bucket B ist ungewöhnlich:** Georg arbeitet Neukontakte vom niedrigsten Score nach oben ab. Reihenfolge in der Tabelle ist verbindlich — Codex bearbeitet von oben.

---

## 2. Pflicht-Pre-Checks (vor jedem Schritt)

Diese Checks sind nicht optional. Bei Treffer → STOPP, nicht weiterverarbeiten, Report mit Begründung.

1. **Sheet-Cross-Check** mit `./precheck_sheet_status.py` (im Bundle). Vor jedem Render/Send re-validieren, dass kein Lead in der Zwischenzeit auf `Bounce`, `Email-Ungültig` oder `Geantwortet*` umgesprungen ist. Aufruf:
   ```powershell
   py -3 ./precheck_sheet_status.py --leads <leads.csv> --dry-run
   ```
   Voraussetzung: Google-Sheet-Service-Account-Credentials erreichbar. Falls nicht: Goal-Stop + im Result-Report flaggen.
2. **Kette/Filiale?** → Lead aus Bucket B entfernen. Trigger-Wörter: `Kette`, `Filiale`, `Franchise`, `GmbH & Co`, `Group`, `Douglas`, `Nivea Haus`, `Laser Clinics`. (Bucket A wurde bereits gefiltert.)
3. **E-Mail-Verifikation (NeverBounce, Frische ≤ 7 Tage):**
   - Pflicht-Vorbedingung jedes Live-Sends — gilt für Bucket A.
   - Befehl: `py -m outreach_cli verify-emails --emails <liste>` (aus deinem outreach-cli-Pfad).
   - `invalid` / `disposable` → raus, Sheet auf `Email-Ungültig`. `risky` / `unknown` → konservativ skippen.
   - Verify-Datum in jeden Draft als Checklist-Item `[x] Email-Verifikation (NeverBounce) frisch (≤7 Tage, <YYYY-MM-DD>)` (verbatim — Layer-C-Parser im `one_shot_send.py` matcht auf `Email-Verifikation`; fehlt der Eintrag → Hardfail, exit 2).
   - Falls NeverBounce-Credentials auf Codex-Maschine fehlen: Codex skipt Bucket-A-Render und flaggt `verify-unavailable`. Claude Code übernimmt Verify vor Send.
4. **Brand-Traffic-Test (Krit. 7):** **DEFERRED to Stufe 2.** Codex flaggt jeden Bucket-B-Lead als `sistrix-pending` und vergibt einen Score `n/7` statt `n/8`. Claude Code macht den Sistrix-Lookup im Browser vor dem Live-Send und entscheidet final über DQ-Brand.
5. **DSGVO-Footer:** Body jeder Mail endet **verbatim** mit dem Drei-Block-Footer (Adresse + UWG/DSGVO-Hinweis + Opt-out). Quelle: `./CLAUDE-extract.md` §Pflicht-Footer. **Adresse: Hauptstr. 29, 85551 Kirchheim b. München** (NICHT mehr Schmölln).

---

## 3. Bucket A — 20 Follow-ups, Last-Touch-Drafts erstellen

**Kontext:** Diese 20 Leads wurden am 11.05.2026 erstmals angeschrieben, FOLLOWUP_AM 18.05. ist überschritten (heute = 22.05., also +4 Tage), kein Reply, keine Bounce.

### 3.1 Lead-Tabelle

(Quelle: `./_scan_20260522.json` → `bucket_A_followups_due`)

| # | Sheet-Z. | FOLLOWUP_AM | Score | Firma | Stadt | Entscheider | E-Mail | Website | SEO_Problem (Sheet) |
|---|----------|-------------|-------|-------|-------|-------------|--------|---------|---------------------|
| 1 | 12 | 18.05.2026 | 5 | Kosmetikstudio Oerder - Sabine Dietz | Koenigstein | Frau Dietz | info@kosmetik-oerder.de | https://www.kosmetik-oerder.de | Sehr guter lokaler Lead Website wirkt aelter Content/SEO-Ausbau naheliegend |
| 2 | 13 | 18.05.2026 | 5 | Soul&Skin | Langen | — | info@soulandskin.de | https://soulandskin.de | Moderner Beauty-Fit HydraFacial + Head Spa Lokale Optimierung Langen ausbaufaehig |
| 3 | 14 | 18.05.2026 | 5 | Maison Beaute | Dreieich | — | info@maison-beaute.de | https://maison-beaute.de | Medical-Beauty-Fokus Lokale Behandlungsseiten Medical Beauty Dreieich fehlen |
| 4 | 15 | 18.05.2026 | 5 | Lanora Kosmetikstudio | Neu-Isenburg | — | info@lanora.de | https://lanora.de | Apparative Kosmetik Mehrere Leistungen Einzelne Leistungs-Landingpages fehlen |
| 5 | 16 | 18.05.2026 | 5 | Vestina Kosmetikinstitut | Moerfelden-Walldorf | — | info@vestina-kosmetik.de | https://vestina-kosmetik.de | Hochwertiger Kosmetik-Fit Einzelne lokale Leistungsseiten Laser/Anti-Aging fehlen |
| 6 | 17 | 18.05.2026 | 5 | Profiderma Kosmetik | Darmstadt | — | info@profiderma.de | https://profiderma.de | Breites Geraete-Angebot Leistungsseiten vorhanden Wenig Ratgeber-/Blogstruktur |
| 7 | 18 | 18.05.2026 | 5 | La Perla Cosmetic | Darmstadt | — | info@laperla-cosmetic.de | https://www.laperla-cosmetic.de | BABOR Excellence Institut Hydrafacial-Seite vorhanden Blog/Ratgeberpotenzial offen |
| 8 | 19 | 18.05.2026 | 5 | LA PEAU - Sinem Kellner | Wiesbaden | Frau Kellner | kundenservice@la-peau.de | https://la-peau.de | Einzelinstitut apparative Kosmetik Lokale Leistungsseiten/Blog kaum sichtbar |
| 9 | 20 | 18.05.2026 | 5 | Wiesbaden Spa - Ludmila Bitter | Wiesbaden | Frau Bitter | info@wiesbaden-spa.de | https://wiesbaden-spa.de | Wellness-Lead lokale Marke Blog/Service-Content vermutlich schwach |
| 10 | 22 | 18.05.2026 | 5 | Beauty Floating | Bad Homburg | — | info@beautyfloating.de | https://beautyfloating.de | Floating + Kosmetik + Massage Kombi Content-Struktur ausbaufaehig |
| 11 | 24 | 18.05.2026 | 5 | BADOUIN-AESTHETICS | Bad Homburg | Dr. Badouin | info@badouin-aesthetics.de | https://badouin-aesthetics.de | Privatpraxis Dr. Jochen Badouin Arztpraxis HWG-konform anschreiben Premium-Potenzial |
| 12 | 25 | 18.05.2026 | 5 | H2 Beautylounge | Bad Nauheim | — | beauty@kosmetik-badnauheim.de | https://kosmetik-badnauheim.de | Bad-Nauheim-Lead Mehrere Leistungen Einzelne Leistungsseiten ausbaufaehig |
| 13 | 26 | 18.05.2026 | 5 | Princess Cosmetics | Bad Nauheim | — | info@princess-cosmetics.de | https://www.princess-cosmetics.de | Inhabergefuehrtes Institut Beauty- + Koerperbehandlungsseiten ausbaufaehig |
| 14 | 29 | 18.05.2026 | 5 | Hautsache Schmidt | Bad Vilbel | — | info@hautsache-schmidt.de | https://www.hautsache-schmidt.de | Lokales Kosmetikstudio Eigene Website Behandlungsseiten + Bad-Vilbel-Bezug ausbaufaehig |
| 15 | 31 | 18.05.2026 | 5 | Louisa Kosmetik | Bad Vilbel | — | louisa@louisa-kosmetik.de | https://www.louisa-kosmetik.de | Kleines Studio Massenheim Lokale Landingpage-Optimierung naheliegend |
| 16 | 34 | 18.05.2026 | 5 | Hunca Kosmetik & Figur Studio | Darmstadt | — | info@hunca-kosmetik.de | https://www.hunca-kosmetik.de | Inhabergefuehrt apparative Kosmetik Viele Leistungen Lokaler Content ausbaufaehig |
| 17 | 35 | 18.05.2026 | 5 | The Beauty Hub | Darmstadt | — | info@the-beauty-hub.de | https://www.the-beauty-hub.de | Einzelunternehmen laut Impressum Basis-Website Lokale Service-Seiten fehlen |
| 18 | 36 | 18.05.2026 | 5 | Kosmetik Kibar | Darmstadt | — | info@kosmetik-kibar.de | https://kosmetik-kibar.de | Klassisches Kosmetikstudio Klare Basisinfos Keine tiefen Leistungsseiten oder Blogstruktur |
| 19 | 37 | 18.05.2026 | 5 | Kosmetik Angelika Heiss | Darmstadt | — | info@kosmetik-angelika-heiss.de | https://kosmetik-angelika-heiss.de | Zentrale Lage Stadtkirche Kleine Website Wenig suchorientierter Content |
| 20 | 38 | 18.05.2026 | 5 | MasterSkin Kosmetik | Dreieich | — | info@master-skin.de | https://master-skin.de | Apparative Kosmetik Inhabergefuehrt Lokale Service-Seiten staerker segmentieren |

### 3.2 Render-Anweisung (Last-Touch / H5_HOT_Trigger)

**Template-Referenz:** `../reports/last_touch_20260519/lasttouch-*.txt` (Beispiel: `lasttouch-belize-beauty-hamburg-belizebeauty-de-20260519.txt`).

**Wichtig — Korrekturen gegenüber Mai-19-Drafts:**
- **Adresse:** `Hauptstr. 29, 85551 Kirchheim b. München` (NICHT mehr Schmölln — alte Drafts haben veraltete Adresse).
- **Pre-Send Checklist:** muss die NeverBounce-Zeile enthalten: `[x] Email-Verifikation (NeverBounce) frisch (≤7 Tage, 2026-05-22)`. Andernfalls bricht `one_shot_send.py` ab (Layer C). Wenn NeverBounce auf Codex-Maschine nicht ausführbar ist → Box `[ ]` lassen, Hand-back an Claude Code.

**Anrede-Auflösung:**
- Wo `Entscheider` im Sheet gesetzt ist (z.B. Frau Dietz / Frau Kellner / Frau Bitter / Dr. Badouin): direkt `Hallo Frau Dietz,` bzw. `Sehr geehrter Herr Dr. Badouin,` (Ärzte → `Sehr geehrter Herr Dr. …`).
- Wo `Entscheider` leer ist: Impressum bzw. Über-uns-Seite live abrufen und Inhaberin/Inhaber extrahieren. Quelle (URL + Datum) im Draft-Header als `Anrede-Quelle:` notieren. Wenn Live-Scrape kein Ergebnis liefert: `Hallo Team [Firma],` (Notausgang).
- **Verbotene Anrede:** `Sehr geehrte Damen und Herren` (zu generisch).

**Keyword-Auswahl:**
- Aus dem `SEO_Problem`-Feld + Branche + Stadt ableiten. Ein konkretes, kommerzielles Keyword (z.B. `Hydrafacial Wiesbaden`, `Laser Bad Homburg`, `Microneedling Darmstadt`). **Keine Suchvolumen-Zahl im Body** — verboten.
- Pflicht-Live-Scrape auf der Studio-Website: Service muss verbatim auf der Seite stehen.

**Body-Skelett (verbatim außer Variablen):**
```
Hallo [ANREDE],

bei Suchanfragen wie „[KEYWORD]" landen Interessenten aktuell bei anderen – nicht bei Ihnen, obwohl Ihr Angebot passt.

Der Grund ist meist kein inhaltlicher, sondern ein struktureller: [KEYWORD-FRAGMENT] ist auf Ihrer Seite nicht sauber auf die lokale Suche ausgerichtet.

Ich fasse Ihnen das in 2–3 konkreten Punkten zusammen – schriftlich, ohne Werbeaussagen.

Ein kurzes Ja genügt.

Mit freundlichen Grüßen
Georg Stopfer

[Drei-Block-Footer verbatim — siehe ./CLAUDE-extract.md §Pflicht-Footer, NEUE Kirchheim-Adresse]
```

**BETREFF-Muster:** `[Firma] – ein konkreter Punkt` (z.B. `Soul&Skin – ein konkreter Punkt`).

**Output-Pfad (relativ zum Repo-Root):** `../reports/followup_20260522/followup-[firma-slug]-[domain-slug]-20260522.txt`

**Draft-Header (Pflicht-Struktur, vor erstem Separator):**
```
STATUS: DRAFT — NICHT VERSENDEN OHNE FREIGABE
Datum: 2026-05-22
Batch: Follow-up Welle Frankfurt_Umland (H5_HOT_Trigger)
Empfänger: [Firma] ([Stadt]) via [email]
Lead-Source: Frankfurt_Umland-Tab Z.[row] | FU am 18.05.2026 (4d her)
Template: H5_HOT_Trigger
Anrede-Quelle: [Sheet | Impressum-URL | …]
Keyword-Quelle: [Sheet SEO_Problem | Live-Scrape <URL>]

Pre-Send Checklist:
[x] DSGVO-Footer enthalten (UWG/DSGVO + Art. 6 Abs. 1 lit. f + Bitte streichen + Art. 21)
[x] Adresse Kirchheim b. München
[x] Email-Verifikation (NeverBounce) frisch (≤7 Tage, 2026-05-22)
[x] Sheet-Pre-Check sauber (./precheck_sheet_status.py 2026-05-22)
[ ] Freigabe Georg
[ ] Sheet-Status NACH Send auf "Last-Touch gesendet" / "Follow-up gesendet" updaten
```

---

## 4. Bucket B — 20 Neukontakte, Stufe-1-Audit (ohne Sistrix)

**Kontext:** Alle 20 sind Score-4-Leads aus dem Frankfurt_Umland-Tab, `Recherche_Status=Neu`. Bereits durch Light-Pre-Qualifizierung gelaufen (Firma + Website + E-Mail im Sheet vorhanden). Codex liefert: Score-Verifizierung (n/7), SEO-Lückenanalyse, Sales-Angle. **Krit. 7 (Brand-Traffic) bleibt offen → `sistrix-pending` Flag.**

### 4.1 Lead-Tabelle (Reihenfolge ist Arbeitsreihenfolge — niedrigster Score, dann Sheet-Z. aufsteigend)

(Quelle: `./_scan_20260522.json` → `bucket_B_neu_asc_score`)

| # | Sheet-Z. | Score | Firma | Stadt | Stadtteil | Branche | Entscheider | E-Mail | Website | SEO_Problem (Sheet) |
|---|----------|-------|-------|-------|-----------|---------|-------------|--------|---------|---------------------|
| 1 | 41 | 4 | Beautique Daniela Billone | Floersheim | Floersheim | Kosmetik / Wimpernlifting / Fusspflege | — | danielabillone@web.de | https://kosmetik-floersheim.de | Einzelstudio Altstadt Private web.de-Mail Kaum Blog/Ratgebercontent |
| 2 | 42 | 4 | Wellness Massagen Friedberg / Karins Massage-Oase | Friedberg | Friedberg | Wellnessmassage | — | karmaoase@t-online.de | https://wellnessmassagen-friedberg.de | Sehr lokaler Massage-Lead Private t-online-Mail Strukturierte Leistungsseiten fehlen |
| 3 | 56 | 4 | CW Cosmetics | Hattersheim | Hattersheim | Kosmetikstudio | — | cw.cosmetics@outlook.de | https://cw-cosmetic.de | Einzelstudio Chantal Marut Outlook-Mail Website wirkt einfach Lokale Behandlungsseiten fehlen |
| 4 | 57 | 4 | Kosmetikstudio Lotus | Hattersheim | Hattersheim-Okriftel | Kosmetik / Anti-Aging / Microneedling | Frau Langer | Langer-lotus@t-online.de | https://kosmetikstudio-lotus.de | Inhaberin Nataliya Langer Private t-online-Mail Bessere Strukturierung Leistungen noetig |
| 5 | 62 | 4 | VITALIFE Massagepraxis | Karben | Karben | Massage / Wellness | — | vitalife@outlook.de | https://www.vitalife-karben.de | Einzelpraxis Massage Outlook-Mail Lokale SEO-Seiten Massagearten fehlen |
| 6 | 63 | 4 | Dorothee Ehrlich-Loewy Kosmetik | Kelsterbach | Kelsterbach | Kosmetik von Kopf bis Fuss | — | dorothee-e-l@web.de | https://kosmetik-kelsterbach.com | Einzelstudio klassische Kosmetikpositionierung Private web.de-Mail Moderne Leistungsseiten fehlen |
| 7 | 64 | 4 | Immer Schoen Kosmetikstudio | Kelsterbach | Kelsterbach | Kosmetik / Manikuere / Pedikuere | — | jana-kiose@web.de | https://immerschoen-kosmetikstudio.de | Inhabergefuehrt seit 2018 Private web.de-Mail Wenig Ratgeber-/SEO-Content |
| 8 | 67 | 4 | Akupunktur TCM Praxis Lin - Dr. Fan Lin | Koenigstein | Koenigstein im Taunus | TCM / Akupunktur | — | tcm-fan@hotmail.de | https://tcm-akupunktur-lin.de | TCM-Lead Private Hotmail-Adresse Lokale Seiten Akupunktur/TCM Koenigstein ausbaufaehig |
| 9 | 68 | 4 | Naturheilpraxis CHEN | Kronberg | Kronberg im Taunus | TCM / Chinesische Medizin | — | xinyu.chen47@gmail.com | https://www.chinesischemedizin-chen.de | TCM-Praxis Private Gmail-Adresse Mehrere lokale Leistungsseiten waeren SEO-relevant |
| 10 | 69 | 4 | Fassbender Massagen | Kronberg | Kronberg im Taunus | Ganzheitliche Massage / Wellness | — | info@fassbender-massagen.de | https://www.fassbender-massagen.de | Einzelpraxis Massage Lokale SEO-Luecke Massagearten + Kronberg-Suchbegriffe |
| 11 | 70 | 4 | Kosmetiksalon Kronberg - Melahat Toluay | Kronberg | Kronberg im Taunus | Kosmetikstudio | — | kosmetikstudio-toluay@t-online.de | https://www.kosmetiksalon-kronberg.de | Klassisches Studio Premium-Lage Private t-online-Mail Lokale SEO-Chance Kosmetik Kronberg |
| 12 | 74 | 4 | VAL Medical Beauty | Mainz | Mainz-Mombach | Medical Beauty / Kosmetik | — | valmedical@gmx.de | https://valmedical.de | Medical-Beauty-Positionierung Private GMX-Mail Lokale Landingpages staerken |
| 13 | 77 | 4 | Akupunktur & TCM Mainz - Wan Qiu | Mainz | Mainz-Neustadt | TCM / Akupunktur / Massage | — | qiu-1118@hotmail.de | https://akupunktur-tcm-mainz.de | VORSICHT Inhaber hat auch Wiesbaden-Standort Nicht beide am selben Tag anschreiben Hotmail-Mail Lokaler SEO-Ausbau Akupunktur Mainz |
| 14 | 82 | 4 | Zauberschoen - Hautgesundheit & Kosmetik | Mainz | Mainz-Hechtsheim | Kosmetik / Hautpflege | — | info@hautkonzept-mainz.de | https://hautkonzept-mainz.de | Domain-Diskrepanz Zauberschoen vs hautkonzept Hautkonzept-Positionierung Lokale Hautpflege-Keywords |
| 15 | 87 | 4 | Kosmetik & Haarentfernung Beate Weber | Oberursel | Oberursel-Weisskirchen | Kosmetik / Haarentfernung | — | beate.weber9@googlemail.com | https://kosmetik-beate-weber.de | Einzelanbieter Googlemail-Adresse Lokale SEO-Luecke Haarentfernung Weisskirchen |
| 16 | 88 | 4 | Nicols Kosmetikstudio | Oberursel | Oberursel | Kosmetikstudio | Frau Burkard | nicol.burkard@web.de | https://nicolskosmetik.de | Inhaberin Nicol Burkard Private web.de-Mail Lokales Studio Website einfach |
| 17 | 89 | 4 | GLOW UP Clinic | Oberursel | Oberursel | Medical Beauty / Aesthetik | — | klaudiazm10@gmail.com | https://glowupclinic.net | Medical-Beauty-Positionierung Private Gmail-Adresse Lokale Landingpages je Behandlung fehlen |
| 18 | 90 | 4 | Kosmetikparadies Marie-Luise Flinsbach | Oberursel | Oberursel | Kosmetik / Fusspflege / Microneedling | — | kosmetikparadies-oberursel@t-online.de | https://kosmetik-paradies-oberursel.de | Langjaehriges Einzelstudio Private t-online-Mail Moderne Service-Seiten + lokale Keyword-Struktur fehlen |
| 19 | 92 | 4 | Praxis fuer TCM und Naturheilkunde - Annette Feil | Oberursel | Oberursel | TCM / Naturheilkunde | — | TCM-Oberursel@t-online.de | https://www.chinesische-medizin-oberursel.de | Lokaler TCM-Lead Private t-online-Mail Service-Seiten + lokale Suchintention fehlen |
| 20 | 93 | 4 | Esthetique Kosmetikinstitut Strzalka | Oberursel | Oberursel | Kosmetikinstitut / SOTHYS | — | info@esthetique-kosmetik-oberursel.sothys.de | https://kosmetikinstitut-strzalka.de | Etabliertes Studio Sothys-Sub-Domain bei Mail Klassische Website Blog/Content-Potenzial |

**Vorsicht-Hinweise (im Sheet markiert):**
- **#13 (Akupunktur & TCM Mainz – Wan Qiu):** Inhaber betreibt auch einen Standort in Wiesbaden. Beide nicht am gleichen Tag anschreiben. → Bei Pre-Check abprüfen, ob Wiesbaden-Pendant in `Frankfurt_Umland` oder Aggregat existiert.
- **#14 (Zauberschoen / hautkonzept-mainz):** Sheet-Firmenname und Mail-Domain stimmen nicht überein. Site live abrufen und prüfen, welche Marke aktuell aktiv ist. Bei Ambiguität → im Result-Report flaggen, nicht raten.
- **#20 (Esthetique / Strzalka):** E-Mail-Subdomain `*.sothys.de` deutet auf Sothys-Markenpartnerschaft. Validieren ob es trotzdem ein Einzelinstitut ist (nicht Kette).

### 4.2 Stufe-1 Pipeline (angepasst auf Codex-Toolset)

Für jeden der 20 Leads:

**A) Ubersuggest** (MCP `mcp__claude_ai_Ubersuggest__*`)
- `domain_overview` → Domain-Authority, Backlinks-Count, Referring Domains, Organic Traffic, Organic Keywords.
- `domain_keywords` (Top 50) → wofür rankt die Domain bereits? Lokal? Brand? Generisch? → reicht aus, um Krit. 1, 2, 8 zu bewerten.
- `domain_top_pages` → welche Seiten ziehen Traffic? Falls Top-Page = `/` ohne lokale Service-Seiten → SEO-Lücke quantifiziert.
- `domain_top_countries` → Erwartung: DE > 90%.

**B) Firecrawl / Web-Fetch**
- Homepage + Behandlungs-Submenüs scrapen.
- Prüfen: Blog vorhanden? H1/H2-Struktur lokal? `lang="de"`? Schema.org `LocalBusiness`/`MedicalBusiness`? GoogleBusinessProfile-Verknüpfung?
- **Pflicht: jede Site einzeln live abrufen — keine Snippet-Schätzungen.**

**C) Sistrix → DEFERRED**
- Codex liefert **kein** Sistrix-Ergebnis.
- Im Result-Report jeden Bucket-B-Lead mit `sistrix_pending: true` markieren.
- Optional: Codex darf eine Brand-Heuristik aus Ubersuggest dokumentieren ("X% der Top-50 Keywords enthalten Brand-Token") als Beobachtung, **aber keine DQ-Entscheidung** auf dieser Basis treffen. DQ-Brand entscheidet erst Claude Code in Stufe 2.

### 4.3 Scoring (7 Kriterien, Max 7 — Krit. 7 deferred)

| Krit. | Beschreibung | Punkte | Quelle |
|-------|--------------|--------|--------|
| 1 | DA ≥ 10 | +1 | Ubersuggest `domain_overview` |
| 2 | ≥ 5 ranking Keywords lokal | +1 | Ubersuggest `domain_keywords` |
| 3 | Eigene Website (kein Free-Builder, kein Facebook-Only) | +1 | Firecrawl Homepage-Check |
| 4 | Service-Angebot Beauty/Wellness/TCM klar erkennbar | +1 | Firecrawl |
| 5 | Einzelstandort (keine Kette/Filiale) | +1 | Impressum-Scrape |
| 6 | Inhaberin/Inhaber identifiziert | +1 | Impressum/Über-uns |
| 7 | ~~Brand-Traffic ≤ 80%~~ | **DEFERRED** | Sistrix (nicht verfügbar bei Codex) |
| 8 | Sichtbarer SEO-Hebel (Blog fehlt / lokale Landingpages fehlen / Schema fehlt) | +1 | Firecrawl + Ubersuggest |

**Score-Ausgabe:** `N/7 (sistrix-pending)`. Score ≥ 5/7 → in nächste Outreach-Welle (vorbehaltlich Sistrix). Score ≤ 3/7 → DQ.

### 4.4 Sheet-Update durch Codex

Nach jedem Audit das Lead-Tracker-Sheet aktualisieren (Tab `Frankfurt_Umland`):

- `SCORE` → numerischer Score 0–7 (Codex schreibt 7-Punkte-Skala; Claude Code addiert ggf. nach Sistrix den 8. Punkt).
- `SEO_Problem` → 1–2 Sätze, konkret (kein Marketing-Sprech). Beispiel: `Blog fehlt komplett, Hydrafacial nicht als eigene Seite, GMB nicht verlinkt`.
- `Recherche_Status` → `Recherche-Done-sistrix-pending` (sendable nach Sistrix-Check) oder `DQ-Kette` / `DQ-Service`.
- Optional: `Entscheider` setzen, wenn Impressum-Scrape eindeutig.

**Befehl-Muster (aus deinem outreach-cli-Pfad):**
```powershell
py -m outreach_cli set-status --email <email> --status "Recherche-Done-sistrix-pending" --column Recherche_Status --date 2026-05-22
```

Falls `set-status` den Custom-Status nicht erlaubt: stattdessen `Recherche-Done` setzen und das `sistrix-pending`-Flag im `SEO_Problem`-Feld voranstellen (z.B. `[SISTRIX-PENDING] Blog fehlt, …`).

Free-Form-Felder (SEO_Problem, Entscheider) gehen über den Google-Sheet-MCP-Server, sofern auf Codex-Maschine verfügbar. Falls nicht: ins Result-Report sammeln, Claude Code schreibt in Stufe 2.

---

## 5. Hand-back an Claude Code (Stufe 2)

Wenn Codex Bucket A + B abgearbeitet hat:

1. **Result-Report** ablegen unter `./RESULT-20260522.md` (im selben `codex-handover/`-Ordner) mit:
   - Pro Bucket-A-Lead: Pfad zum Draft-File (`../reports/followup_20260522/…`) + Anrede-Quelle + Verify-Datum (oder `verify-pending`).
   - Pro Bucket-B-Lead: Score (n/7), SEO_Problem (neu), Recherche_Status-Endstand, Sistrix-Pending-Flag.
   - Liste der DQ-Leads (mit Begründung).
   - Falls Codex Tools fehlten (NeverBounce, Sheet-Schreibzugriff, etc.): explizite Flag-Liste, was Claude Code nachholen muss.
2. Claude Code übernimmt für **Stufe 2** (Sistrix-Lookup + finaler Score auf 8-Skala + Hook-Profil-Wahl), **Stufe 3** (Browser-Test) und Live-Send.
3. Live-Send von Bucket A erfolgt erst nach Georgs Freigabe pro Draft (`[ ] Freigabe Georg` → `[x]`).

---

## 6. Pflicht-Regeln (Zusammenfassung — bei Konflikt gewinnt diese Sektion + `./CLAUDE-extract.md`)

- **DSGVO-Footer:** Drei-Block-Schluss verbatim, neue Kirchheim-Adresse. Marker `UWG/DSGVO`, `Art. 6 Abs. 1 lit. f DSGVO`, `Bitte streichen`, `Art. 21 DSGVO` müssen alle im Body stehen.
- **Email-Verifikation:** Bucket-A-Send ist gesperrt, wenn `[x] Email-Verifikation (NeverBounce) frisch (≤7 Tage)` im Header fehlt — Layer-C-Parser im `one_shot_send.py` blockt sonst hart (exit 2).
- **Verbotene Wörter:** siehe `./CLAUDE-extract.md` §Brand Voice.
- **Keine erfundenen Zahlen.** Live-Scrape Pflicht. Ketten raus. Adresse Kirchheim.
- **Krit. 7 (Brand-Traffic):** Codex skipt → `sistrix-pending`. Claude Code macht final.

---

## 7. Anhänge (alle relativ zu diesem Ordner)

- **JSON-Dump (Lead-Daten):** `./_scan_20260522.json`
- **CLAUDE.md-Extract (verbindlich):** `./CLAUDE-extract.md`
- **Pre-Check-Skript (Original-Kopie):** `./precheck_sheet_status.py`
- **Template-Master (Variante C, Erstmail):** `../outreach-cli/outreach_cli/templates/variante_c.txt`
- **Template-Master (H5_HOT_Trigger / Last-Touch):** Beispiel `../reports/last_touch_20260519/lasttouch-belize-beauty-hamburg-belizebeauty-de-20260519.txt` (Adresse + NeverBounce-Checkbox aktualisieren!)
- **Sender (mit Layer-C-Gate):** `../../Tools/one_shot_send.py` — **nur in Claude-Code-Mount erreichbar.** Codex sendet **nicht selbst live**; Codex liefert Drafts an Claude Code zurück. Live-Send ist Stufe 2 / Stufe 3.

---

**Erstellt:** 2026-05-22 von Claude Code (v2 nach Goal-27-Blocker).
**Sortier-Regel Bucket B:** Score aufsteigend (Georg-Vorgabe 2026-05-22).
**Sistrix-Status:** deferred to Stufe 2.
