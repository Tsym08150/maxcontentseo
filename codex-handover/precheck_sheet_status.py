"""precheck_sheet_status.py — Pre-Send Sheet-Status-Filter
================================================================
Pflicht-Cross-Check vor jedem Outreach-Batch.
Verhindert Doppel-/Triple-Versand an Leads, die im Google-Sheet
bereits einen blockierenden Status tragen (Follow-up gesendet,
Angeschrieben, Bounce, "Nicht kontaktieren"/DNC).

Erkenntnis 2026-05-19: leads.csv alleine reicht nicht. Das Google-
Sheet (Lead_Tracker_Gesamt) trägt eine zweite Wahrheit über bereits
kontaktierte Leads, die NICHT immer in leads.csv-sent landet
(z.B. wenn Outreach über andere Kanäle/Wellen lief).

Verhalten:
- Liest alle leads.csv-Zeilen mit status=ready
- Liest alle relevanten Sheet-Tabs via Service Account (read-only)
- Für jede ready-Email: prüft, ob sie in IRGENDEINEM Tab einen
  blockierenden Status trägt
- Bei Treffer: setzt status=skip + error="auto-skipped: <begründung>"
- Schreibt leads.csv atomar zurück (Move-Item-Pattern)
- Liefert Bericht (stdout) + Exit-Code

Exit-Codes:
  0 — OK (keine ready, oder alle ready geprüft, kein Blocker)
  0 — OK mit Filterungen (filtered > 0, geänderte CSV)
  2 — kritischer Fehler (Sheet-API down, CSV defekt etc.)

Aufruf von send_outreach.ps1 / outreach_cli:
  py -3 precheck_sheet_status.py --leads ".\leads.csv"
  → wenn exit != 0: STOP, kein Send
"""

import argparse
import csv
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime

# Service Account + Sheet Config
CRED_PATH = r"D:\000 SEO Business\Tools\GoogleAutomationfürAutomtischen schreiben inDokumenten\GoogleSheetMcp\credentials\google-service-account.json"
SHEET_ID = "19ak15Thx3icvmcviMLePG6d22psdWocBChTBNykorL0"
LOG_PATH = r"D:\000 SEO Business\Tools\GoogleAutomationfürAutomtischen schreiben inDokumenten\GoogleSheetMcp\logs\precheck.log"

# Tabs to scan + ihre Status-Spalten-Namen (oder None wenn dyn. Suche)
TABS_TO_SCAN = ["Hamburg", "Muenchen", "Frankfurt", "Frankfurt_Umland", "Bad Homburg", "Pipeline_v2_Qualified", "Alle_Leads"]

# Blockierende Status-Werte (case-insensitive substring match)
# Wenn der Status-String einen dieser Begriffe enthält, ist die Mail blockiert
BLOCKING_STATUSES_ALWAYS = [
    "bounce",
    "nicht kontaktieren",  # DNC
    "dnc",
    "closed",
    "hot",
    "warm",
    "reply",
    "last-touch gesendet",  # final state nach 3. Touch
    "last touch gesendet",
]

# Time-conditional blocking: blockiert nur wenn FOLLOWUP_AM weniger als N Tage her ist
# Policy (2026-05-19): "Follow-up gesendet" + FU vor < 7 Tagen = blockiert | ≥ 7 Tage = Last-Touch erlaubt
LAST_TOUCH_MIN_DAYS = 7
TIME_CONDITIONAL_STATUSES = [
    "follow-up gesendet",
    "followup gesendet",
    "angeschrieben",
    "sent",
    "versendet",
]

# Allowed (non-blocking) statuses — for clarity, leads with these continue
ALLOWED_STATUSES = ["neu", "test", "ungeprueft", ""]


def log(msg, file=sys.stdout):
    print(msg, file=file)


def write_persistent_log(entries):
    """Append run entries to log file for audit trail."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    ts = datetime.now().isoformat(timespec="seconds")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps({"ts": ts, **entry}, ensure_ascii=False) + "\n")


def _parse_dmy(s):
    if not s: return None
    s = s.strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try: return datetime.strptime(s, fmt).date()
        except ValueError: continue
    return None


def fetch_sheet_emails_with_status():
    """Returns: dict {email_lowercase: [(tab, row, status, firma, followup_am), ...]}"""
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        log("FEHLER: google-api-python-client nicht installiert. pip install google-api-python-client google-auth", sys.stderr)
        sys.exit(2)

    if not os.path.exists(CRED_PATH):
        log(f"FEHLER: Service-Account-JSON nicht gefunden: {CRED_PATH}", sys.stderr)
        sys.exit(2)

    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_file(CRED_PATH, scopes=scopes)
    svc = build("sheets", "v4", credentials=creds, cache_discovery=False)

    # First: get list of actual tabs (so we don't fail on non-existent tabs)
    meta = svc.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
    actual_tabs = {s["properties"]["title"] for s in meta["sheets"]}

    result = {}
    tabs_scanned = []

    for tab in TABS_TO_SCAN:
        if tab not in actual_tabs:
            continue
        try:
            res = svc.spreadsheets().values().get(
                spreadsheetId=SHEET_ID, range=f"{tab}!A1:Z"
            ).execute()
        except Exception as e:
            log(f"WARN: Tab '{tab}' fetch failed: {e}", sys.stderr)
            continue
        vals = res.get("values", [])
        if not vals:
            continue
        header = [h.strip() for h in vals[0]]
        # find email column index (heuristic: "EMAIL", "email", "E-Mail")
        email_col = None
        firma_col = None
        followup_col = None
        last_ant_col = None
        status_cols = []
        for i, h in enumerate(header):
            hl = h.lower()
            if email_col is None and ("email" in hl or "e-mail" in hl or "mail" == hl):
                email_col = i
            if firma_col is None and ("firma" in hl or "name" == hl):
                firma_col = i
            if followup_col is None and "followup_am" in hl:
                followup_col = i
            if last_ant_col is None and "letzte_antwort" in hl:
                last_ant_col = i
            # Status-bearing columns: Recherche_Status, OUTREACH_STATUS, AUDIT_EMPFEHLUNG, Verkaufsstatus, status
            if any(t in hl for t in ["recherche_status", "outreach_status", "audit_empfehlung", "verkaufsstatus", "status"]):
                status_cols.append((i, h))

        if email_col is None:
            continue  # no email col = no useful data

        tabs_scanned.append(tab)
        for ri, row in enumerate(vals[1:], start=2):
            if email_col >= len(row):
                continue
            email = (row[email_col] or "").strip().lower()
            if not email or "@" not in email:
                continue
            firma = row[firma_col].strip() if (firma_col is not None and firma_col < len(row)) else ""
            fu_am = row[followup_col].strip() if (followup_col is not None and followup_col < len(row)) else ""
            last_ant = row[last_ant_col].strip() if (last_ant_col is not None and last_ant_col < len(row)) else ""
            # collect all status values for this row
            status_snapshot = []
            for col_idx, col_name in status_cols:
                if col_idx < len(row):
                    v = (row[col_idx] or "").strip()
                    if v:
                        status_snapshot.append(f"{col_name}={v}")
            if email not in result:
                result[email] = []
            result[email].append({
                "tab": tab, "row": ri, "firma": firma,
                "statuses": status_snapshot,
                "followup_am": fu_am,
                "letzte_antwort_am": last_ant,
            })

    return result, tabs_scanned


def is_blocking(hit, today=None):
    """Returns blocking-reason string or None.
    Hit dict has: statuses[], followup_am, letzte_antwort_am, tab, firma.

    Policy:
    - BLOCKING_STATUSES_ALWAYS in any status → blocked, regardless of date
    - LETZTE_ANTWORT_AM present → blocked (Lead hat geantwortet, kein cold send)
    - TIME_CONDITIONAL_STATUSES + FU < LAST_TOUCH_MIN_DAYS → blocked
    - TIME_CONDITIONAL_STATUSES + FU ≥ LAST_TOUCH_MIN_DAYS → ALLOWED (Last-Touch eligible)
    """
    if today is None:
        today = datetime.now().date()
    # Antwort-Block: jede Antwort = kein cold send mehr
    if hit.get("letzte_antwort_am", "").strip():
        return f"Lead hat geantwortet ({hit['letzte_antwort_am']})"
    # Statuses durchlaufen
    for s in hit["statuses"]:
        sl = s.lower()
        # Always-block
        for block in BLOCKING_STATUSES_ALWAYS:
            if block in sl:
                return s
        # Time-conditional block
        for tcond in TIME_CONDITIONAL_STATUSES:
            if tcond in sl:
                fu_date = _parse_dmy(hit.get("followup_am", ""))
                if fu_date is None:
                    # Kein Datum → konservativ blocken
                    return s + " (kein FU-Datum — konservativ blockiert)"
                days_since = (today - fu_date).days
                if days_since < LAST_TOUCH_MIN_DAYS:
                    return f"{s} (FU vor {days_since}d, min {LAST_TOUCH_MIN_DAYS}d nötig)"
                # ≥ MIN_DAYS → eligible für Last-Touch, NICHT blockieren
                continue
    return None


def precheck(leads_path, dry_run=False):
    if not os.path.exists(leads_path):
        log(f"FEHLER: leads.csv nicht gefunden: {leads_path}", sys.stderr)
        return 2

    with open(leads_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    if not rows:
        log("INFO: leads.csv ist leer.")
        return 0

    ready_rows = [r for r in rows if (r.get("status") or "").strip().lower() == "ready"]
    log(f"INFO: {len(ready_rows)} ready-Rows in {leads_path}")

    if not ready_rows:
        log("INFO: Keine ready-Rows — nichts zu prüfen.")
        return 0

    log("INFO: Lade Sheet-Status (Service Account read-only) …")
    sheet_map, tabs_scanned = fetch_sheet_emails_with_status()
    log(f"INFO: Tabs gescannt: {tabs_scanned}")
    log(f"INFO: Sheet-Index: {len(sheet_map)} unique emails")

    filtered = []
    kept = []
    log_entries = []

    for r in ready_rows:
        email = (r.get("email") or "").strip().lower()
        hits = sheet_map.get(email, [])
        block_reason = None
        block_source = None
        for hit in hits:
            reason = is_blocking(hit)
            if reason:
                block_reason = reason
                block_source = f"{hit['tab']}!R{hit['row']} ({hit['firma']})"
                break
        if block_reason:
            filtered.append({"email": email, "reason": block_reason, "source": block_source})
            r["status"] = "skip"
            existing_err = (r.get("error") or "").strip()
            note = f"auto-skipped {datetime.now().strftime('%Y-%m-%d')}: {block_source} → {block_reason}"
            r["error"] = (existing_err + " | " + note).strip(" |") if existing_err else note
            log_entries.append({"action": "skip", "email": email, "block_source": block_source, "block_reason": block_reason})
        else:
            kept.append(email)

    # Report
    log("")
    log("=" * 70)
    log("PRECHECK SHEET STATUS — Ergebnis")
    log("=" * 70)
    log(f"  Ready vor Pre-Check : {len(ready_rows)}")
    log(f"  Behalten (sendbar)  : {len(kept)}")
    log(f"  Auto-skipped        : {len(filtered)}")
    log("")
    if filtered:
        log("Filtered Leads:")
        for f in filtered:
            log(f"  ✗ {f['email']}")
            log(f"      Quelle: {f['source']}")
            log(f"      Grund:  {f['reason']}")
        log("")
    if kept:
        log("Sendbare Leads (status=ready bleibt):")
        for e in kept:
            log(f"  ✓ {e}")
        log("")
    log("=" * 70)

    # Persist log entries
    if log_entries:
        log_entries.append({"action": "summary", "ready_before": len(ready_rows), "kept": len(kept), "filtered": len(filtered)})
        write_persistent_log(log_entries)
        log(f"INFO: Audit-Log: {LOG_PATH}")

    # Write back CSV (atomic via temp + replace)
    if filtered and not dry_run:
        tmp_path = leads_path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
                w.writeheader()
                w.writerows(rows)
            shutil.move(tmp_path, leads_path)
            log(f"INFO: leads.csv atomar aktualisiert — {len(filtered)} Rows von ready → skip")
        except Exception as e:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            log(f"FEHLER beim CSV-Write: {e}", sys.stderr)
            return 2

    if filtered and dry_run:
        log("INFO: --dry-run: leads.csv NICHT geändert. Würde aber {0} Rows skippen.".format(len(filtered)))

    return 0


def main():
    ap = argparse.ArgumentParser(description="Pre-Send Sheet-Status-Filter")
    ap.add_argument("--leads", default=r"D:\000 SEO Business\Tools\leads.csv",
                    help="Pfad zu leads.csv (default: Tools\\leads.csv)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Nur Vorschau, keine CSV-Änderung")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    rc = precheck(args.leads, dry_run=args.dry_run)
    sys.exit(rc)


if __name__ == "__main__":
    main()
