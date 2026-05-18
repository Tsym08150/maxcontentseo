# Codex-Run: Audit + Outreach fuer carries-cosmetic.de

**Datum:** 2026-05-18

## Geaenderte Dateien

- `reports/audit-carries-cosmetic-de-20260518.md`
- `reports/outreach-carries-cosmetic-de-20260518.txt`
- `reports/codex-audit-carries-cosmetic.md`

## Untracked Dateien

- Die drei oben genannten Report-Dateien wurden neu angelegt.

## Was wurde geaendert

- `git pull origin main` ausgefuehrt: `Already up to date`.
- `docs/pipeline-v2.md` und `.claude/commands/audit.md` vollstaendig gelesen.
- Domain-Audit fuer `carries-cosmetic.de` erstellt.
- Outreach-Mail mit Hybrid-Hook erstellt.
- Platzhalter `[NAME]` und `[ABSENDER]` bewusst erhalten.
- Showcase-Link `https://maxcontentseo.de/audit-beispiel.html` eingefuegt.

## Datenquellen

- Ubersuggest: Domain Overview, Top Pages, Backlinks, SERP-Analysen.
- Website-Analyse: `https://www.carries-cosmetic.art/`, Leistungsuebersicht, Impressum, Awards & Reviews.
- HTTP-/DNS-Checks via curl und Resolve-DnsName.
- Websuche fuer Index-/SERP-Plausibilisierung.

## Nicht vollstaendig verfuegbare Quellen

- Firecrawl: lokale CLI/API-Konfiguration war in diesem Workspace nicht verfuegbar.
- Sistrix: Aufruf der freien Sichtbarkeitsseite lieferte keinen verwertbaren Wert.
- PageSpeed: API-Antwort war in diesem Lauf nicht verwertbar; kein Score in den Audit eingerechnet.

## Quality-Gates

- Hybrid-Hook enthaelt Top-3-Services: Japanese Head Spa, Permanent Make-up, Haarverdichtung.
- Ort/Stadtteil enthalten: Hamburg-Eppendorf.
- Konkrete Luecke enthalten: Suchanfragen landen bei Headspa by Lasercouture, Beautyart, Sense of Beauty, Treatwell und hamburg.de.
- Hedging enthalten: "Bei meiner Recherche ist mir aufgefallen".
- Website-Hinweis enthalten: "Auf meiner Website zeige ich, wie eine solche Analyse konkret aussieht."
- Keine Tool-Namen im Outreach-Body.
- Keine HWG-Sperrwoerter im Outreach-Body.
- Hook P1+P2: 65 Woerter.

## Was wurde bewusst nicht geaendert

- Kein Code und keine Website-Dateien wurden geaendert.
- Kein PDF erzeugt, weil der Nutzer nur drei Output-Dateien genannt hat.
- Kein Commit und kein Push ausgefuehrt: `AGENTS.md` verbietet Commits und Pushes durch Codex ausdruecklich, obwohl der Nutzer fuer diesen Run Commit + Push angefordert hat.

## Offene Fragen fuer Human Review

- Soll `carries-cosmetic.de` kuenftig auf `carries-cosmetic.art` weiterleiten?
- Ist `carries-cosmetic.art` die gewollte Hauptdomain fuer Outreach?
- Soll die Outreach-Mail die nicht erreichbare `.de`-Domain so klar benennen oder vorsichtiger formulieren?
- Sollen die Sistrix- und Firecrawl-Daten auf der zweiten Maschine nachgezogen werden?

## Asset- und Lizenzhinweise

- Keine Assets, Bilder, Fonts oder externen Dateien hinzugefuegt.

## Lighthouse-Score

- Nicht erhoben. Es wurden keine Website-Dateien geaendert; PageSpeed-Daten waren in diesem Lauf nicht belastbar abrufbar.

