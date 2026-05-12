"""`outreach send` Command — Phase 1+2: Dry-Run + SMTP.

Pipeline:
  1. SheetClient öffnen (oder Test-Self: hardcoded Fake-Lead)
  2. leads.load_filtered_leads() — Tab/Score/Status/Limit/HWG-Filter
  3. templates.load_template() — Template + Frontmatter
  4. Pro Lead: render(template, render_vars) → subject + body
  5. transport.deliver(...) — DryRunTransport schreibt .eml, SmtpTransport sendet

Refactor (HIGH-04 Fix 2026-05-11): kein `if dry_run: ... else: ...` mehr im
Loop — Transport-Protocol macht das polymorph.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ..config import Config
from ..email.transport import (
    DeliveryResult,
    DryRunTransport,
    MailTransport,
)
from ..leads.loader import FilterStats, FilteredLead, load_filtered_leads
from ..sheets import SheetClient
from ..templates.engine import (
    MissingTemplateVariableError,
    Template,
    load_template,
    render,
)


@dataclass
class SendRunResult:
    template_name: str
    tab: str
    transport_name: str
    stats: FilterStats
    delivered: list[DeliveryResult] = field(default_factory=list)
    failed: list[DeliveryResult] = field(default_factory=list)
    skipped_render_errors: list[tuple[str, str]] = field(default_factory=list)
    sheet_sync_failures: list[tuple[str, str]] = field(default_factory=list)
    preview_dir: Optional[Path] = None

    @property
    def total_attempted(self) -> int:
        return len(self.delivered) + len(self.failed)

    @property
    def all_succeeded(self) -> bool:
        return self.total_attempted > 0 and not self.failed


def run_send(
    *,
    tab: str,
    template_name: str,
    transport: MailTransport,
    score_min: int = 0,
    status: Optional[str] = None,
    limit: int = 0,
    exclude_hwg: bool = True,
    from_email: str = "georg@maxcontentseo.de",
    sheet_client: Optional[SheetClient] = None,
    rate_limit_seconds: float = 0.0,
    restrict_to_emails: Optional[set[str]] = None,
) -> SendRunResult:
    """Führt den Send-Workflow aus mit gegebenem Transport.

    Args:
        tab: Sheet-Tab-Name (z.B. "Frankfurt_Umland")
        template_name: Template-Name ohne .txt (z.B. "variante_c")
        transport: DryRunTransport, SmtpTransport oder Custom-Implementierung
        score_min: Score-Schwelle (0 = kein Filter)
        status: Recherche_Status-Filter (None = kein Filter)
        limit: Max N Leads (0 = unbegrenzt)
        exclude_hwg: HWG-Heilpraktiker/Arzt-Ausschluss (default True)
        from_email: From-Header
        restrict_to_emails: Optional Whitelist — nur Leads mit Email in diesem Set
            werden versendet. Anderen werden silently dropped (CLI hat sie
            schon via verifier filtern lassen). Lowercase-Matching.
        sheet_client: Optionaler vor-konfigurierter Client (für Tests)
        rate_limit_seconds: Pause zwischen Versanden (für SMTP, nicht für dry-run)
    """
    import time as _time

    if sheet_client is None:
        sheet_client = SheetClient(Config.from_env())

    # Filter Leads
    filtered, stats = load_filtered_leads(
        sheet_client,
        tab=tab,
        score_min=score_min,
        status=status,
        limit=limit,
        exclude_hwg=exclude_hwg,
    )

    # Whitelist-Filter (z.B. nach Email-Verifikation in CLI). Silently drop.
    if restrict_to_emails is not None:
        allow = {e.strip().lower() for e in restrict_to_emails}
        filtered = [fl for fl in filtered if fl.email.strip().lower() in allow]

    # Template
    template: Template = load_template(template_name)

    # Render + Deliver via Transport
    from datetime import date as _date
    from ..config import H_RECHERCHE_STATUS

    delivered: list[DeliveryResult] = []
    failed: list[DeliveryResult] = []
    render_errors: list[tuple[str, str]] = []
    sync_failures: list[tuple[str, str]] = []  # (email, reason) — non-fatal
    is_live_send = transport.name() != "dry-run"

    for idx, fl in enumerate(filtered, start=1):
        try:
            subject, body = render(template, fl.render_vars)
        except MissingTemplateVariableError as e:
            render_errors.append((fl.email, str(e)))
            continue
        result = transport.deliver(
            index=idx,
            to_email=fl.email,
            from_email=from_email,
            subject=subject,
            body=body,
        )
        if result.delivered:
            delivered.append(result)
            # Sheet-Sync: Recherche_Status = "Angeschrieben" für erfolgreich gesendete
            # Mails. Verhindert Doppel-Versand beim nächsten Run (Filter --status Neu).
            # Nicht für Dry-Run — kein echter Versand passiert.
            # Non-fatal: wenn Sync fehlschlägt, ist die Mail trotzdem raus.
            if is_live_send:
                try:
                    sheet_client.set_status(
                        email=fl.email,
                        status="Angeschrieben",
                        when=_date.today(),
                        column=H_RECHERCHE_STATUS,
                    )
                except Exception as e:
                    sync_failures.append((fl.email, f"{type(e).__name__}: {e}"))
        else:
            failed.append(result)

        if rate_limit_seconds > 0 and idx < len(filtered):
            _time.sleep(rate_limit_seconds)

    # preview_dir nur befüllen wenn DryRunTransport
    preview_dir = getattr(transport, "preview_dir", None)

    return SendRunResult(
        template_name=template_name,
        tab=tab,
        transport_name=transport.name(),
        stats=stats,
        delivered=delivered,
        failed=failed,
        skipped_render_errors=render_errors,
        sheet_sync_failures=sync_failures,
        preview_dir=preview_dir,
    )
