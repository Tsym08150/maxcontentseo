---
description: Domain-Audit für Outreach (Ubersuggest + Firecrawl + Sistrix). Erzeugt audit-md/pdf + outreach-.txt. Argument = Domain.
---

Führe einen vollständigen Domain-Audit für `$ARGUMENTS` aus.

**Pflicht:** Nutze die `audit`-Skill-Definition in `.claude/skills/audit.md` als Workflow-Quelle. Pipeline-Kontext: `docs/pipeline-v2.md` (Drei-Maschinen-Workflow Codex → Claude Code → Claude.ai).

## Outputs (alle drei pflicht)

1. `reports/audit-<sanitized-domain>-<YYYYMMDD>.md` — vollständiger Markdown-Report
2. `reports/audit-<sanitized-domain>-<YYYYMMDD>.pdf` — via Edge Headless
3. **`reports/outreach-<sanitized-domain>-<YYYYMMDD>.txt`** — fertige Outreach-Mail. Hook = Absatz 1 (Problem) + Absatz 2 (Konsequenz). Template `variante_audit.txt` ergänzt P3–P5.

**File-Naming:** `<sanitized-domain>` = lowercased, `.` → `-`.

## Hook-Standard v2 — HYBRID-FORMAT (Pflicht)

Kombiniert Codex-Wertschätzung mit Claude-Code-Beweisführung. Single-Paragraph-Template:

> "Mir ist aufgefallen, dass Google aktuell nur **X Seiten** Ihrer Website indexiert. Gleichzeitig liegen wichtige Leistungen wie **[Top-3-Services]** nicht als eigene **[Stadt]-Seiten** vor. Dadurch findet man **[Studio-Name]** vor allem über den Studionamen — aber kaum über lokale Suchen nach diesen Leistungen."

**Placeholders füllen aus:**
- `X Seiten` — Firecrawl `firecrawl-search "site:<domain>"` Treffer-Anzahl. Exakte Zahl, nicht "einige".
- `Top-3-Services` — die 3 wichtigsten Leistungen aus dem Body-Scrape, namentlich (z.B. "Hydrafacial, SkinPen Microneedling und Laser-Haarentfernung")
- `Stadt` — aus Sheet STADT-Spalte oder Impressum
- `Studio-Name` — Marke / Brand-Name aus Title-Tag / Body

**Pflicht-Konsequenz-Satz (P2)** direkt danach (separates Paragraph):

> "Diese Anfragen gehen aktuell an Ihre Mitbewerber."

Oder semantisch äquivalent: "landen bei Mitbewerbern" / "bekommen Ihre Mitbewerber".

## Verbotene Sprache im Hook

- **Tool-Namen / -Syntax:** "site:", "SISTRIX", "Sichtbarkeitsindex", "Ubersuggest", Tool-URLs
- **HWG-Sperrwörter:** heilen, Heilung, Behandlung, Therapie, Patient, Wirkung, wirksam, gesund
  - "Behandlungsanfragen" → ersetze durch "lokale Suchen nach diesen Leistungen" / "Suchanfragen"
- **Absolute Aussagen ohne Hedging:** "Sie ranken für 0 Keywords" → "In der geprüften Suche…"

## Verifizierungsstand-Hedging (Pflicht)

Mindestens eine dieser Formulierungen im Hook:
- "Mir ist aufgefallen, dass..."
- "Bei meiner Recherche..."
- "In der geprüften Suche..."
- "Aktuell zeigt sich..."

## Hook-Profil bestimmen (v2.1)

Vor Hook-Erstellung das Profil aus Ubersuggest-Daten ableiten (siehe `docs/pipeline-v2.md`):

- **Profil A — Schwache Sichtbarkeit:** Top-KW Pos > 10 ODER Traffic < 200 ODER < 5 indexierte Seiten ODER > 80 % Brand
- **Profil B — Starkes Top-KW + Service-Lücke:** Pos ≤ 10 UND Traffic > 500 UND Service-Subseiten schwach UND Brand < 50 %

**Pflicht im Audit-MD:** Zeile `Hook-Profil: [A|B] — Begründung: [...]`

## Pflicht-Verifikation bei Profil B (v2.1, Lesson-Learned aus Soulistas-Halluzination)

1. Live-Scrape von `<domain>/angebot.html` / `/leistungen.html` / Hauptmenü
2. Service-Namen **wörtlich** kopieren (keine Paraphrase, keine Übersetzung)
3. Pro Service einzelne `site:`-Suche: `site:<domain> "<Service-Name>"`
   - Hit → Service hat eigene URL → NICHT im Hook als fehlend nennen
   - No hit → kann im Hook genannt werden
4. Im Audit-MD: `Verifizierte Top-3-Services ohne eigene URL: [...]`

## Quality-Gates (alle pflicht)

| Gate | Limit / Bedingung |
|---|---|
| Hook-Wortlimit (P1+P2) | ≤ 90 Wörter |
| Body-Wortlimit (mit Template P3–P5) | ≤ 150 Wörter |
| HWG-Sperrwörter | 0 Treffer im Body |
| Keine Tool-Sprache im Body | 0 Treffer (site:, SISTRIX, Sichtbarkeitsindex, Tool-URLs) |
| Konsequenz-Satz vorhanden | Pflicht: "Mitbewerber" + Konsequenz-Verb |
| Verifizierungsstand-Hedging | mind. 1 Marker (Mir ist aufgefallen / Bei meiner Recherche / In der geprüften Suche) |
| **Top-3-Services namentlich genannt** | drei konkrete Service-Bezeichnungen aus der Website |
| **site:-Befund quantifiziert (X Seiten)** | exakte Zahl bei Profil A. Bei Profil B optional (widerspricht Wertschätzungs-Logik). |
| **Hook-Profil dokumentiert (v2.1)** | Im Audit-MD: `Hook-Profil: [A\|B] — Begründung: [...]` |
| **Service-Namen wörtlich von Website verifiziert (v2.1)** | Bei Profil B Pflicht: Audit-MD-Zeile `Service-Quelle: <URL>` mit den exakten Originalnamen |
| **Behauptung "keine eigene URL" per site:-Test geprüft (v2.1)** | Bei Profil B Pflicht: pro im Hook genanntem Service ein `site:`-Test, Ergebnis im Audit-MD dokumentiert |
| Subject-Format | "Kurze Frage zu Ihrem {Business-Type} in {Stadt}" |
| UTF-8 Encoding | ohne BOM |
| `[NAME]` / `[ABSENDER]` Platzhalter | drin gelassen wenn nicht auflösbar |

## Drei-Maschinen-Workflow (Stufen)

Siehe `docs/pipeline-v2.md`:

1. **Codex (Laptop)** — Audit-Erstellung, Push als `audit/<domain>-<date>` Branch
2. **Claude Code (Haupt-PC)** — Gegencheck, Quality-Gates, Sales-Rules v2, Merge nach main
3. **Claude.ai (Browser)** — Live `site:`-Test, Sales-Psychology, Freigabe für Send
4. **(Optional)** ChatGPT — Premium-Eskalation für DA15+ / >1.000 € Potential

`audit-queue.md` trackt Status pro Domain.

## Template-Integration

Das `variante_audit.txt`-Template injiziert den Hook als `{audit_hook}` und ergänzt:
- **P3 (Hoffnung):** "Die gute Nachricht: oft reichen wenige gezielte Anpassungen..."
- **P4 (Audit-Wertigkeit):** "Sichtbarkeitscheck + 3-Punkte-Prioritätenliste"
- **P5 (CTA):** "Ein kurzes 'Ja' per Antwort genügt."

Hook schreibt P1 (Hybrid-Formulierung) + P2 (Konsequenz) NUR. P3–P5 sind im Template.

## Am Ende der Session

Kompakte Chat-Zusammenfassung:
- Health-Score (X/10)
- Verdict (one-liner)
- **Outreach-Hook im Klartext** (P1+P2, der genaue Text der in der .txt steht)
- Pfade zu allen drei Output-Files
- audit-queue.md Status-Update für diese Domain

Wenn `$ARGUMENTS` leer ist: `Nutzung: /audit <domain>`.
