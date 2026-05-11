# outreach-cli

Kompakte Zwischenschicht zwischen Claude Code und dem Google-Sheet
`Lead_Tracker_Gesamt` (Tabs: **Muenchen, Hamburg, Frankfurt, Frankfurt_Umland,
Bad Homburg** sowie Aggregat **Alle_Leads**).

Statt das ganze Sheet in den Kontext zu laden, ruft Claude Code kurze CLI-Befehle
auf und bekommt kompakte tabellarische oder JSON-Ausgabe zurück.

---

## Why this exists

Über Monate hat das Apps-Script-Webhook unter
`https://script.google.com/macros/s/.../exec` (Modi `updateCell`,
`updateByEmail`) `200 OK`-Responses mit Body `"Das Script wurde abgeschlossen,
jedoch kein Wert zurückgegeben."` geliefert, **ohne tatsächlich ins Sheet zu
schreiben**. Konkrete Ausfälle (verifiziert via Backup-Snapshots + sent_log):

- **Muenchen**: Header-Diskrepanz `KONTAKTIERT` (im Sheet) vs `KONTAKTIERT_AM`
  (im Webhook-Payload) → 4 Leads bekamen H4_FU_Beauty Follow-ups versendet,
  Sheet blieb auf `Angeschrieben`.
- **Frankfurt**: My Tiny Spa, 2026-05-11 — Webhook gab "no value" zurück,
  `Verkaufsstatus="Geantwortet - kein Interesse"` wurde nie geschrieben.
- **Gesamt**: 101 historische Stati aus `sent_log.csv` waren im Sheet veraltet
  (siehe `v2_nachzieh.py`).

outreach-cli ersetzt den Webhook durch **direkten Google-Sheets-API-Zugriff mit
Service-Account-Auth via `gspread`**. Jeder `set-status`-Call hat
verifizierbares Outcome (success/fail/partial per Tab), kein silent no-op mehr.

---

## Architektur-Highlights

- **Asymmetrische Datums-Logik** für Bestandsdaten-Migration (`v2_nachzieh.py`):
  - `KONTAKTIERT_AM` = **älteres** wins (Erstkontakt-Schutz — Sheet-Datum darf
    nicht durch späteres sent_log-Datum überschrieben werden).
  - `FOLLOWUP_AM` = **neueres** wins (Letzter-Touchpoint — sent_log-Datum
    soll Sheet-Datum bei späteren FU-Wellen ersetzen).
- **Aggregat-Sync**: `set_status` schreibt synchron in Primary-Stadt-Tab **und**
  `Alle_Leads`-Aggregat. Partial-Failure wird per `SetStatusResult.partial_failure`
  reportet (Exit-Code 3), nicht silently inkonsistent.
- **Synonym-Map** für Header-Drift: Alt-Frankfurt `.` → `FIRMA`,
  Alt-Muenchen `KONTAKTIERT` → `KONTAKTIERT_AM`, `FOLLOW-UP` → `FOLLOWUP_AM`,
  Alle_Leads `Stadt` → `STADT`. Damit funktioniert die CLI während laufender
  Header-Migrationen ohne Downtime.
- **Lifecycle-Schutz vor Downgrades**: Leads im Endzustand
  (`Geantwortet - kein Interesse`, `Geantwortet - Interesse`, `Bounce`) werden
  von Bulk-Importern (`v2_nachzieh`) nie wieder auf frühere Lifecycle-Stufen
  (`Angeschrieben`, `Follow-up gesendet`) zurückgesetzt.
- **Idempotency** mit `--force` Override: re-runs schreiben nur wenn sich Werte
  tatsächlich ändern. Schützt vor Quota-Verschwendung und Audit-Trail-Drift.
- **Two-Spalten-Status-Modell**: `Recherche_Status` (Outreach-Lifecycle:
  Nicht kontaktiert → Angeschrieben → Follow-up gesendet) **getrennt von**
  `Verkaufsstatus` (Sales-Outcome: Geantwortet*/Bounce). `set-status --column`
  wählt, welche Spalte geschrieben wird (Default: `Verkaufsstatus`).

---

## Setup

### 1. Service-Account ins Sheet einladen

JSON liegt bereits:
```
D:\000 SEO Business\Tools\GoogleAutomationfürAutomtischen schreiben inDokumenten\GoogleSheetMcp\credentials\google-service-account.json
```

`client_email` aus dem JSON kopieren → Sheet `Lead_Tracker_Gesamt` → **Teilen** →
diese E-Mail als **Editor**. Aktuell:
`sheets-mcp-server@maxcontentseo-mcp.iam.gserviceaccount.com`

### 2. Python ≥ 3.10

```powershell
py --version
```

### 3. .env

```powershell
cd "D:\000 SEO Business\maxcontentseo\outreach-cli"
Copy-Item .env.example .env
```

Variablen:
- `SHEET_ID` — Spreadsheet-ID
- `GOOGLE_CREDENTIALS_PATH` — Pfad zur Service-Account-JSON
- `PRIMARY_TABS` — Stadt-Tabs (kommasepariert)
- `AGGREGATE_TABS` — Aggregat/Master-Tabs (kommasepariert)

### 4. Install

```powershell
py -m pip install -e .
```

### 5. Smoke-Test

```powershell
py -m outreach_cli status --email mytinyspa.frankfurt@googlemail.com
```

---

## Befehle

### `outreach status --email <EMAIL> [--json]`

Zeigt den Lead in **Primary-Tab UND Aggregat-Tab** (falls in beiden). Bei
Inkonsistenz zwischen den beiden warnt es.

```powershell
py -m outreach_cli status --email info@example.de
py -m outreach_cli status --email info@example.de --json
```

### `outreach set-status --email <EMAIL> --status <STATUS> [--column COL] [--date YYYY-MM-DD] [--json]`

Setzt eine Status-Spalte. **Schreibt synchron in Primary + Aggregat.** Default-
Spalte: `Verkaufsstatus`.

| Option | Default | Werte |
|---|---|---|
| `--column` | `Verkaufsstatus` | `Verkaufsstatus`, `Recherche_Status` |
| `--status` | (Pflicht) | `Angeschrieben`, `Follow-up gesendet`, `Geantwortet - kein Interesse`, `Geantwortet - Interesse`, `Bounce`, `Nicht kontaktiert` |
| `--date` | heute | `YYYY-MM-DD` |

Datums-Routing je nach Status:

| Status                         | Datumsspalte                                    |
|--------------------------------|-------------------------------------------------|
| `Angeschrieben`                | `KONTAKTIERT_AM`                                |
| `Follow-up gesendet`           | `FOLLOWUP_AM`                                   |
| `Geantwortet - kein Interesse` | `LETZTE_ANTWORT_AM` (Fallback `KONTAKTIERT_AM`) |
| `Geantwortet - Interesse`      | `LETZTE_ANTWORT_AM` (Fallback `KONTAKTIERT_AM`) |
| `Bounce`                       | `LETZTE_ANTWORT_AM` (Fallback `KONTAKTIERT_AM`) |
| `Nicht kontaktiert`            | _(kein Datum)_                                  |

```powershell
# Antwort eingegangen — Verkaufsstatus updaten (default --column)
py -m outreach_cli set-status --email info@example.de --status "Geantwortet - kein Interesse"

# Outreach-Lifecycle markieren — Recherche_Status
py -m outreach_cli set-status --email info@example.de --status "Angeschrieben" --column Recherche_Status --date 2026-05-11
```

### `outreach followups --stadt <STADT> [--date YYYY-MM-DD] [--json]`

Listet Leads mit `FOLLOWUP_AM = heute` (oder `--date`) für die Stadt.

```powershell
py -m outreach_cli followups --stadt Frankfurt
py -m outreach_cli followups --stadt "Bad Homburg" --date 2026-05-15
```

### `outreach hot [--column COL] [--json]`

Hot Leads: `Spalte = Geantwortet - Interesse` **oder** (`FOLLOWUP_AM ≥ heute`
**und** `SCORE ≥ 6` **und** nicht tot). Default-Spalte: `Verkaufsstatus`.

```powershell
py -m outreach_cli hot
py -m outreach_cli hot --column Recherche_Status
```

---

## Header-Synonym-Map

Tab-individuelle Header-Schreibweisen werden tolerant gematcht:

| Canonical | Akzeptierte Aliase |
|---|---|
| `FIRMA` | `.` (Alt-Frankfurt) |
| `STADT` | `Stadt` (Alle_Leads, Frankfurt_Umland) |
| `KONTAKTIERT_AM` | `KONTAKTIERT`, `KONTAKTIERT AM`, `Kontaktiert` (Alt-Muenchen) |
| `FOLLOWUP_AM` | `FOLLOW-UP`, `FOLLOW_UP`, `FOLLOWUP` (Alt-Muenchen) |

Damit funktioniert die CLI auch in Tabs die noch nicht umbenannt wurden.

---

## Aggregat-Sync

`set-status` schreibt **immer** in beide Tabs wenn der Lead in beiden steht:

```
Stadt-Tab (z.B. Frankfurt) → primary update
Alle_Leads                  → secondary update
```

Bei Inkonsistenz (unterschiedliche Werte vor Update) wird gewarnt, der Update
aber durchgeführt — beide Tabs konvergieren zum neuen Wert.

---

## Exit-Codes

| Code | Bedeutung                                          |
|------|----------------------------------------------------|
| 0    | OK                                                 |
| 1    | Lead nicht gefunden                                |
| 2    | API-Fehler oder Validierungsfehler (Datum, Status, Spalte) |

---

## JSON-Output

Mit `--json` liefert jeder Command Lead-Objekte in diesem Schema:

```json
{
  "_row_index": 34,
  "_tab": "Frankfurt",
  "firma": "My Tiny Spa",
  "stadt": "Frankfurt",
  "email": "mytinyspa.frankfurt@googlemail.com",
  "score": "5",
  "recherche_status": "Nicht kontaktiert",
  "verkaufsstatus": "Geantwortet - kein Interesse",
  "kontaktiert_am": "",
  "followup_am": "",
  "letzte_antwort_am": "11.05.2026",
  "seo_problem": ""
}
```

`status` liefert ein Objekt mit `{"primary": <lead>, "secondary": <lead>}`.
`set-status` liefert zusätzlich `{"column", "date_column", "date_value", "warnings"}`.

---

## Tests

```powershell
py -m pip install -e ".[dev]"
py -m pytest tests/
```

34 Tests, pure logic, kein API-Call. Header-Aliasing, Datums-Parsing,
Status→Spalte-Routing, Row-Normalisierung.

---

## Backup

Vor strukturellen Sheet-Migrationen wurde eine Sheet-Kopie als
`Lead_Tracker_Gesamt_Backup_2026-05-11` manuell im Browser erstellt.
Zusätzlich liegt ein JSON-Snapshot unter [backups/](backups/) mit allen
Tab-Inhalten zum Migrations-Zeitpunkt.

---

## Was outreach-cli NICHT macht (v1)

- **Kein E-Mail-Versand** — bleibt in `D:\000 SEO Business\Tools\send_outreach.ps1`
  etc. unangetastet.
- **Kein Apps-Script-Webhook** — direkter API-Zugriff.

---

## v2-Roadmap

- ~~Historische Stati aus `sent_log.csv` nachziehen~~ **✅ DONE 2026-05-11** —
  `v2_nachzieh.py` hat 101 Leads korrigiert (vom geschätzten 13). Asymmetrische
  Datums-Logik: KONTAKTIERT_AM behält älteres (Erstkontakt-Schutz),
  FOLLOWUP_AM behält neueres (letzter Touchpoint).
- Code-Review-Backlog abarbeiten — siehe [REVIEW-BACKLOG.md](REVIEW-BACKLOG.md)
  (CR-01, HI-01/03/04/05/06, ME-*, LO-*).
- `outreach send-followup --batch <stadt>` — Versand-Integration.
- `outreach doctor` — Schema-Health-Check als eingebautes Sub-Command.
- Tab-Cache mit TTL für CLI-Hot-Path (mehrfache Calls in derselben Pipeline).

## Exit-Codes

| Code | Bedeutung |
|---|---|
| 0 | OK |
| 1 | Lead nicht gefunden |
| 2 | API/Validierungs-Fehler |
| 3 | Partial-Failure bei `set-status` (Tabs nun inkonsistent — manuelles Recovery oder Retry) |

---

## Architektur (kurz)

```
outreach_cli/
├── config.py    # .env, Status-Whitelist, Header-Konstanten + Aliase, Tab-Klassen
├── sheets.py    # gspread-Wrapper + reine Logik (testbar ohne API)
└── cli.py       # typer commands + rich tables + JSON
```

`SheetClient` cached Tab-Inhalte pro Prozess. Mutationen invalidieren den Cache.
Eine CLI-Invocation = ein Prozess = ein Re-Fetch pro angefasstem Tab.
