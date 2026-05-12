"""Bounce-Parser Unit-Tests — synthetische RFC-822-Bounces."""

from __future__ import annotations

import textwrap

import pytest

from outreach_cli.imap.parser import parse_bounce


def _make_bounce(*, subject: str, body: str, content_type: str = "text/plain; charset=utf-8") -> bytes:
    """Minimaler RFC-822-Wrapper für Test-Body."""
    return (
        f"From: MAILER-DAEMON <mailer-daemon@proton.me>\r\n"
        f"To: georg@maxcontentseo.de\r\n"
        f"Subject: {subject}\r\n"
        f"Date: Mon, 12 May 2026 10:00:00 +0000\r\n"
        f"Content-Type: {content_type}\r\n"
        f"MIME-Version: 1.0\r\n"
        f"\r\n"
        f"{body}"
    ).encode("utf-8")


def test_parse_perma_bounce_with_final_recipient_in_body():
    body = textwrap.dedent("""\
        This is the mail system at host mail.example.com.

        Your message could not be delivered to one or more recipients.

        Failed recipient: lead@kaputtshop.de
        SMTP status: 550 5.1.1 No such user

        ---
        Original message attached.
        """)
    raw = _make_bounce(subject="Undelivered Mail Returned to Sender", body=body)
    b = parse_bounce(raw, own_user="georg@maxcontentseo.de")
    assert b.bounce_type == "permanent"
    assert "lead@kaputtshop.de" in b.failed_recipients
    assert "georg@maxcontentseo.de" not in b.failed_recipients


def test_parse_transient_bounce():
    body = textwrap.dedent("""\
        This message is automatically generated. The message you sent is being
        delayed and still being retried.

        Recipient: slow-mail@kunde.de
        Status: 4.4.2 Connection timed out
        """)
    raw = _make_bounce(subject="Delayed Mail (still being retried)", body=body)
    b = parse_bounce(raw, own_user="georg@maxcontentseo.de")
    assert b.bounce_type == "transient"
    assert "slow-mail@kunde.de" in b.failed_recipients


def test_parse_excludes_own_address_and_proton_internals():
    body = textwrap.dedent("""\
        Original sender: georg@maxcontentseo.de
        Internal-Id: <4g8K0742mszMqTqC@mail-106111.protonmail.ch>
        Final-Recipient: rfc822; echterlead@firma.de
        Failed: mailer-daemon@proton.me
        Status: 5.1.1
        """)
    raw = _make_bounce(subject="Undelivered", body=body)
    b = parse_bounce(raw, own_user="georg@maxcontentseo.de")
    assert b.failed_recipients == ["echterlead@firma.de"]
    # Eigene + Proton-Internals nicht enthalten
    assert "georg@maxcontentseo.de" not in b.failed_recipients
    assert not any("protonmail.ch" in r for r in b.failed_recipients)
    assert not any("proton.me" in r for r in b.failed_recipients)


def test_parse_bounce_extracts_original_subject():
    body = textwrap.dedent("""\
        Your message could not be delivered.

        Subject of failed message: Kurze Frage zu Ihrem Studio in München
        Failed: empfaenger@nicht-existent.de
        Status: 550
        """)
    raw = _make_bounce(subject="Mail Delivery Failed", body=body)
    b = parse_bounce(raw, own_user="georg@maxcontentseo.de")
    assert b.original_subject is not None
    assert "Studio in München" in b.original_subject


def test_parse_unknown_bounce_type_when_no_pattern_matches():
    body = "Generic mail server complaint. recipient@example.de"
    raw = _make_bounce(subject="Mail returned", body=body)
    b = parse_bounce(raw, own_user="georg@maxcontentseo.de")
    assert b.bounce_type == "unknown"
    # Trotz unknown-type wird der Recipient extrahiert (Greedy-Fallback)
    assert "recipient@example.de" in b.failed_recipients


def test_parse_empty_bounce_no_crash():
    raw = _make_bounce(subject="(empty)", body="")
    b = parse_bounce(raw, own_user="georg@maxcontentseo.de")
    assert b.failed_recipients == []
    assert b.bounce_type == "unknown"
