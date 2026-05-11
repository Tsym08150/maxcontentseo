"""MailTransport Protocol — Abstraktion über Dry-Run und SMTP.

Phase 1 (heute): DryRunTransport schreibt .eml-Files.
Phase 2 (jetzt): SmtpTransport (in sender.py) versendet via ProtonMail.
Test-Self-Mode nutzt SmtpTransport mit hardcoded Ziel.

Beide Transports implementieren das gleiche `.deliver(...)` Interface.
`run_send` ist transport-agnostisch und branched nicht mehr intern.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Protocol

from .builder import BuiltMail, build_eml, write_eml


@dataclass(frozen=True)
class DeliveryResult:
    """Ergebnis eines einzelnen Versand-Attempts (egal welcher Transport)."""
    to_email: str
    subject: str
    body: str
    eml_bytes: bytes
    delivered: bool
    # Transport-spezifische Metadaten
    path: Optional[Path] = None           # DryRunTransport
    smtp_response: Optional[str] = None   # SmtpTransport
    delivered_at: Optional[datetime] = None
    error: Optional[str] = None
    retry_count: int = 0


class MailTransport(Protocol):
    """Protocol für alle Mail-Transports.

    Implementierungen:
      - DryRunTransport     → .eml-File in preview/
      - SmtpTransport       → echter Versand via ProtonMail
      - TestSelfTransport   → 1 Mail an Owner (Subset von SmtpTransport)
    """

    def deliver(
        self,
        *,
        index: int,
        to_email: str,
        from_email: str,
        subject: str,
        body: str,
    ) -> DeliveryResult: ...

    def name(self) -> str:
        """Kurzer Identifier für Logs ('dry-run', 'smtp', 'test-self')."""
        ...


class DryRunTransport:
    """Phase 1: schreibt .eml in preview/, kein Netzwerk."""

    def __init__(self, preview_dir: Path):
        self.preview_dir = preview_dir

    def name(self) -> str:
        return "dry-run"

    def deliver(
        self,
        *,
        index: int,
        to_email: str,
        from_email: str,
        subject: str,
        body: str,
    ) -> DeliveryResult:
        bm: BuiltMail = write_eml(
            out_dir=self.preview_dir,
            index=index,
            to_email=to_email,
            from_email=from_email,
            subject=subject,
            body=body,
        )
        return DeliveryResult(
            to_email=bm.to_email,
            subject=bm.subject,
            body=bm.body,
            eml_bytes=bm.eml_bytes,
            delivered=True,
            path=bm.path,
            delivered_at=datetime.now(),
        )
