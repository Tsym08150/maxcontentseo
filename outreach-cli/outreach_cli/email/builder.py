"""EML-Builder für outreach-cli send.

Generiert RFC-5322-konforme MIME-Bytes. Subject wird RFC-2047
base64-MIME-encoded falls Non-ASCII enthalten (deutsche Umlaute im Subject).
Body als `text/plain; charset=utf-8` (Python email-stdlib wählt automatisch
zwischen 8bit / quoted-printable / base64).

**KEIN UTF-8-BOM mehr im Output** (Fix REVIEW-send CR-02, 2026-05-11):
- BOM vor MIME-Header bricht RFC-5322 (erstes Byte muss Header-Char sein).
- SMTP-Wire-Protocol: BOM würde Spam-Filter triggern, Gmail "Upload draft" rejected.
- Die ursprüngliche BOM-Policy galt für `.ps1`/`.md`-Files mit deutschen Umlauten,
  NICHT für MIME-Envelopes. .eml-Files sind MIME-Envelopes.

`from_email` und `to_email` werden validiert (`@` muss vorhanden sein, sonst
ValueError) — MEDIUM-04 Fix.

Achtung: Dieses Modul heißt `outreach_cli.email.builder`. `email.mime.text`
in den Imports referenziert die **Python-Standard-Library** (`email` package),
nicht dieses Subpaket — absolute imports sind in Python 3 default.
"""

from __future__ import annotations

from dataclasses import dataclass
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from pathlib import Path
import re


# UTF-8 BOM byte sequence — exportiert für Backward-Compat-Tests.
# NICHT mehr in build_eml-Output gepackt (CR-02 Fix).
UTF8_BOM = b"\xef\xbb\xbf"


class InvalidEmailError(ValueError):
    """Raised wenn from/to email keine @-Zeichen enthält."""


@dataclass(frozen=True)
class BuiltMail:
    to_email: str
    subject: str
    body: str
    eml_bytes: bytes
    path: Path | None = None


def _safe_filename(email: str) -> str:
    """Macht eine Email-Adresse Dateinamen-tauglich."""
    s = re.sub(r"[^a-zA-Z0-9._@-]", "_", email)
    s = s.replace("@", "_at_")
    return s


def _validate_email(addr: str, label: str) -> None:
    if "@" not in addr or not addr.split("@", 1)[-1]:
        raise InvalidEmailError(f"Invalid {label}: {addr!r} (no domain)")


def build_eml(
    *,
    to_email: str,
    from_email: str,
    subject: str,
    body: str,
) -> bytes:
    """Baut RFC-5322 MIME-Bytes.

    Subject wird automatisch MIME-encoded (RFC 2047) wenn Non-ASCII.
    Output ist direkt SMTP-fähig (kein BOM, keine extra Prefixe).
    """
    _validate_email(from_email, "from_email")
    _validate_email(to_email, "to_email")

    msg = MIMEText(body, _subtype="plain", _charset="utf-8")
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = str(Header(subject, charset="utf-8"))
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=from_email.split("@", 1)[-1])

    return msg.as_bytes()


def write_eml(
    *,
    out_dir: Path,
    index: int,
    to_email: str,
    from_email: str,
    subject: str,
    body: str,
) -> BuiltMail:
    """Schreibt .eml in out_dir und gibt BuiltMail mit path zurück.

    .eml-File ist identisch zu SMTP-Wire-Bytes (kein BOM-Prefix).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    eml_bytes = build_eml(
        to_email=to_email, from_email=from_email,
        subject=subject, body=body,
    )
    safe = _safe_filename(to_email)
    path = out_dir / f"{index:03d}_{safe}.eml"
    path.write_bytes(eml_bytes)
    return BuiltMail(
        to_email=to_email,
        subject=subject,
        body=body,
        eml_bytes=eml_bytes,
        path=path,
    )
