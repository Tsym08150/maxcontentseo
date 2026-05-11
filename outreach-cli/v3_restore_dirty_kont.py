"""v3_restore_dirty_kont.py — Restauriert originale KONTAKTIERT-Datums
und korrigiert Recherche_Status für die 32 dirty leads.

Quelle: muenchen_email_update.ps1 + Pre-Cleanup-Snapshot 2026-04-27 (identisch).
Plus erstkontakte_28-04-2026_aus_gmail.csv für 1 Frankfurt-Lead.

Per-Lead-Logik:
  - Dirty-KONT = 'Bounce'              → Verkaufsstatus='Bounce',
                                          KONT=Original-Datum (wenn bekannt),
                                          RS=Original-Status
  - Dirty-KONT = 'Auto-Reply erhalten'  → KONT=Original-Datum,
                                          RS='Angeschrieben' (oder 'Follow-up gesendet'),
                                          Notiz in Naechste_Aktion 'Auto-Reply erhalten'
  - Dirty-KONT = 'Follow-up gesendet'   → KONT=Original-Datum,
                                          RS='Follow-up gesendet' (da FU am 29.04)

STRICT: per Default DRY-RUN. --apply zum Schreiben.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from outreach_cli.config import (
    H_KONTAKTIERT, H_FOLLOWUP, H_RECHERCHE_STATUS, H_VERKAUFSSTATUS, Config,
)
from outreach_cli.sheets import (
    SheetClient, SheetsAPIError, _find_header, _col_letter, _parse_date,
)

PS_PATH = Path(r"D:\000 SEO Business\muenchen_email_update.ps1")
ERSTKONTAKTE_CSV = Path(r"D:\000 SEO Business\Tools\sheet-sync\erstkontakte_28-04-2026_aus_gmail.csv")


def parse_de(s: str) -> Optional[date]:
    s = (s or "").strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%d.%m.%Y").date()
    except ValueError:
        return None


def load_originals() -> dict[str, dict]:
    """Email-lower → {kont: '21.04.2026', fu: '29.04.2026', orig_status: '...'}"""
    out: dict[str, dict] = {}
    # PS-Skript
    text = PS_PATH.read_text(encoding="utf-8", errors="replace")
    row_re = re.compile(r'@\(((?:"[^"]*",?\s*)+)\)')
    field_re = re.compile(r'"([^"]*)"')
    for m in row_re.finditer(text):
        fields = field_re.findall(m.group(1))
        if len(fields) < 10:
            continue
        firma, stadt, branche, website, email, score, prio, status, kont, fu = fields[:10]
        em = email.strip().lower()
        if not em or "@" not in em:
            continue
        out[em] = {"kont": kont.strip(), "fu": fu.strip(), "orig_status": status.strip()}

    # erstkontakte_28-04-2026 CSV
    import csv
    if ERSTKONTAKTE_CSV.exists():
        with ERSTKONTAKTE_CSV.open(encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                em = (r.get("EMAIL") or "").strip().lower()
                kont = (r.get("KONTAKTIERT_AM") or "").strip()
                fu = (r.get("FOLLOWUP_AM") or "").strip()
                stat = (r.get("Recherche_Status") or "").strip()
                if em and em not in out and kont:
                    out[em] = {"kont": kont, "fu": fu, "orig_status": stat}
    return out


def classify_dirty(dirty_value: str) -> str:
    """Was bedeutet der dirty KONT-Wert semantisch?"""
    v = dirty_value.strip().lower()
    if v == "bounce":
        return "bounce"
    if v == "follow-up gesendet":
        return "fu_sent_marker"
    if "auto" in v and "reply" in v:
        return "autoreply"
    return "unknown"


def build_plan(
    client: SheetClient, originals: dict[str, dict]
) -> list[dict]:
    """Plan nach User-Patterns (final 2026-05-11):
      P1: KONT='Follow-up gesendet'  → KONT='', RS='Follow-up gesendet'
      P2: KONT='Bounce' + RS='Angeschrieben' (kein FU)
          → KONT=Original-Datum (oder leer), VK='Bounce', RS bleibt
      P3: KONT='Bounce' + RS='Follow-up gesendet' (FU im sent_log)
          → KONT='' (leeren), VK='Bounce', RS bleibt
      P4: KONT='Auto-Reply erhalten'
          → KONT=Original-Datum, RS='Follow-up gesendet' (wenn FU),
             Naechste_Aktion += 'Auto-Reply erhalten <datum>'
    """
    plans: list[dict] = []
    for tab in client.config.primary_tabs:
        try:
            headers, data = client._load_tab(tab)
        except Exception as e:
            print(f"  [{tab}] FAIL load: {e}")
            continue
        kont_idx = _find_header(headers, H_KONTAKTIERT)
        fu_idx = _find_header(headers, H_FOLLOWUP)
        rs_idx = _find_header(headers, H_RECHERCHE_STATUS)
        vk_idx = _find_header(headers, H_VERKAUFSSTATUS)
        email_idx = _find_header(headers, "EMAIL")
        na_idx = _find_header(headers, "Naechste_Aktion")
        if kont_idx is None or email_idx is None:
            continue

        for offset, row in enumerate(data, start=2):
            if kont_idx >= len(row):
                continue
            kont_val = row[kont_idx].strip()
            if not kont_val or _parse_date(kont_val) is not None:
                continue  # parsebares Datum oder leer → skip
            em = row[email_idx].strip().lower() if email_idx < len(row) else ""
            cur_fu = row[fu_idx].strip() if fu_idx is not None and fu_idx < len(row) else ""
            cur_rs = row[rs_idx].strip() if rs_idx is not None and rs_idx < len(row) else ""
            cur_vk = row[vk_idx].strip() if vk_idx is not None and vk_idx < len(row) else ""
            cur_na = row[na_idx].strip() if na_idx is not None and na_idx < len(row) else ""

            classification = classify_dirty(kont_val)
            orig = originals.get(em)
            orig_kont = orig["kont"] if orig else ""

            # Initial: alle Werte = current
            new_kont = kont_val
            new_fu = cur_fu
            new_rs = cur_rs
            new_vk = cur_vk
            new_na = cur_na
            actions: list[str] = []
            pattern = "?"

            if classification == "fu_sent_marker":
                pattern = "P1"
                # KONT=Original-Datum aus PS-Skript (User-Update 2026-05-11),
                # Fallback leer wenn kein Original.
                if orig_kont:
                    new_kont = orig_kont
                    actions.append(f"KONT '{kont_val}' → '{orig_kont}' (Original aus PS-Skript)")
                else:
                    new_kont = ""
                    actions.append(f"KONT '{kont_val}' → '' (Original unbekannt)")
                if cur_rs != "Follow-up gesendet":
                    new_rs = "Follow-up gesendet"
                    actions.append(f"RS '{cur_rs}' → 'Follow-up gesendet'")

            elif classification == "bounce":
                # P2 oder P3?
                if cur_rs == "Follow-up gesendet":
                    pattern = "P3"
                    new_kont = ""
                    actions.append(f"KONT '{kont_val}' → '' (P3: FU dokumentiert, Original unbekannt)")
                else:
                    pattern = "P2"
                    if orig_kont:
                        new_kont = orig_kont
                        actions.append(f"KONT '{kont_val}' → '{orig_kont}' (Versuchs-Datum)")
                    else:
                        new_kont = ""
                        actions.append(f"KONT '{kont_val}' → '' (Original unbekannt)")
                if cur_vk != "Bounce":
                    new_vk = "Bounce"
                    actions.append(f"VK '{cur_vk}' → 'Bounce'")

            elif classification == "autoreply":
                pattern = "P4"
                if orig_kont:
                    new_kont = orig_kont
                    actions.append(f"KONT '{kont_val}' → '{orig_kont}'")
                else:
                    new_kont = ""
                    actions.append(f"KONT '{kont_val}' → '' (Original unbekannt)")
                if cur_fu and parse_de(cur_fu) and cur_rs != "Follow-up gesendet":
                    new_rs = "Follow-up gesendet"
                    actions.append(f"RS '{cur_rs}' → 'Follow-up gesendet' (FU dokumentiert)")
                # Notiz in Naechste_Aktion
                note = f"Auto-Reply erhalten {orig_kont or '?'}"
                if note not in cur_na:
                    new_na = f"{cur_na} | {note}".strip(" |") if cur_na else note
                    actions.append(f"Naechste_Aktion: + '{note}'")
            else:
                pattern = "UNKNOWN"
                actions.append(f"UNKNOWN: {kont_val!r}")

            if actions:
                plans.append({
                    "tab": tab,
                    "row_index": offset,
                    "email": em,
                    "pattern": pattern,
                    "classification": classification,
                    "cur_kont": kont_val,
                    "cur_fu": cur_fu,
                    "cur_rs": cur_rs,
                    "cur_vk": cur_vk,
                    "cur_na": cur_na,
                    "new_kont": new_kont,
                    "new_fu": new_fu,
                    "new_rs": new_rs,
                    "new_vk": new_vk,
                    "new_na": new_na,
                    "actions": actions,
                    "kont_idx": kont_idx,
                    "fu_idx": fu_idx,
                    "rs_idx": rs_idx,
                    "vk_idx": vk_idx,
                    "na_idx": na_idx,
                })
    return plans


def _build_updates_for_row(
    headers: list[str], row_index: int, target: dict
) -> list[dict]:
    """Baut Update-Dicts für eine Row basierend auf target {col: new_value}."""
    updates = []
    for col_name, new_val in target.items():
        col_idx = _find_header(headers, col_name)
        if col_idx is None:
            continue
        updates.append({
            "range": f"{_col_letter(col_idx)}{row_index}",
            "values": [[new_val]],
        })
    return updates


def _sync_to_aggregate(
    client: SheetClient, email: str, target: dict
) -> str:
    """Schreibt die Ziel-Werte zusätzlich in Alle_Leads. Returns status string."""
    for agg_tab in client.config.aggregate_tabs:
        try:
            headers, data = client._load_tab(agg_tab)
        except Exception as e:
            return f"AGG-LOAD-FAIL: {e}"
        email_idx = _find_header(headers, "EMAIL")
        if email_idx is None:
            continue
        for offset, row in enumerate(data, start=2):
            if email_idx >= len(row):
                continue
            if row[email_idx].strip().lower() == email.lower():
                # Build updates only for cells whose current value differs
                actual_updates = []
                for col_name, new_val in target.items():
                    col_idx = _find_header(headers, col_name)
                    if col_idx is None:
                        continue
                    cur_val = row[col_idx].strip() if col_idx < len(row) else ""
                    if cur_val == new_val:
                        continue
                    actual_updates.append({
                        "range": f"{_col_letter(col_idx)}{offset}",
                        "values": [[new_val]],
                    })
                if not actual_updates:
                    return f"AGG-NOOP (Z.{offset})"
                try:
                    ws = client._sh.worksheet(agg_tab)
                    ws.batch_update(actual_updates, value_input_option="USER_ENTERED")
                    client._invalidate(agg_tab)
                    return f"AGG-OK Z.{offset} ({len(actual_updates)} cells)"
                except Exception as e:
                    return f"AGG-FAIL: {e}"
        return f"AGG-NOT-FOUND"
    return "no aggregate tabs"


def apply_plan(client: SheetClient, plans: list[dict], sleep: float, dry: bool) -> dict:
    stats = {"ok": 0, "fail": 0, "agg_ok": 0, "agg_fail": 0, "agg_skip": 0}
    for i, p in enumerate(plans, start=1):
        print(f"\n[{i}/{len(plans)}] {p['email']} ({p['tab']} Z.{p['row_index']})")
        for a in p["actions"]:
            print(f"    {a}")
        if dry:
            continue

        # Primary update
        target = {
            "KONTAKTIERT_AM": p["new_kont"],
            "FOLLOWUP_AM": p["new_fu"],
            "Recherche_Status": p["new_rs"],
            "Verkaufsstatus": p["new_vk"],
            "Naechste_Aktion": p["new_na"],
        }
        # nur Felder die sich ändern
        diffs = {k: v for k, v in target.items() if v != {
            "KONTAKTIERT_AM": p["cur_kont"], "FOLLOWUP_AM": p["cur_fu"],
            "Recherche_Status": p["cur_rs"], "Verkaufsstatus": p["cur_vk"],
            "Naechste_Aktion": p["cur_na"],
        }[k]}

        if not diffs:
            print(f"    (no primary changes)")
        else:
            try:
                headers, _ = client._load_tab(p["tab"])
                updates = _build_updates_for_row(headers, p["row_index"], diffs)
                if updates:
                    ws = client._sh.worksheet(p["tab"])
                    ws.batch_update(updates, value_input_option="USER_ENTERED")
                    client._invalidate(p["tab"])
                    stats["ok"] += 1
                    print(f"    [PRIMARY-OK] {len(updates)} cells")
            except Exception as e:
                stats["fail"] += 1
                print(f"    [PRIMARY-FAIL] {e}")
                continue

        # Aggregate sync
        agg_status = _sync_to_aggregate(client, p["email"], diffs or target)
        if "OK" in agg_status:
            stats["agg_ok"] += 1
        elif "NOOP" in agg_status or "NOT-FOUND" in agg_status:
            stats["agg_skip"] += 1
        else:
            stats["agg_fail"] += 1
        print(f"    [AGGREGATE] {agg_status}")

        if i < len(plans):
            time.sleep(sleep)
    return stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Schreiben (sonst Dry-Run).")
    ap.add_argument("--sleep", type=float, default=2.0)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--pick-emails", type=str, default="",
                    help="Kommagetrennte Emails — nur diese verarbeiten.")
    args = ap.parse_args()
    picks = {e.strip().lower() for e in args.pick_emails.split(",") if e.strip()}

    cfg = Config.from_env()
    client = SheetClient(cfg)
    originals = load_originals()
    print(f"Original-Datenquelle: {len(originals)} Emails geladen.\n")

    plans = build_plan(client, originals)
    if picks:
        plans = [p for p in plans if p["email"].lower() in picks]
    if args.limit:
        plans = plans[:args.limit]
    print(f"Plan-Größe: {len(plans)} Updates\n")

    if not plans:
        print("Nichts zu tun.")
        return 0

    if not args.apply:
        for i, p in enumerate(plans, start=1):
            print(f"[{i}] {p['email']:<42}  {p['tab']:<18} Z.{p['row_index']}")
            for a in p["actions"]:
                print(f"     • {a}")
        print(f"\nDRY-RUN. {len(plans)} Updates geplant. --apply zum Schreiben.")
        return 0

    print("=" * 90)
    print(f" APPLY: {len(plans)} Updates")
    print("=" * 90)
    stats = apply_plan(client, plans, args.sleep, dry=False)
    print(f"\n=== SUMMARY: {stats['ok']} ok, {stats['fail']} fail ===")
    return 0 if stats["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
