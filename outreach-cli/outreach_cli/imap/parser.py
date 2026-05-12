"""Bounce-Message-Parser.

Eingang: RFC 822 raw bytes (typischerweise multipart/report mit:
  - text/plain Erklärung
  - message/delivery-status mit Final-Recipient
  - message/rfc822 attached der originalen Mail)

Ziel: Liste der `failed_recipients` (E-Mail-Adressen, die nicht zugestellt
werden konnten) plus optional `bounce_type` (permanent/transient/unknown).
"""

from __future__ import annotations

import email
import re
from dataclasses import dataclass, field
from email import policy
from email.message import Message
from typing import Optional


# E-Mail-Regex — robust für deutsche Standard-Adressen. Bewusst eng:
# - Keine Internationalized Domain Names (IDN) — selten in B2B-Outreach
# - Top-Level-Domain min 2 Buchstaben (kein .digit)
EMAIL_RE = re.compile(
    r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"
)

# Adressen die NIE als "gebouncter Recipient" gelten (Sender/Bridge-Server).
# Subdomain-Match wichtig: Proton's interne Message-ID-Hosts sind z.B.
# `mail-106111.protonmail.ch` oder `mailsubfra1001.protonmail.ch` — `@protonmail.ch`
# als Substring greift dort NICHT. Stattdessen Suffix-Match auf .domain.tld.
EXCLUDE_PATTERNS = (
    "mailer-daemon",
    "postmaster@",
    "noreply@",
    "no-reply@",
    "donotreply@",
)

# Domain-Suffixe die als "interne Mail-Infrastruktur" ausgeschlossen werden.
EXCLUDE_DOMAIN_SUFFIXES = (
    "protonmail.ch",
    "proton.me",
    "pm.me",
)

# Permanent-Bounce-Signale (5xx SMTP-Codes oder klare Subjects)
PERMA_PATTERNS = re.compile(
    r"(?:5\d\d\s|status:\s*5\.\d+\.\d+|undelivered|returned to sender|"
    r"user unknown|no such user|mailbox not found|address rejected|"
    r"recipient.*rejected|nicht zustellbar)",
    re.IGNORECASE,
)

# Transient-Bounce-Signale (4xx, Delayed)
TRANSIENT_PATTERNS = re.compile(
    r"(?:4\d\d\s|status:\s*4\.\d+\.\d+|delayed mail|still being retried|"
    r"temporarily deferred|verzögert)",
    re.IGNORECASE,
)


@dataclass
class BounceMessage:
    """Geparste Bounce-Mail."""
    uid: Optional[bytes] = None  # IMAP UID (für Debugging/Audit)
    subject: str = ""
    sender_label: str = ""  # z.B. "MAILER-DAEMON@proton.me"
    received_date: Optional[str] = None
    bounce_type: str = "unknown"  # permanent | transient | unknown
    failed_recipients: list[str] = field(default_factory=list)
    original_subject: Optional[str] = None  # Subject der ursprünglich gesendeten Mail
    raw_size: int = 0


def _own_address_filter(own_user: str) -> set[str]:
    """Adressen die nie als 'failed recipient' zählen (wir senden uns nicht selbst Bounces)."""
    own = own_user.lower().strip()
    return {own}


def _exclude_addr(addr: str, own_filter: set[str]) -> bool:
    a = addr.lower()
    if a in own_filter:
        return True
    if any(p in a for p in EXCLUDE_PATTERNS):
        return True
    # Domain-Suffix-Check: alles was auf einer Mail-Infrastruktur-Domain endet.
    # `a@b.c.protonmail.ch` matched genauso wie `x@protonmail.ch`.
    if "@" in a:
        domain = a.rsplit("@", 1)[1]
        if any(domain == suf or domain.endswith("." + suf) for suf in EXCLUDE_DOMAIN_SUFFIXES):
            return True
    return False


def _walk_text(msg: Message) -> str:
    """Sammle allen text/* Content (auch nested), inkl. attached message/rfc822-Header."""
    chunks: list[str] = []
    for part in msg.walk():
        ctype = part.get_content_type()
        if ctype.startswith("text/"):
            try:
                content = part.get_content()
                if isinstance(content, str):
                    chunks.append(content)
            except Exception:
                payload = part.get_payload(decode=True)
                if payload:
                    try:
                        chunks.append(payload.decode("utf-8", errors="replace"))
                    except Exception:
                        pass
        elif ctype in ("message/delivery-status", "message/rfc822"):
            # delivery-status enthält Final-Recipient: rfc822; foo@bar.de
            # message/rfc822 enthält die orig. Mail als sub-Message
            try:
                for sub in part.iter_parts():
                    chunks.append(str(sub))
            except Exception:
                # Fallback: serialize as-is
                try:
                    chunks.append(str(part.get_payload()))
                except Exception:
                    pass
    # Auch die Header-Section als Text mit aufnehmen — manche Bouncer schreiben
    # nur In-Reply-To/References + Subject mit der orig Adresse.
    for h in ("Subject", "X-Failed-Recipients", "X-Original-To", "Delivered-To"):
        v = msg.get(h)
        if v:
            chunks.append(f"{h}: {v}")
    return "\n".join(chunks)


def parse_bounce(
    raw: bytes,
    *,
    own_user: str = "georg@maxcontentseo.de",
    uid: Optional[bytes] = None,
) -> BounceMessage:
    """Parse eine Bounce-Mail aus RFC-822-Bytes.

    Strategie:
    1. Subject + Sender lesen
    2. Bounce-Type via Pattern-Match auf Subject + Body (perma / transient / unknown)
    3. Failed-Recipient-Extraktion in dieser Reihenfolge:
       a) "Final-Recipient:" Header (RFC 3464)
       b) "Original-Recipient:" Header
       c) "X-Failed-Recipients:" Header
       d) Subject ausgewertet (manche Server schreiben Adresse in Subject)
       e) Greedy-Regex auf body, filter Eigene/Sender/proton-internals
    4. Bei mehreren Kandidaten: dedupliziert + sortiert.
    """
    msg = email.message_from_bytes(raw, policy=policy.default)
    subject = (msg.get("Subject") or "").strip()
    sender_label = (msg.get("From") or "").strip()
    received_date = (msg.get("Date") or "").strip()

    text = _walk_text(msg)

    # Bounce-Type
    if PERMA_PATTERNS.search(subject) or PERMA_PATTERNS.search(text):
        bounce_type = "permanent"
    elif TRANSIENT_PATTERNS.search(subject) or TRANSIENT_PATTERNS.search(text):
        bounce_type = "transient"
    else:
        bounce_type = "unknown"

    # Original-Subject (kommt aus attached message/rfc822 oder "Subject of failed message")
    orig_subject = None
    m = re.search(
        r"(?:Subject of failed message|Original Subject|orig\. Subject|"
        r"Betreff(?:\s+der\s+ursprünglichen\s+Nachricht)?):\s*([^\r\n]+)",
        text, re.IGNORECASE,
    )
    if m:
        orig_subject = m.group(1).strip()
    if not orig_subject:
        # Im attached message/rfc822 ist auch wieder ein Subject:-Header
        for part in msg.walk():
            if part.get_content_type() == "message/rfc822":
                try:
                    for sub in part.iter_parts():
                        s = sub.get("Subject")
                        if s:
                            orig_subject = s.strip()
                            break
                except Exception:
                    pass
                if orig_subject:
                    break

    # Failed-Recipient-Extraktion
    own_filter = _own_address_filter(own_user)
    candidates: list[str] = []

    def _add_candidate(s: Optional[str]) -> None:
        if not s:
            return
        for match in EMAIL_RE.findall(s):
            if not _exclude_addr(match, own_filter):
                candidates.append(match.lower())

    # Header-basiert (zuverlässigste Quelle nach RFC 3464)
    for header_name in ("Final-Recipient", "Original-Recipient", "X-Failed-Recipients"):
        for part in msg.walk():
            v = part.get(header_name)
            _add_candidate(v)

    # Im delivery-status part nach "Final-Recipient: rfc822; <addr>" suchen
    for part in msg.walk():
        if part.get_content_type() == "message/delivery-status":
            try:
                body = part.get_payload()
                if isinstance(body, list):
                    for sub in body:
                        for header_name in ("Final-Recipient", "Original-Recipient"):
                            v = sub.get(header_name) if hasattr(sub, "get") else None
                            if v:
                                _add_candidate(str(v))
            except Exception:
                pass

    # Im body Subject + Original-Mail-To
    _add_candidate(subject)

    # Fallback: alle Adressen im Plain-Text, gefiltert
    if not candidates:
        _add_candidate(text)

    # Dedup + sort
    failed = sorted(set(candidates))

    return BounceMessage(
        uid=uid,
        subject=subject,
        sender_label=sender_label,
        received_date=received_date,
        bounce_type=bounce_type,
        failed_recipients=failed,
        original_subject=orig_subject,
        raw_size=len(raw),
    )
