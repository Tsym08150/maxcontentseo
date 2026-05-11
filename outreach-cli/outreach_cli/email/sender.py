"""SmtpTransport — Phase 2 SMTP-Versand via ProtonMail (oder kompatibler Anbieter).

Verhalten:
  - STARTTLS auf Port 587 (Standard ProtonMail-Submission)
  - Login mit SMTP_USER + SMTP_TOKEN (App-Password aus .env)
  - Retry-Logik bei transienten Errors (Timeout, ConnectionError):
      max_retries=3 Versuche, exponentielles Backoff (1s, 2s, 4s)
  - Permanente Errors (auth, addr rejected) → kein Retry, sofort fail
  - Rate-Limiting passiert AUSSERHALB dieses Moduls (im run_send-Loop)

Token wird NICHT geloggt — auch nicht bei Auth-Fail.

Achtung: Dieses Modul heißt `outreach_cli.email.sender`. `smtplib` und
`email.*` in den Imports referenzieren die **Python-Standard-Library**.
"""

from __future__ import annotations

import smtplib
import socket
import time
from datetime import datetime
from email.message import EmailMessage  # stdlib (typing only)
from typing import Optional

from ..config import SmtpConfig
from .builder import build_eml
from .transport import DeliveryResult


# SMTP-Errors die einen Retry rechtfertigen (transient)
_RETRYABLE_ERRORS: tuple[type, ...] = (
    socket.timeout,
    TimeoutError,
    ConnectionError,
    smtplib.SMTPServerDisconnected,
    smtplib.SMTPConnectError,
)

# SMTP-Errors die KEINEN Retry rechtfertigen (permanent)
_PERMANENT_ERRORS: tuple[type, ...] = (
    smtplib.SMTPAuthenticationError,
    smtplib.SMTPSenderRefused,
    smtplib.SMTPRecipientsRefused,
    smtplib.SMTPDataError,
    smtplib.SMTPNotSupportedError,
)


class SmtpTransport:
    """Echter SMTP-Versand. Per default 3 Retries bei transienten Errors.

    Nutzung:
        config = SmtpConfig.from_env()
        transport = SmtpTransport(config, max_retries=3)
        result = transport.deliver(index=1, to_email=..., ...)

    Verbindung wird pro deliver() neu auf-/abgebaut. Für Batch mit vielen
    Mails könnte das ineffizient sein, ist aber robuster gegen Server-
    Drops zwischen Versanden.
    """

    def __init__(
        self,
        config: SmtpConfig,
        *,
        max_retries: int = 3,
        retry_backoff_seconds: float = 1.0,
        connect_timeout: float = 30.0,
    ):
        self.config = config
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self.connect_timeout = connect_timeout

    def name(self) -> str:
        return "smtp"

    def deliver(
        self,
        *,
        index: int,
        to_email: str,
        from_email: str,
        subject: str,
        body: str,
    ) -> DeliveryResult:
        """Sendet eine Mail. Bei Fehler: DeliveryResult.delivered=False, error befüllt."""
        eml_bytes = build_eml(
            to_email=to_email, from_email=from_email,
            subject=subject, body=body,
        )

        last_error: Optional[str] = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self._send_once(
                    from_email=from_email,
                    to_email=to_email,
                    eml_bytes=eml_bytes,
                )
                return DeliveryResult(
                    to_email=to_email,
                    subject=subject,
                    body=body,
                    eml_bytes=eml_bytes,
                    delivered=True,
                    smtp_response=response,
                    delivered_at=datetime.now(),
                    retry_count=attempt,
                )
            except _PERMANENT_ERRORS as e:
                # Permanente Fehler: kein Retry, sofort fail.
                last_error = f"PERMANENT {type(e).__name__}: {e}"
                break
            except _RETRYABLE_ERRORS as e:
                last_error = f"TRANSIENT {type(e).__name__}: {e}"
                if attempt < self.max_retries:
                    sleep_for = self.retry_backoff_seconds * (2 ** attempt)
                    time.sleep(sleep_for)
                    continue
                # Letzter Versuch erschöpft
                break
            except Exception as e:  # noqa: BLE001 — fallback für unbekannte SMTP-Fehler
                last_error = f"UNEXPECTED {type(e).__name__}: {e}"
                break

        return DeliveryResult(
            to_email=to_email,
            subject=subject,
            body=body,
            eml_bytes=eml_bytes,
            delivered=False,
            error=last_error,
            retry_count=self.max_retries,
        )

    def _send_once(
        self, *, from_email: str, to_email: str, eml_bytes: bytes
    ) -> str:
        """Ein einzelner SMTP-Versuch. Raises bei Fehler.

        Returns: SMTP-Server-Response (für Logging).
        """
        cfg = self.config
        with smtplib.SMTP(host=cfg.host, port=cfg.port, timeout=self.connect_timeout) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(cfg.user, cfg.token)
            # sendmail returns dict of {addr: (code, response)} for *failed* recipients
            # — empty dict = success.
            refused = smtp.sendmail(from_email, [to_email], eml_bytes)
            if refused:
                raise smtplib.SMTPRecipientsRefused(refused)
            # smtp.noop() liefert (code, msg) — letzte Response
            try:
                code, msg = smtp.noop()
                return f"SMTP {code}: {msg.decode('ascii', errors='replace')}"
            except Exception:
                return "SMTP 250 OK (no detail)"
