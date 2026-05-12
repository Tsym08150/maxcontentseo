"""`outreach verify-emails` Command + Send-Pipeline-Hook.

Zwei Pfade:
  (A) Standalone-Aufruf:  `py -m outreach_cli verify-emails --tab X`
  (B) Pre-Send-Hook:      automatisch vor `outreach send --confirm-live` (CLI ruft
                          `run_verify_for_send_pipeline` direkt auf).

Output-Format: identisch (Table + Counts + JSON). Pfad B führt zusätzlich
Sheet-Updates auf "Email-Ungültig" für gefilterte Adressen aus.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

from ..config import H_RECHERCHE_STATUS, Config
from ..leads.loader import FilteredLead, load_filtered_leads
from ..sheets import SheetClient
from ..verifier import (
    BatchVerifyResult,
    EmailVerifyCache,
    VerificationBucket,
    VerificationDecision,
    verify_batch,
)


@dataclass
class VerifyReport:
    """Aufbereitetes Ergebnis für CLI-Rendering + Send-Filter."""
    batch: BatchVerifyResult
    sheet_updates_ok: int = 0
    sheet_updates_failed: int = 0
    sheet_update_errors: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.batch.decisions)

    @property
    def n_send(self) -> int:
        return len(self.batch.by_bucket(VerificationBucket.SEND))

    @property
    def n_warn(self) -> int:
        return len(self.batch.by_bucket(VerificationBucket.SEND_WITH_WARN))

    @property
    def n_skip(self) -> int:
        return len(self.batch.by_bucket(VerificationBucket.SKIP))

    @property
    def n_quota(self) -> int:
        return len(self.batch.by_bucket(VerificationBucket.QUOTA_ABORT))

    @property
    def n_error(self) -> int:
        return len(self.batch.by_bucket(VerificationBucket.ERROR))

    @property
    def sendable_emails(self) -> set[str]:
        return set(self.batch.sendable_emails)


def _mark_skipped_in_sheet(
    sheet_client: SheetClient,
    decisions: list[VerificationDecision],
) -> tuple[int, int, list[str]]:
    """Schreibt Recherche_Status='Email-Ungültig' für alle SKIP-Decisions.

    Returns (ok_count, failed_count, errors).
    """
    ok = 0
    failed = 0
    errs: list[str] = []
    for d in decisions:
        if d.bucket != VerificationBucket.SKIP:
            continue
        try:
            sr = sheet_client.set_status(
                email=d.email,
                status="Email-Ungültig",
                when=date.today(),
                column=H_RECHERCHE_STATUS,
            )
            if sr.partial_failure or sr.total_failure:
                failed += 1
                errs.append(f"set_status({d.email}): partial/total failure")
            else:
                ok += 1
        except Exception as e:
            failed += 1
            errs.append(f"set_status({d.email}): {type(e).__name__}: {e}")
    return ok, failed, errs


def run_verify_for_emails(
    emails: list[str],
    *,
    sheet_client: Optional[SheetClient] = None,
    apply_sheet_updates: bool = True,
) -> VerifyReport:
    """Verifiziert eine konkrete Email-Liste.

    Args:
        emails: Liste zu prüfender Adressen.
        sheet_client: Optional (für apply_sheet_updates und potentielle Lookups).
        apply_sheet_updates: Wenn True, SKIP-Decisions werden im Sheet auf
            "Email-Ungültig" gesetzt. Bei False nur Detection (für Dry-Run).
    """
    batch = verify_batch(emails)
    report = VerifyReport(batch=batch)

    if apply_sheet_updates and any(
        d.bucket == VerificationBucket.SKIP for d in batch.decisions
    ):
        if sheet_client is None:
            sheet_client = SheetClient(Config.from_env())
        ok, failed, errs = _mark_skipped_in_sheet(sheet_client, batch.decisions)
        report.sheet_updates_ok = ok
        report.sheet_updates_failed = failed
        report.sheet_update_errors = errs

    return report


def run_verify_for_tab(
    *,
    tab: str,
    score_min: int = 0,
    status_filter: Optional[str] = None,
    limit: int = 0,
    exclude_hwg: bool = True,
    sheet_client: Optional[SheetClient] = None,
    apply_sheet_updates: bool = True,
) -> tuple[VerifyReport, list[FilteredLead]]:
    """Lädt Leads aus Tab mit gleichen Filtern wie send + verifiziert.

    Wird vor send --confirm-live aufgerufen. Returns auch die geladenen Leads
    (damit Caller nicht doppelt laden muss).
    """
    if sheet_client is None:
        sheet_client = SheetClient(Config.from_env())

    leads, _stats = load_filtered_leads(
        sheet_client,
        tab=tab,
        score_min=score_min,
        status=status_filter,
        limit=limit,
        exclude_hwg=exclude_hwg,
    )

    emails = [l.email for l in leads if l.email]
    report = run_verify_for_emails(
        emails,
        sheet_client=sheet_client,
        apply_sheet_updates=apply_sheet_updates,
    )
    return report, leads
