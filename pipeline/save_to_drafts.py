"""save_to_drafts.py — Automatisches Draft-Ablegen in ProtonMail Entwürfe.

Bedingungen für automatisches Ablegen (ALLE müssen erfüllt sein):
- Empfänger nicht auf DNC-Liste (do_not_contact.txt) — R14, hart
- Kein Roast-Deadlock (roast_result != "DEADLOCK")
- NeverBounce: valid oder catch-all
- Dry-Run: DNC-Gate OK + Format OK
- Kein manueller Eingriff nötig war (manual_intervention=False)
- approvals.json erfolgreich geladen

Wenn eine Bedingung nicht erfüllt → STOPP mit Fehlermeldung, kein Send.
"""

from __future__ import annotations

import email as email_lib
import email.message
import email.utils
import imaplib
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

# DNC-/Suppression-Check (R14): zentrale, einzige Wahrheit (do_not_contact.txt
# via outreach_cli.suppression). Wir nutzen denselben Check wie das Send-Gate
# (one_shot_send.send_message -> DNCBlockedError) — kein neuer Check, gleiche
# Semantik. outreach-cli liegt als Schwesterordner (Pfad wie tools/sheets_client.py).
_OUTREACH_CLI_DIR = Path(__file__).parent.parent / "outreach-cli"
if str(_OUTREACH_CLI_DIR) not in sys.path:
    sys.path.insert(0, str(_OUTREACH_CLI_DIR))
from outreach_cli.suppression import is_suppressed

APPROVALS_PATH = Path(__file__).parent.parent / "config" / "approvals.json"
PIPELINE_LOG = Path(__file__).parent.parent.parent / "logs" / "pipeline-log.txt"
ENV_PATH = Path(__file__).parent.parent / "outreach-cli" / ".env"

IMAP_HOST = "127.0.0.1"
IMAP_PORT = 1143
DRAFTS_FOLDER = "Drafts"


def load_approvals() -> dict:
    if not APPROVALS_PATH.exists():
        raise FileNotFoundError(f"approvals.json nicht gefunden: {APPROVALS_PATH}")
    with APPROVALS_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_approvals(data: dict) -> None:
    with APPROVALS_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _check_gates(
    *,
    recipient: str,
    roast_result: str,
    neverbounce_status: str,
    dry_run_ok: bool,
    manual_intervention: bool,
    approvals: dict,
) -> tuple[bool, str]:
    """Prüft alle Gate-Bedingungen. Gibt (ok, reason) zurück."""
    # DNC-/Suppression-Gate (R14) — hart, identische Semantik zum Send-Gate
    # (one_shot_send.send_message -> DNCBlockedError): ein Treffer in
    # do_not_contact.txt blockt; fehlende Datei = fail-open (siehe suppression.py).
    if is_suppressed(recipient):
        return False, (
            f"Empfänger {recipient} steht auf der DNC-Liste (do_not_contact.txt) — "
            f"kein Draft abgelegt."
        )
    if roast_result == "DEADLOCK":
        return False, "Roast-Deadlock — manuelle Überarbeitung erforderlich"
    # role_account + smtp_connectable = Mailbox existiert, kein Hard-Bounce-Risiko
    # (confirmed_rule: "NeverBounce role_account bei smtp_connectable = kein STOPP")
    allowed_nb = {"valid", "catch-all", "role_account_smtp_connectable"}
    if neverbounce_status not in allowed_nb:
        return False, f"NeverBounce-Status '{neverbounce_status}' — nur {allowed_nb} erlaubt"
    if not dry_run_ok:
        return False, "Dry-Run fehlgeschlagen (DNC-Gate oder Format-Fehler)"
    if manual_intervention:
        return False, "Manueller Eingriff war nötig — automatisches Ablegen nicht erlaubt"
    if not approvals:
        return False, "approvals.json konnte nicht geladen werden"
    return True, ""


def _build_mime_message(
    sender: str,
    recipient: str,
    subject: str,
    body: str,
) -> email_lib.message.Message:
    msg = email_lib.message.Message()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg["Date"] = email_lib.utils.formatdate(localtime=True)
    msg["Content-Type"] = "text/plain; charset=utf-8"
    msg["Content-Transfer-Encoding"] = "quoted-printable"
    msg.set_payload(body, charset="utf-8")
    return msg


def _append_to_drafts(user: str, password: str, msg: email_lib.message.Message) -> None:
    """Legt msg als Entwurf in ProtonMail Drafts-Ordner ab via IMAP APPEND."""
    imap = imaplib.IMAP4(IMAP_HOST, IMAP_PORT)
    try:
        imap.login(user, password)
        raw = msg.as_bytes()
        result, data = imap.append(
            DRAFTS_FOLDER,
            r"\Draft",
            imaplib.Time2Internaldate(datetime.now(timezone.utc)),
            raw,
        )
        if result != "OK":
            raise RuntimeError(f"IMAP APPEND fehlgeschlagen: {result} {data}")
    finally:
        try:
            imap.logout()
        except Exception:
            pass


def _append_pipeline_log(domain: str, recipient: str, note: str) -> None:
    PIPELINE_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = (
        f"\n---\n"
        f"DATUM: {date.today().isoformat()}\n"
        f"DOMAIN: {domain}\n"
        f"AKTION: Draft in ProtonMail Entwürfe abgelegt\n"
        f"EMPFAENGER: {recipient}\n"
        f"HINWEIS: {note}\n"
        f"ERGEBNIS: READY (Draft abgelegt — wartet auf Georg-Freigabe)\n"
        f"---\n"
    )
    with PIPELINE_LOG.open("a", encoding="utf-8") as f:
        f.write(entry)


def save_draft(
    *,
    domain: str,
    recipient: str,
    subject: str,
    body: str,
    roast_result: str = "GUT",
    neverbounce_status: str = "valid",
    dry_run_ok: bool = True,
    manual_intervention: bool = False,
) -> None:
    """Hauptfunktion: prüft Gates, legt Draft ab, aktualisiert approvals.json."""

    # approvals.json laden
    try:
        approvals = load_approvals()
    except FileNotFoundError as e:
        print(f"STOPP: Automatisches Draft-Ablegen nicht möglich — {e}. Manuelle Freigabe erforderlich.")
        sys.exit(1)

    # Gate-Prüfung
    ok, reason = _check_gates(
        recipient=recipient,
        roast_result=roast_result,
        neverbounce_status=neverbounce_status,
        dry_run_ok=dry_run_ok,
        manual_intervention=manual_intervention,
        approvals=approvals,
    )
    if not ok:
        print(f"STOPP: Automatisches Draft-Ablegen nicht möglich — {reason}. Manuelle Freigabe erforderlich.")
        sys.exit(1)

    # Credentials laden
    load_dotenv(ENV_PATH)
    user = os.environ.get("PROTONMAIL_USER", "georg@maxcontentseo.de")
    password = os.environ.get("PROTONMAIL_BRIDGE_PASSWORD", "")
    if not password:
        print("STOPP: PROTONMAIL_BRIDGE_PASSWORD fehlt in .env. Manuelle Freigabe erforderlich.")
        sys.exit(1)

    # MIME-Nachricht bauen
    msg = _build_mime_message(
        sender=f"Georg Stopfer <{user}>",
        recipient=recipient,
        subject=subject,
        body=body,
    )

    # IMAP APPEND
    try:
        _append_to_drafts(user, password, msg)
    except Exception as e:
        print(f"STOPP: IMAP-Fehler — {e}. Draft wurde NICHT abgelegt und NICHT gesendet. Manuelle Freigabe erforderlich.")
        sys.exit(1)

    print(f"[save_to_drafts] Draft abgelegt: {recipient} | {subject}")

    # sent_domains aktualisieren
    today_str = date.today().isoformat()
    existing = {e["domain"] for e in approvals.get("sent_domains", [])}
    if domain not in existing:
        approvals.setdefault("sent_domains", []).append({"domain": domain, "date": today_str})

    # whitelist.domains_processed aktualisieren
    processed = approvals.setdefault("whitelist", {}).setdefault("domains_processed", [])
    domains_in_list = {e["domain"] for e in processed}
    if domain not in domains_in_list:
        processed.append({"domain": domain, "last_sent": today_str, "status": "Draft abgelegt"})
    else:
        for entry in processed:
            if entry["domain"] == domain:
                entry["last_sent"] = today_str
                entry["status"] = "Draft abgelegt"
                break

    save_approvals(approvals)
    print(f"[save_to_drafts] approvals.json aktualisiert: {domain} -> sent_domains")

    # Pipeline-Log
    _append_pipeline_log(domain, recipient, "Automatisches Draft-Ablegen — alle Gates OK")
    print(f"[save_to_drafts] Pipeline-Log aktualisiert.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Draft in ProtonMail Entwürfe ablegen")
    parser.add_argument("--domain", required=True, help="Domain des Leads (z.B. example-studio.de)")
    parser.add_argument("--to", required=True, help="Empfänger-E-Mail")
    parser.add_argument("--subject", required=True, help="Betreff")
    parser.add_argument("--body-file", required=True, help="Pfad zur .txt-Datei mit Mail-Body")
    parser.add_argument("--roast-result", default="GUT", choices=["GUT", "ÜBERARBEITEN", "DEADLOCK"])
    parser.add_argument("--neverbounce-status", default="valid")
    parser.add_argument("--dry-run-ok", action="store_true", default=True)
    parser.add_argument("--manual-intervention", action="store_true", default=False)
    args = parser.parse_args()

    body_path = Path(args.body_file)
    if not body_path.exists():
        print(f"FEHLER: Body-Datei nicht gefunden: {body_path}", file=sys.stderr)
        sys.exit(1)

    body = body_path.read_text(encoding="utf-8")

    save_draft(
        domain=args.domain,
        recipient=args.to,
        subject=args.subject,
        body=body,
        roast_result=args.roast_result,
        neverbounce_status=args.neverbounce_status,
        dry_run_ok=args.dry_run_ok,
        manual_intervention=args.manual_intervention,
    )
