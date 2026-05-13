# Audit-Pipeline v2 — Drei-Maschinen-Workflow

## Standard-Pipeline (alle Leads)

### Stufe 1 — Codex (Laptop): Audit-Erstellung
- Tools: Ubersuggest, Firecrawl, Sistrix
- Website-Analyse: Leistungsseiten, HWG-Wording, Trust, Sprache
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
- Sales-Psychology-Check
- Strategische Hook-Einschätzung
- Freigabe für `outreach-cli send --confirm-live`

## Premium-Eskalation (DA15+ oder Auftragspotenzial >1.000 €)

Zusätzlich nach Stufe 3:

### Stufe 4 — ChatGPT: Härtetest
- Sales-Copy-Review
- Sprach-Tonalität für Premium-Segment
- Dritte Meinung zum Hook

## Hook-Standard (Hybrid)

Kombiniert Codex-Wertschätzung mit Claude-Code-Beweisführung:

> "Mir ist aufgefallen, dass Google aktuell nur X Seiten Ihrer Website indexiert. Gleichzeitig liegen wichtige Leistungen wie [Top-3-Services] nicht als eigene [Stadt]-Seiten vor. Dadurch findet man [Studio] vor allem über den Studionamen — aber kaum über lokale Suchen nach diesen Leistungen."

**HWG-Note:** "Behandlungsanfragen" (im ursprünglichen Pipeline-v2-Entwurf) wurde durch "lokale Suchen nach diesen Leistungen" ersetzt — bleibt semantisch identisch, vermeidet HWG-Sperrwort `Behandlung`.

## Quality-Gates (`.claude/commands/audit.md` erweitern)

Zusätzlich zu bestehenden v2-Gates:

- **"Top-3-Services namentlich genannt"** — neu (drei konkrete Leistungs-Bezeichnungen aus der Website)
- **"site:-Befund quantifiziert (X Seiten)"** — neu (exakte Zahl indexierter Seiten, nicht „einige" oder „wenige")

## Zwei-Quellen-Regel bleibt

Stufen 1+2 sind das Two-Source-Verifikations-Setup. Stufen 3+4 sind Sales-Layer-Reviews, keine zusätzliche Tool-Verifikation.

## Status-Tracking

Siehe `audit-queue.md` — Tracking-Tabelle mit den vier Spalten Codex / Claude Code / Claude.ai / Send.
