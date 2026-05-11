# Changelog

Alle nennenswerten Änderungen an maxcontentseo werden in dieser Datei
dokumentiert.

Format: [Keep a Changelog](https://keepachangelog.com/),
Versionierung locker an Datum gebunden (kein SemVer — Site ist statisch,
keine API-Verträge).

---

## [2026-05-11] Sheet-Migration + outreach-cli + historische Daten-Restauration

### Added
- **outreach-cli** (Python CLI mit 4 Befehlen: `status`, `set-status`,
  `followups`, `hot`). Zwischenschicht zwischen Claude Code und
  `Lead_Tracker_Gesamt`. Service-Account-Auth via `gspread`.
- **52 Tests** (37 reine Logik + 15 Mutation-Tests mit gspread-Mocks).
- **JSON-Backup-System** lokal in `outreach-cli/backups/` (nicht im Repo —
  enthält Lead-Daten).
- **`LETZTE_ANTWORT_AM`-Spalte** in allen Stadt-Tabs (Muenchen, Hamburg,
  Frankfurt, Frankfurt_Umland, Bad Homburg) sowie Alle_Leads.
- **Bad Homburg** als neuer Tab im Sheet, mit 9 Pilot-Leads importiert.
- **`Verkaufsstatus`-Spalte** in Frankfurt_Umland (fehlte vorher).
- **Two-Spalten-Status-Modell**: `Recherche_Status` (Outreach-Lifecycle)
  getrennt von `Verkaufsstatus` (Sales-Outcome).

### Fixed
- **Apps-Script-Webhook-Bug** (monatelange stille "no value"-Responses ohne
  tatsächliche Schreibvorgänge). Ersetzt durch direkten Sheets-API-Zugriff.
- **101 Leads** mit korrekten historischen Stati und Datums aus `sent_log.csv`
  ins Sheet nachgezogen via `outreach-cli/v2_nachzieh.py`. Asymmetrische
  Datums-Logik: `KONTAKTIERT_AM` keep-older, `FOLLOWUP_AM` keep-newer.
- **32 pre-existing dirty rows** mit Status-Texten in der `KONTAKTIERT_AM`-Spalte
  (Hinterlassenschaften aus `muenchen_email_update.ps1`-Era vor sent_log)
  restauriert via `outreach-cli/v3_restore_dirty_kont.py`. Original-Datums aus
  zwei unabhängigen Datenquellen rekonstruiert.
- **Frankfurt-Header repariert**: Spalte 1 hieß `.` → `FIRMA` umbenannt,
  `STADT`-Spalte ergänzt (mit "Frankfurt" befüllt), `FOLLOWUP_AM` ergänzt,
  4 leere Schrott-Spalten gelöscht, doppelter `VERKAUFSWINKEL` zu
  `Verkaufswinkel` normalisiert.
- **Muenchen-Header normalisiert**: `KONTAKTIERT` → `KONTAKTIERT_AM`,
  `FOLLOW-UP` → `FOLLOWUP_AM`. (Diese Diskrepanz war monatelang Ursache von
  silent Webhook-Failures bei Muenchen-Leads.)
- **My Tiny Spa** (Frankfurt Z.34): `Verkaufsstatus` korrekt auf
  `Geantwortet - kein Interesse` gesetzt — vorheriger Webhook-Versuch hatte
  nichts geschrieben.

### Changed
- **Sheet-Updates** laufen ab jetzt via direkte Google-Sheets-API +
  Service-Account, nicht mehr via Apps-Script-Webhook.
- **Status-Migration** für 7 alte Tools-Scripts (`send_outreach.ps1`,
  `send_followup_*.ps1`, `sync_update.py`, `Update_Muenchen_Followup_Status.ps1`
  u.a.) ist kompatibel: die Scripts schreiben weiterhin `KONTAKTIERT_AM` und
  `FOLLOWUP_AM` (Header-Namen die jetzt im Sheet existieren — vorher gabs
  Diskrepanzen).
- **`Alle_Leads`-Aggregat-Tab** Spalte 1 `Stadt` → `STADT` (Konsistenz mit
  anderen Tabs).
- **`outreach-cli/.gitignore`** um `backups/` und `.env` erweitert.

### Security
- **`backups/`** in `.gitignore` ergänzt — Lead-Daten (Emails, Firmen,
  Stati, ~190 Datensätze) bleiben ausschließlich lokal, nicht im public Repo.
- **`.env`** in `.gitignore` — Service-Account-JSON-Pfade verlassen die
  Maschine nicht.
- **`.env.example`** committet ohne Secrets (SHEET_ID + Service-Account-Pfad
  als Placeholder erkennbar — siehe HI-01 in `outreach-cli/REVIEW-BACKLOG.md`
  als TODO für nächste Session, real-looking IDs durch echte Placeholder
  ersetzen).
- **Service-Account-JSON** (private_key) liegt ausschließlich unter
  `D:\000 SEO Business\Tools\...\credentials\` — niemals im Repo, niemals in
  Logs, niemals in Test-Fixtures.

### Documentation
- **`AGENTS.md`** — neue Sektionen "Lead-Tracker — Datenkorruption-Notiz"
  und "Sheet-Migration 11.05.2026 — Stand nach Cleanup".
- **`outreach-cli/README.md`** — "Why this exists" + Architektur-Highlights
  ergänzt.
- **`outreach-cli/REVIEW.md`** — 24 Findings aus gsd-code-reviewer-Lauf.
- **`outreach-cli/REVIEW-BACKLOG.md`** — 19 offene Findings als TODO-Checkboxen
  (1 CRITICAL, 5 HIGH, 8 MEDIUM, 5 LOW) für nächste Session.
