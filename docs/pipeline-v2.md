# Audit-Pipeline v2.1 — Drei-Maschinen-Workflow

## Standard-Pipeline (alle Leads)

### Stufe 1 — Codex (Laptop): Audit-Erstellung
- Tools: Ubersuggest, Firecrawl, Sistrix
- Website-Analyse: Leistungsseiten, HWG-Wording, Trust, Sprache
- **Pflicht-Verifikation (v2.1):** Service-Namen DIREKT von der Website ziehen, jeden via `site:`-Test einzeln prüfen
- Output:
  - `reports/audit-<domain>-<date>.md`
  - `reports/outreach-<domain>-<date>.txt`
- Branch: `audit/<domain>-<date>`
- Commit + Push

### Stufe 2 — Claude Code (Haupt-PC): Gegencheck
- Pullt Codex-Branch
- Verifiziert Tool-Zahlen (Sistrix SI, Ubersuggest, Index-Count)
- Prüft Quality-Gates (Wortlimit, HWG, Tool-Sprache, Konsequenz-Satz)
- Prüft Sales-Rules v2 (Problem + Hoffnung + Konsequenz, Big Domino)
- OK → Merge nach main
- Korrekturen → diff-Datei, Codex bessert nach

### Stufe 3 — Claude.ai (Browser): Abschlusstest
- Live `site:`-Test im Browser
- **Service-Realitäts-Check (v2.1):** jede im Hook genannte Behauptung live nachprüfen
- Sales-Psychology-Check
- Strategische Hook-Einschätzung
- Freigabe für `outreach-cli send --confirm-live`

## Premium-Eskalation (DA15+ oder Auftragspotenzial >1.000 €)

Zusätzlich nach Stufe 3:

### Stufe 4 — ChatGPT: Härtetest
- Sales-Copy-Review
- Sprach-Tonalität für Premium-Segment
- Dritte Meinung zum Hook

---

## Hook-Varianten je nach Lead-Profil (v2.1)

Codex muss vor Hook-Erstellung das Lead-Profil bestimmen anhand der Ubersuggest-Daten.

### Profil A — Schwache Sichtbarkeit (Default)

**Trigger:**
- Top-Keyword-Position > 10, ODER
- Organic Traffic < 200, ODER
- < 5 indexierte Seiten, ODER
- > 80 % Brand-Traffic-Anteil

**Hook-Logik:** Sichtbarkeits-Schmerz

> "Mir ist aufgefallen, dass Google aktuell nur X Seiten Ihrer Website indexiert. Gleichzeitig liegen wichtige Leistungen wie [Top-3] nicht als eigene [Stadt]-Seiten vor. Dadurch findet man [Studio] vor allem über den Studionamen — aber kaum über lokale Suchen nach diesen Leistungen."

**Pflicht-Konsequenz-Satz:** "Diese Anfragen gehen aktuell an Ihre Mitbewerber."

**Beispiel-Lead:** dermacosmetic-wiesbaden.de (SI 0,0004, 3 indexiert, 89 % Brand-Traffic)

### Profil B — Starkes Top-KW, schwache Service-Differenzierung

**Trigger:**
- Top-Keyword-Position ≤ 10 UND Traffic > 500, UND
- Service-Subseiten haben < 50 Traffic ODER fehlen, UND
- Brand-Traffic-Anteil < 50 %

**Hook-Logik:** Wertschätzung + Service-Lücke

> "Mir ist aufgefallen, dass Ihre Website bereits stark für '[Top-KW]' rankt — ein gutes Fundament. Gleichzeitig liegen wichtige einzelne Leistungen wie [Top-3] nicht als eigene [Stadt]-Seiten vor. Wer gezielt nach diesen Leistungen sucht, findet [Studio] dadurch oft nicht direkt — diese Anfragen gehen aktuell an Mitbewerber."

**site:-Quantifizierung optional** — bei starkem Ranking widerspricht die Zahl der Wertschätzungs-Logik.

**Beispiel-Lead:** soulistas.de (Pos 5 "massage wiesbaden", 2.233 Traffic) — **AKTUELL BLOCKED** wegen Service-Halluzinationen, siehe `audit-queue.md`.

### Profil-Auswahl-Regel

Codex muss vor Hook-Erstellung explizit dokumentieren:
- Profil A oder Profil B
- Welche Trigger erfüllt sind
- Im Audit-Markdown als Zeile: `Hook-Profil: [A|B] — Begründung: [...]`

### Erweiterbarkeit

Weitere Profile bei Bedarf:
- **Profil C:** NAP-Inkonsistenz dominiert (Hook = Local-SEO-Sofort-Schmerz)
- **Profil D:** Frische Domain ohne Daten (Hook = Konsequenz-Frame ohne Zahlen)

---

## 🚨 Service-Halluzination — Top-Risiko bei Profil B

**Fall:** Soulistas-Audit am 13.05.2026 (`audit/soulistas-de-20260513`)

Codex hat 3 Services im Hook genannt die nicht der Realität entsprachen:
- "Soul-Time-Massage" als angeblich fehlende URL — **existiert** als `soulistas.de/massagen/soul-time-de-luxe.html`
- "Entspannung de Luxe" — **falscher Name**, tatsächlich "Soul-Time de Luxe"
- "Full-Body-Peeling" — **falscher Name**, tatsächlich "Softpeeling" / "Softpeeling-Massage"

**Branch wurde NICHT gemerged.** Stufe 3 (Claude.ai) hat die Halluzination beim Live-Browser-Check entdeckt.

### Lesson: Profil B braucht zusätzliche Verifikation

Profil B (Wertschätzung + Service-Lücke) hat **strukturell höheres Halluzinations-Risiko** als Profil A, weil:
1. Top-3-Services müssen **wörtlich richtig** sein (Sales-Glaubwürdigkeit hängt davon ab)
2. Die Behauptung "hat keine eigene URL" muss **pro Service einzeln verifiziert** werden
3. Codex tendiert dazu, Service-Namen aus Branchen-Wissen zu synthetisieren statt von der Quelle zu lesen

### Mandatory-Verification-Schritte für Profil B

1. **Live-Scrape** von `<domain>/angebot.html` / `/leistungen.html` / Hauptmenü
2. Jeden Service-Namen **wörtlich** kopieren (keine Paraphrase, keine Übersetzung)
3. **Pro Service** einzelne `site:`-Suche: `site:<domain> "<Service-Name>"`
   - Hit → Service hat eigene URL → NICHT im Hook als fehlend nennen
   - No hit → Service hat keine eigene URL → kann im Hook genannt werden
4. Nur Services im Hook nennen, die Schritt 3 mit "no hit" bestanden haben
5. Im Audit-MD dokumentieren: `Verifizierte Top-3-Services ohne eigene URL: [...]`

---

## Hook-Standard (Hybrid)

Kombiniert Codex-Wertschätzung mit Claude-Code-Beweisführung. Format hängt vom Profil ab (siehe oben).

**HWG-Note:** "Behandlungsanfragen" (im ursprünglichen Pipeline-v2-Entwurf) wurde durch "lokale Suchen nach diesen Leistungen" ersetzt — bleibt semantisch identisch, vermeidet HWG-Sperrwort `Behandlung`.

## Quality-Gates (`.claude/commands/audit.md` erweitern)

Vollständige Liste in `audit.md`. Highlights v2.1:

- **"Top-3-Services namentlich genannt"** (v2)
- **"site:-Befund quantifiziert (X Seiten)"** (v2, **conditional bei Profil B**)
- **"Hook-Profil dokumentiert (A oder B mit Begründung)"** (v2.1 — neu)
- **"Service-Namen wörtlich von Website verifiziert"** (v2.1 — neu)
- **"Behauptung 'keine eigene URL' per site:-Test geprüft"** (v2.1 — neu)

## Zwei-Quellen-Regel bleibt

Stufen 1+2 sind das Two-Source-Verifikations-Setup. Stufen 3+4 sind Sales-Layer-Reviews, keine zusätzliche Tool-Verifikation.

## Status-Tracking

Siehe `audit-queue.md` — Tracking-Tabelle mit den vier Spalten Codex / Claude Code / Claude.ai / Send. BLOCKED-Status mit aktiver Blocker-Sektion für Re-Run-Anweisungen.
