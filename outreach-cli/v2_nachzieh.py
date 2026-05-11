"""v2_nachzieh.py — Historische Stati aus sent_log.csv ins Sheet nachziehen.

Hintergrund:
  Apps-Script-Webhook lieferte über Monate "no value"-Responses ohne tatsächlich
  zu schreiben. Versand-Scripts (send_outreach.ps1 etc.) loggten Erfolg im
  sent_log.csv, das Sheet blieb aber stale. Bisher bestätigt:
    - 4 Muenchen-Leads mit H4_FU_Beauty sent → Sheet=Angeschrieben (statt Follow-up gesendet)
    - 1 Frankfurt-Lead (My Tiny Spa) → manuell bereits via outreach-cli korrigiert
    - Unbekannt viele weitere Leads in Frankfurt / Hamburg / Frankfurt_Umland.

Was dieses Skript macht:
  1. Liest sent_log.csv (alle Einträge mit status='sent')
  2. Pro Email: ermittelt Empfehlung (status + Datums) aus Versand-Historie
  3. Vergleicht mit Sheet-Zustand (Recherche_Status, KONTAKTIERT_AM, FOLLOWUP_AM)
  4. Generiert Update-Vorschlag pro Lead
  5. Zeigt Vorschau-Tabelle, wartet auf User-Bestätigung
  6. Bei Bestätigung: führt set-status durch (Aggregat-Sync wird über
     SheetClient.set_status automatisch erledigt)

Idempotency: bereits korrekte Leads werden via SheetClient.set_status() automatisch
geskippt (kein doppelter Write).

Lifecycle-Schutz:
  Leads die im Sheet bereits in einem Endzustand sind (Geantwortet*, Bounce)
  werden NIE downgegradet — egal was sent_log sagt.

Usage:
    py v2_nachzieh.py                    # Vorschau only, kein Write
    py v2_nachzieh.py --apply             # Nach Vorschau direkt schreiben
    py v2_nachzieh.py --apply --force     # Auch idempotente Re-Writes
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from outreach_cli.config import (
    H_KONTAKTIERT,
    H_FOLLOWUP,
    H_RECHERCHE_STATUS,
    Config,
)
from outreach_cli.sheets import SheetClient, SheetsAPIError, _parse_date

SENT_LOG = Path(r"D:\000 SEO Business\Tools\sent_log.csv")

# Stati die "fortgeschrittener" sind als Outreach — Downgrade verboten
TERMINAL_STATUSES = {
    "Geantwortet - kein Interesse",
    "Geantwortet - Interesse",
    "Bounce",
}


def template_type(t: str) -> str:
    """ERST vs FOLLOWUP vs unbekannt."""
    t = (t or "").upper()
    if "FU" in t or "FOLLOW" in t or t.startswith("H4"):
        return "FOLLOWUP"
    if t.startswith(("H1", "H2", "H3")):
        return "ERST"
    return "?"


def iso_to_de_date(s: str) -> str:
    """'2026-05-04 08:31:39' → '04.05.2026'. Leer falls Parsing fehlschlägt."""
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d.%m.%Y %H:%M:%S", "%d.%m.%Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%d.%m.%Y")
        except ValueError:
            continue
    return ""


def parse_to_date_obj(s: str) -> Optional[date]:
    """ISO oder DE → date-Object."""
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d.%m.%Y %H:%M:%S", "%d.%m.%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def load_sent_log() -> dict[str, list[dict]]:
    """Gruppiert sent_log.csv-Einträge mit status='sent' pro Email (lower-cased)."""
    if not SENT_LOG.exists():
        raise SystemExit(f"FEHLER: {SENT_LOG} nicht gefunden")

    by_email: dict[str, list[dict]] = defaultdict(list)
    with SENT_LOG.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            status = (row.get("status") or "").strip().lower()
            if status != "sent":
                continue
            em = (row.get("email") or "").strip().lower()
            if em:
                by_email[em].append(row)
    return by_email


def derive_recommendation(events: list[dict]) -> tuple[str, str, str]:
    """Aus sent_log-Events: (status, kontaktiert_am, followup_am).

    - Wenn FU-Versand vorhanden: status='Follow-up gesendet', FU_AM=spätester FU
    - Wenn nur Erst-Versand: status='Angeschrieben', KONT_AM=spätester Erst
    - In beiden Fällen: KONT_AM=frühester Erst (falls vorhanden)
    """
    erst_dates = sorted([
        (e.get("sent_at", ""), e) for e in events
        if template_type(e.get("template", "")) == "ERST"
    ])
    fu_dates = sorted([
        (e.get("sent_at", ""), e) for e in events
        if template_type(e.get("template", "")) == "FOLLOWUP"
    ])

    if not erst_dates and not fu_dates:
        return ("", "", "")

    kontaktiert_am = iso_to_de_date(erst_dates[0][0]) if erst_dates else ""
    followup_am = iso_to_de_date(fu_dates[-1][0]) if fu_dates else ""

    if fu_dates:
        status = "Follow-up gesendet"
    else:
        status = "Angeschrieben"

    return (status, kontaktiert_am, followup_am)


def status_outranks(current: str, target: str) -> bool:
    """True wenn current bereits 'weiter' im Lifecycle ist als target.
    Outreach-Lifecycle: Nicht kontaktiert → Angeschrieben → Follow-up gesendet → Geantwortet*/Bounce.
    """
    order = {
        "Nicht kontaktiert": 0,
        "": 0,
        "Angeschrieben": 1,
        "Follow-up gesendet": 2,
        "Geantwortet - kein Interesse": 3,
        "Geantwortet - Interesse": 3,
        "Bounce": 3,
    }
    return order.get(current, 0) > order.get(target, 0)


def date_field_for_status(status: str) -> str:
    """Welche Datumsspalte ist relevant für diesen Status?"""
    if status == "Angeschrieben":
        return H_KONTAKTIERT
    if status == "Follow-up gesendet":
        return H_FOLLOWUP
    return ""


def conservative_effective_date(
    current_str: str, rec_str: str, keep_when: str = "older"
) -> tuple[Optional[date], bool]:
    """Asymmetrische konservative Datums-Logik.

    keep_when='older' (für KONTAKTIERT_AM, Erstkontakt-Schutz):
      → behalte current wenn parsebar UND älter als rec.
    keep_when='newer' (für FOLLOWUP_AM, letzter-Touchpoint-Schutz):
      → behalte current wenn parsebar UND jünger als rec.

    Returns (effective_date_obj, keep_current_flag).
    """
    if not rec_str:
        return None, False
    current_d = parse_to_date_obj(current_str)
    rec_d = parse_to_date_obj(rec_str)
    if rec_d is None:
        return None, False
    if current_d is not None:
        if keep_when == "older" and current_d < rec_d:
            return None, True
        if keep_when == "newer" and current_d > rec_d:
            return None, True
    return rec_d, False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--apply", action="store_true",
                        help="Nach Vorschau direkt schreiben.")
    parser.add_argument("--force", action="store_true",
                        help="Auch idempotent-OK Leads neu schreiben.")
    parser.add_argument("--limit", type=int, default=0,
                        help="Nur erste N Leads bearbeiten (0=alle).")
    parser.add_argument("--sleep", type=float, default=3.0,
                        help="Pause in Sekunden zwischen Leads (Rate-Limit-Schutz).")
    parser.add_argument("--quota-retry-sleep", type=float, default=60.0,
                        help="Sleep bei 429-Quota-Error vor Retry.")
    parser.add_argument("--quota-retry-max", type=int, default=3,
                        help="Max Retry-Versuche bei 429.")
    parser.add_argument("--skip-emails", type=str, default="",
                        help="Kommagetrennte Liste von Emails die übersprungen werden sollen.")
    args = parser.parse_args()

    skip_set = {e.strip().lower() for e in args.skip_emails.split(",") if e.strip()}
    if skip_set:
        print(f"Skip-Emails: {sorted(skip_set)}")

    print("=" * 90)
    print(" v2_nachzieh — historische Stati aus sent_log ins Sheet nachziehen")
    print("=" * 90)

    sent_log = load_sent_log()
    print(f"\nsent_log.csv: {sum(len(v) for v in sent_log.values())} sent-events "
          f"in {len(sent_log)} eindeutigen Emails")

    cfg = Config.from_env()
    print(f"Primary-Tabs: {', '.join(cfg.primary_tabs)}")
    print(f"Aggregate-Tabs: {', '.join(cfg.aggregate_tabs)}")

    client = SheetClient(cfg)

    # Pro Email: ermittle Empfehlung + Sheet-Zustand
    pending_updates: list[dict] = []
    skipped: list[dict] = []
    not_found: list[str] = []

    for email, events in sent_log.items():
        if email in skip_set:
            skipped.append({"email": email, "tab": "?", "row": 0,
                            "reason": "in --skip-emails"})
            continue
        rec_status, rec_kont, rec_fu = derive_recommendation(events)
        if not rec_status:
            continue  # Keine relevanten Versand-Events

        try:
            lead = client.find_by_email(email)
        except SheetsAPIError as e:
            print(f"  [API-FEHLER] {email}: {e}")
            continue

        if lead is None:
            not_found.append(email)
            continue

        current_rs = lead.recherche_status
        current_kont = lead.kontaktiert_am
        current_fu = lead.followup_am

        # Lifecycle-Schutz: Terminal-Stati nicht downgraden
        if current_rs in TERMINAL_STATUSES:
            skipped.append({
                "email": email, "tab": lead.tab, "row": lead.row_index,
                "reason": f"current={current_rs!r} (terminal — protected)",
            })
            continue
        if status_outranks(current_rs, rec_status):
            skipped.append({
                "email": email, "tab": lead.tab, "row": lead.row_index,
                "reason": f"current={current_rs!r} > rec={rec_status!r} (downgrade blocked)",
            })
            continue

        # Asymmetrische Datums-Logik:
        # - KONTAKTIERT_AM = Erstkontakt, behalte ÄLTERES
        # - FOLLOWUP_AM    = letzter Touchpoint, behalte NEUERES
        eff_kont_date, keep_kont = conservative_effective_date(
            current_kont, rec_kont, keep_when="older")
        eff_fu_date, keep_fu = conservative_effective_date(
            current_fu, rec_fu, keep_when="newer")

        # Welches Datum wird der Haupt-set_status-Call schreiben?
        if rec_status == "Follow-up gesendet":
            main_date_obj = None if keep_fu else eff_fu_date
            main_date_keep = keep_fu
        elif rec_status == "Angeschrieben":
            main_date_obj = None if keep_kont else eff_kont_date
            main_date_keep = keep_kont
        else:
            main_date_obj = None
            main_date_keep = False

        # Pre-step für KONT-Backfill: nur wenn status='Follow-up gesendet'
        # UND current_kont leer ODER nicht-parsebar (z.B. 'Bounce') UND rec_kont da
        current_kont_parseable = parse_to_date_obj(current_kont) is not None
        needs_kont_backfill = (
            rec_status == "Follow-up gesendet"
            and not current_kont_parseable
            and bool(rec_kont)
        )

        # Idempotency: nichts zu tun wenn Status passt UND alle relevanten Datums
        # entweder bereits korrekt sind ODER per keep-Regel beibehalten werden
        date_in_sheet_obj = parse_to_date_obj(
            current_fu if rec_status == "Follow-up gesendet" else current_kont
        )
        status_already_ok = (current_rs == rec_status)
        date_already_ok = (
            main_date_keep
            or main_date_obj is None
            or date_in_sheet_obj == main_date_obj
        )

        if (status_already_ok and date_already_ok
                and not needs_kont_backfill and not args.force):
            skipped.append({
                "email": email, "tab": lead.tab, "row": lead.row_index,
                "reason": ("already in target state (incl. keep-rule)"
                           if (keep_kont or keep_fu) else "already in target state"),
            })
            continue

        pending_updates.append({
            "email": email,
            "tab": lead.tab,
            "row": lead.row_index,
            "firma": lead.firma,
            "current_rs": current_rs,
            "current_kont": current_kont,
            "current_fu": current_fu,
            "rec_status": rec_status,
            "rec_kont": rec_kont,
            "rec_fu": rec_fu,
            "needs_kont_backfill": needs_kont_backfill,
            "main_date_obj": main_date_obj,
            "keep_kont": keep_kont,
            "keep_fu": keep_fu,
        })

        if args.limit and len(pending_updates) >= args.limit:
            break

    # --- Vorschau ---
    print("\n" + "=" * 90)
    print(f" VORSCHAU: {len(pending_updates)} Updates, {len(skipped)} skipped, "
          f"{len(not_found)} not-found")
    print("=" * 90)

    if pending_updates:
        print(f"\n{'#':<3} {'TAB':<18} {'EMAIL':<38} {'CURRENT → REC':<55} {'DATES'}")
        print("-" * 160)
        for i, u in enumerate(pending_updates, start=1):
            change = f"{u['current_rs']!r} → {u['rec_status']!r}"
            kont_arrow = (
                f"{u['current_kont'] or '-'} [KEEP-KONT]" if u['keep_kont']
                else f"{u['current_kont'] or '-'}→{u['rec_kont'] or '-'}"
            )
            fu_arrow = (
                f"{u['current_fu'] or '-'} [KEEP-FU]" if u['keep_fu']
                else f"{u['current_fu'] or '-'}→{u['rec_fu'] or '-'}"
            )
            dates = f"K:{kont_arrow}  F:{fu_arrow}"
            if u['needs_kont_backfill']:
                dates += "  [+kont backfill]"
            print(f"{i:<3} {u['tab']:<18} {u['email'][:38]:<38} {change:<55} {dates}")

    if skipped:
        print(f"\nSkipped ({len(skipped)}):")
        for s in skipped[:20]:
            print(f"  - {s['email']} ({s['tab']} Z.{s['row']}): {s['reason']}")
        if len(skipped) > 20:
            print(f"  ... und {len(skipped) - 20} weitere")

    if not_found:
        print(f"\nNicht im Sheet gefunden ({len(not_found)}):")
        for em in not_found[:10]:
            print(f"  - {em}")
        if len(not_found) > 10:
            print(f"  ... und {len(not_found) - 10} weitere")

    if not pending_updates:
        print("\nNichts zu tun. Alle sent-Events bereits korrekt im Sheet abgebildet.")
        return 0

    # --- Apply ---
    if not args.apply:
        print("\n" + "=" * 90)
        print(" DRY-RUN — kein Write. Re-Run mit --apply zum Ausführen.")
        print("=" * 90)
        return 0

    print("\n" + "=" * 90)
    print(f" APPLY: {len(pending_updates)} Updates")
    print("=" * 90)
    succeeded = 0
    failed = 0
    partial = 0
    skipped_at_write = 0
    bounce_fixed: list[str] = []  # Track KONTAKTIERT_AM='Bounce' corrections

    def _retry_on_quota(fn, *fa, **fkw):
        """Wrappe set_status mit 429-Retry-Logik."""
        for attempt_idx in range(args.quota_retry_max + 1):
            try:
                return fn(*fa, **fkw)
            except SheetsAPIError as e:
                msg = str(e).lower()
                if "429" in msg or "quota" in msg or "rate" in msg:
                    if attempt_idx < args.quota_retry_max:
                        print(f"    [QUOTA] 429 erkannt, sleep {args.quota_retry_sleep}s "
                              f"(retry {attempt_idx+1}/{args.quota_retry_max})...")
                        time.sleep(args.quota_retry_sleep)
                        continue
                raise

    for i, u in enumerate(pending_updates, start=1):
        if u["current_kont"].lower() == "bounce":
            bounce_fixed.append(u["email"])
        em = u["email"]
        print(f"\n[{i}/{len(pending_updates)}] {em}  ({u['tab']} Z.{u['row']})")

        # Falls Status='Follow-up gesendet' und KONTAKTIERT_AM noch leer:
        # erst Angeschrieben + KONT_AM nachziehen
        if u["needs_kont_backfill"] and u["rec_kont"]:
            kont_obj = parse_to_date_obj(u["rec_kont"])
            if kont_obj:
                print(f"  Pre-Step: backfill KONTAKTIERT_AM via Status=Angeschrieben")
                try:
                    r1 = _retry_on_quota(
                        client.set_status, em, "Angeschrieben",
                        when=kont_obj, column=H_RECHERCHE_STATUS, force=args.force,
                    )
                except SheetsAPIError as e:
                    print(f"  [FAIL Pre-Step] {e}")
                    failed += 1
                    continue
                print(f"    -> {r1.writes_succeeded} ok, {r1.writes_skipped} skip, "
                      f"{r1.writes_failed} fail")
                for w in r1.warnings:
                    print(f"    ! {w}")

        # Haupt-Update: nutze konservativ ermitteltes effective Datum
        # (None = kein Datums-update, current bleibt)
        target_date_obj = u["main_date_obj"]
        if u["keep_kont"] or u["keep_fu"]:
            print(f"  [KEEP] aktuelles Datum bleibt erhalten")
        try:
            result = _retry_on_quota(
                client.set_status, em, u["rec_status"],
                when=target_date_obj, column=H_RECHERCHE_STATUS, force=args.force,
            )
        except SheetsAPIError as e:
            print(f"  [FAIL Main-Step] {e}")
            failed += 1
            continue
        print(f"  Update: {u['rec_status']!r}")
        for a in result.attempts:
            marker = "OK" if a.success and not a.skipped_idempotent else (
                "SKIP" if a.skipped_idempotent else "FAIL")
            print(f"    [{marker}] {a.tab} Z.{a.row_index}"
                  + (f" — {a.error}" if a.error else ""))
        for w in result.warnings:
            print(f"    ! {w}")

        if result.total_failure:
            failed += 1
        elif result.partial_failure:
            partial += 1
        elif result.writes_succeeded > 0:
            succeeded += 1
        else:
            skipped_at_write += 1

        # Rate-Limit-Schutz zwischen Leads
        if i < len(pending_updates) and args.sleep > 0:
            time.sleep(args.sleep)

    print("\n" + "=" * 90)
    print(f" ZUSAMMENFASSUNG: {succeeded} ok, {skipped_at_write} skip, "
          f"{partial} partial, {failed} fail")
    if bounce_fixed:
        print(f" Korruption gefixt (KONTAKTIERT_AM='Bounce' -> echtes Datum): "
              f"{len(bounce_fixed)} Leads")
        for em in bounce_fixed:
            print(f"   - {em}")
    print("=" * 90)
    if failed or partial:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
