# REVIEW-Backlog

Reste aus dem ersten Code-Review (siehe `REVIEW.md` für volle Details).
Diese Findings wurden in dieser Session **nicht** gefixt — bewusste Entscheidung
weil v2_nachzieh.py sie nicht triggert.

---

## TODO für nächste Session (nicht in dieser gefixt)

Explizite Checklist der offenen HIGH/MEDIUM Findings, sortiert nach Empfehlung.
Detaillierter Trigger + Aufwand in der Tabelle unten.

### CRITICAL (1 offen)
- [ ] **CR-01** — Inconsistency-warn-Block könnte bei Spelling-Drift versagen (`sheets.py:394-401`)

### HIGH (5 offen)
- [ ] **HI-01** — Echte SHEET_ID in `.env.example` durch Placeholder ersetzen
- [ ] **HI-03** — `_find_header` Alias-Precedence: Schema-Doctor-Subcommand für orphaned alt-Spalten
- [ ] **HI-04** — `followups_on` stadt-Typo: Validation gegen `config.primary_tabs`, fail-loud
- [ ] **HI-05** — `hot_leads` unparseable dates: Logger-Count + erweiterte `_parse_date` Formate
- [ ] **HI-06** — `set_status` Re-fetch entfernen: in-memory LeadRow-Update statt 2× API-Quota

### MEDIUM (8 offen)
- [ ] **ME-01** — `Config.from_env` `ConfigError` Custom-Exception statt `SystemExit`
- [ ] **ME-02** — `load_dotenv` Multi-path-search (CWD-aware)
- [ ] **ME-03** — `SetStatusResult` `frozen=True` mit mutable list — `frozen=False` oder `tuple`
- [ ] **ME-04** — `Sequence[str]` statt `Iterable[str]` für `tabs`-Parameter
- [ ] **ME-05** — CLI-Pfade testen via Typer `CliRunner`
- [ ] **ME-06** — `except Exception` in `cli.py` durch spezifische Exceptions ersetzen
- [ ] **ME-07** — `_parse_iso(date_) if date_ else date.today()` Dead-Branch entfernen
- [ ] **ME-08** — `_emit_json` `--pretty` Flag ODER README an compact-Output anpassen

### LOW (5 offen, optional)
- [ ] **LO-01** — `_DOTENV_PATH` CWD-Suche (Duplikat zu ME-02)
- [ ] **LO-02** — `sys.stderr.reconfigure(encoding="utf-8")` für Windows-cp1252
- [ ] **LO-03** — `__main__.py` `__name__` guard entfernen (Style)
- [ ] **LO-04** — Status-Spalten in `HEADER_ALIASES` (Sub-Issue zu CR-01)
- [ ] **LO-06** — `_parse_date` `%d/%m/%Y` entfernen (locale-ambiguous)
- [ ] **LO-07** — Type-Annotations: `Iterator`/`Sequence` statt `Iterable`

**Gesamt offen: 19 Findings (1 CRITICAL, 5 HIGH, 8 MEDIUM, 6 LOW)**

---

## In dieser Session gefixt

| ID | Severity | Fix |
|---|---|---|
| CR-02 | CRITICAL | `set_status` partial-failure handling via `SetStatusResult.partial_failure`/`total_failure`; CLI Exit-Code 3 für partial |
| CR-03 | CRITICAL | LETZTE_ANTWORT_AM-Fallback auf KONTAKTIERT_AM entfernt — Status-write läuft trotzdem, Datum wird gewarnt aber nicht destruktiv kopiert |
| HI-02 | HIGH | `find_by_email` fängt `gspread.APIError` → `SheetsAPIError` mit Tab-Kontext |
| LO-05 | LOW | Idempotency: skip wenn Status+Datum bereits ziel-konform; `--force` Flag zum Override |
| _bonus_ | — | `_lead_value` Header-aware lookup (mildert CR-01-Klasse latent) |
| _bonus_ | — | 15 neue Mutation-Tests (gspread-Mocks) — schließt ME-05 Coverage-Gap teilweise |

## Offen — v2

| ID | Severity | Was | Trigger | Aufwand |
|---|---|---|---|---|
| CR-01 | CRITICAL | Inconsistency-warn-Block könnte bei Verkaufsstatus/Recherche_Status-Drift versagen | Sheet bekommt Spalten-Spelling-Variante, die nicht in HEADER_ALIASES ist | M — Aliases erweitern oder `_normalize_row` fuzzy-matchen |
| HI-01 | HIGH | Echte `SHEET_ID` in `.env.example` committed | Repo geht public oder leaked | S — Placeholder + Dokumentation |
| HI-03 | HIGH | `_find_header` Alias-Precedence könnte orphaned alt-Spalten ignorieren | Sheet hat sowohl Canonical als Alias-Spalte mit unterschiedlichen Daten | M — Doctor-Subcommand das duplicates erkennt |
| HI-04 | HIGH | `followups_on` silent miss bei stadt-Typo | User schreibt `--stadt frankfurt-umland` statt `Frankfurt_Umland` | S — Validation gegen `config.primary_tabs`, fail-loud |
| HI-05 | HIGH | `hot_leads` drop unparseable dates silent | Sheet hat Datum-Werte in unbekanntem Format | S — Logger-Count + erweiterte `_parse_date` Formate |
| HI-06 | HIGH | `set_status` re-fetch nach write — TOCTOU + 2× API-Quota | Race mit anderem Writer | S — In-memory Update des LeadRow statt Re-fetch |
| ME-01 | MEDIUM | `Config.from_env` raises `SystemExit` aus Library-Modul | Anders testbar gemacht werden müssen | S — `ConfigError` Custom-Exception |
| ME-02 | MEDIUM | `load_dotenv` fixed Path, nicht CWD-aware | Pip-Install vs editable-install | S — Multi-path-search |
| ME-03 | MEDIUM | Frozen dataclass `SetStatusResult` mit mutable list field | Code-Smell, kein aktueller Bug | XS — `frozen=False` oder `tuple` |
| ME-04 | MEDIUM | `Optional[Iterable[str]]` Type könnte konsumierten Generator akzeptieren | API-Missbrauch | XS — `Sequence` statt `Iterable` |
| ME-05 | MEDIUM | Test-Coverage für CLI-Pfade fehlt | Refactoring riskant | M — Typer `CliRunner` |
| ME-06 | MEDIUM | `except Exception` in cli.py maskiert Bugs | Programmer-errors als "API-FEHLER" angezeigt | S — Spezifische Exceptions |
| ME-07 | MEDIUM | `_parse_iso(date_) if date_ else date.today()` redundant | Dead-Branch | XS — `_parse_iso(date_)` reicht |
| ME-08 | MEDIUM | `_emit_json` kompakt, README zeigt pretty | Doku-Mismatch | XS — `--pretty` Flag oder README anpassen |
| LO-01 | LOW | `_DOTENV_PATH` ignoriert CWD | Duplikat zu ME-02 | — |
| LO-02 | LOW | `⚠`-Emoji auf stderr kann cp1252 brechen | Windows-Konsole ohne UTF-8 | XS — `sys.stderr.reconfigure` (ich habe bereits `!` statt `⚠` in cli.py — fast gefixt) |
| LO-03 | LOW | `__main__.py` `__name__` guard redundant | — | — |
| LO-04 | LOW | Status-Spalten nicht in HEADER_ALIASES | Sub-Issue von CR-01 | — |
| LO-06 | LOW | `_parse_date` `%d/%m/%Y` locale-ambiguous | US-User | XS — entfernen |
| LO-07 | LOW | Type-Annotations: `Iterable` statt `Iterator`/`Sequence` | Type-Checker-Lärm | XS |

## Empfohlene Reihenfolge für v2-Aufräum-Pass

1. HI-01 (Sicherheit — schnell, hohe Wirkung)
2. HI-04 (User-Experience — schnell)
3. CR-01 (Datenqualität — mittel)
4. ME-06 (Debugability — schnell)
5. ME-01 + ME-02 (Testbarkeit — mittel)
6. HI-03 + HI-05 + HI-06 (zusammen ein Schema-Doctor-Subcommand)
7. ME-05 (CLI-Tests — mittel)
8. Rest (LO-* + ME-03/04/07/08 — Kosmetik)
