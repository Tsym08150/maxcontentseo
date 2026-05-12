"""`outreach bounce-check` Command.

Pipeline:
  1. ImapConfig.from_env() — Bridge-Credentials prüfen
  2. BridgeImapClient — connect + login
  3. search_bounces(since_days) — IMAP-SEARCH auf 4 Bounce-Pattern
  4. fetch_raw(uid) + parse_bounce — MIME-Parse, failed_recipients extrahieren
  5. Cross-Ref gegen Sheet (Recherche_Status = "Angeschrieben")
  6. set_status(email, "Bounce", column=Recherche_Status) für jeden Match
  7. Output: Bounce-Rate + Liste

Aufruf:
  py -m outreach_cli bounce-check --tab Frankfurt_Umland
  py -m outreach_cli bounce-check --all-tabs --since-days 7
  py -m outreach_cli bounce-check --tab X --dry-run    # nur scannen, kein Sheet-Update
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from ..config import H_RECHERCHE_STATUS
from ..imap import (
    BridgeImapClient,
    ImapAuthError,
    ImapConnectError,
    parse_bounce,
)
from ..imap.client import ImapConfig
from ..sheets import LeadRow, SetStatusResult, SheetClient


@dataclass
class BounceMatch:
    """Ein gebouncter Recipient der im Sheet gefunden wurde."""
    email: str
    bounce_type: str  # permanent | transient | unknown
    bounce_subject: str
    received_date: str
    matched_lead: LeadRow
    set_status_result: Optional[SetStatusResult] = None


@dataclass
class BounceCheckResult:
    bounces_total: int = 0
    failed_recipients: list[str] = field(default_factory=list)
    matched_in_sheet: list[BounceMatch] = field(default_factory=list)
    unmatched_recipients: list[str] = field(default_factory=list)
    sheet_writes_ok: int = 0
    sheet_writes_failed: int = 0
    angeschrieben_in_scope: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def bounce_rate_pct(self) -> Optional[float]:
        """Bounces als Anteil der 'Angeschrieben'-Leads im Scope.

        None falls keine Angeschrieben-Leads im Scope gefunden (Division-by-Zero).
        """
        if self.angeschrieben_in_scope == 0:
            return None
        return (len(self.matched_in_sheet) / self.angeschrieben_in_scope) * 100.0


def run_bounce_check(
    *,
    tab: Optional[str] = None,
    all_tabs: bool = False,
    since_days: int = 2,
    dry_run: bool = False,
    sheet_client: Optional[SheetClient] = None,
    imap_cfg: Optional[ImapConfig] = None,
) -> BounceCheckResult:
    """Führt Bounce-Check aus. `tab` ODER `all_tabs` — nicht beides.

    Args:
        tab: Genau ein Tab (z.B. "Frankfurt_Umland").
        all_tabs: Alle in Config.tabs konfigurierten Tabs.
        since_days: IMAP-SEARCH-Fenster (default 2 Tage).
        dry_run: Wenn True, kein set_status — nur Detection + Output.
        sheet_client: Optional vor-konfigurierter SheetClient.
        imap_cfg: Optional vor-konfigurierte ImapConfig.

    Returns BounceCheckResult — Caller printet/formatiert.
    """
    result = BounceCheckResult()

    if not tab and not all_tabs:
        result.errors.append("FEHLER: --tab oder --all-tabs nötig.")
        return result
    if tab and all_tabs:
        result.errors.append("FEHLER: --tab und --all-tabs sind mutex.")
        return result

    # 1. SheetClient
    if sheet_client is None:
        from ..config import Config
        sheet_client = SheetClient(Config.from_env())

    scope_tabs = list(sheet_client.config.tabs) if all_tabs else [tab]  # type: ignore[list-item]

    # 2. Count "Angeschrieben" Leads in scope (für Bounce-Rate-Denominator)
    angeschrieben_emails: set[str] = set()
    for t in scope_tabs:
        try:
            for lead in sheet_client.iter_tab_rows(t):
                if lead.recherche_status.strip().lower() == "angeschrieben":
                    angeschrieben_emails.add(lead.email.lower())
        except Exception as e:
            result.errors.append(f"Sheet-Scan {t!r} fehlgeschlagen: {e}")
    result.angeschrieben_in_scope = len(angeschrieben_emails)

    # 3. IMAP — connect, search, fetch, parse
    if imap_cfg is None:
        try:
            imap_cfg = ImapConfig.from_env()
        except SystemExit as e:
            result.errors.append(str(e))
            return result

    try:
        with BridgeImapClient(imap_cfg) as imap:
            uids = imap.search_bounces(since_days=since_days)
            for uid in uids:
                try:
                    raw = imap.fetch_raw(uid)
                except Exception as e:
                    result.errors.append(f"FETCH UID {uid!r} failed: {e}")
                    continue
                bounce = parse_bounce(raw, own_user=imap_cfg.user, uid=uid)
                result.bounces_total += 1
                result.failed_recipients.extend(bounce.failed_recipients)

                # 4. Match gegen Sheet
                for recipient in bounce.failed_recipients:
                    lead = sheet_client.find_by_email(recipient, tabs=scope_tabs)
                    if lead is None:
                        # Auch in Aggregat suchen — manchmal lebt der Lead nur dort
                        lead = sheet_client.find_in_aggregate(recipient)
                    if lead is None:
                        result.unmatched_recipients.append(recipient)
                        continue

                    match = BounceMatch(
                        email=recipient,
                        bounce_type=bounce.bounce_type,
                        bounce_subject=bounce.subject,
                        received_date=bounce.received_date,
                        matched_lead=lead,
                    )

                    # 5. Sheet-Update — Recherche_Status = "Bounce"
                    if not dry_run:
                        try:
                            sr = sheet_client.set_status(
                                email=recipient,
                                status="Bounce",
                                when=date.today(),
                                column=H_RECHERCHE_STATUS,
                            )
                            match.set_status_result = sr
                            if sr.partial_failure or sr.total_failure:
                                result.sheet_writes_failed += 1
                                result.errors.append(
                                    f"set_status({recipient!r}) partial/total failure"
                                )
                            else:
                                result.sheet_writes_ok += 1
                        except Exception as e:
                            result.sheet_writes_failed += 1
                            result.errors.append(f"set_status({recipient!r}) raised: {e}")

                    result.matched_in_sheet.append(match)

    except ImapConnectError as e:
        result.errors.append(f"IMAP-Verbindung fehlgeschlagen: {e}")
    except ImapAuthError as e:
        result.errors.append(f"IMAP-Login fehlgeschlagen: {e}")
    except Exception as e:
        result.errors.append(f"Unerwarteter IMAP-Fehler: {type(e).__name__}: {e}")

    # Dedup
    result.failed_recipients = sorted(set(result.failed_recipients))
    result.unmatched_recipients = sorted(set(result.unmatched_recipients))

    return result
