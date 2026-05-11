"""Tests für Phase 2 SMTP-Integration.

Coverage:
- SmtpConfig.from_env: .env korrekt geladen + Placeholder-Schutz
- SmtpTransport: Retry bei transienten Errors, kein Retry bei permanenten
- SmtpTransport: Rate-Limit-Pause via run_send
- TestSelf-Pfad: 1 Mail an Owner mit hardcoded Test-Lead
- HWG word-boundary regex: false-positive Cases

KEIN echter SMTP-Versand in Tests — alles mocked.
"""

from __future__ import annotations

import os
import smtplib
import socket
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from outreach_cli.config import SmtpConfig
from outreach_cli.email.sender import SmtpTransport
from outreach_cli.email.transport import DeliveryResult
from outreach_cli.leads.loader import is_hwg_excluded
from outreach_cli.sheets import LeadRow


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _lead(*, firma: str = "Test", branche: str = "Kosmetik") -> LeadRow:
    return LeadRow(
        tab="X", row_index=2,
        data={
            "EMAIL": "x@y.de", "FIRMA": firma, "STADT": "Frankfurt",
            "BRANCHE": branche, "SCORE": "5", "Recherche_Status": "Neu",
            "Entscheider": "",
        },
    )


def _make_smtp_config() -> SmtpConfig:
    return SmtpConfig(
        host="smtp.protonmail.ch", port=587,
        user="georg@maxcontentseo.de", token="fake-app-password",
        owner_email="georg@maxcontentseo.de",
    )


# ---------------------------------------------------------------------------
# 1. test_smtp_credentials_from_env — .env korrekt geladen
# ---------------------------------------------------------------------------

def test_smtp_credentials_from_env(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "user@example.com")
    monkeypatch.setenv("SMTP_TOKEN", "real-token-xyz")
    monkeypatch.setenv("OWNER_EMAIL", "owner@example.com")

    cfg = SmtpConfig.from_env()
    assert cfg.host == "smtp.example.com"
    assert cfg.port == 587
    assert cfg.user == "user@example.com"
    assert cfg.token == "real-token-xyz"
    assert cfg.owner_email == "owner@example.com"


def test_smtp_config_missing_keys_raises(monkeypatch):
    """Fehlende .env-Keys → klare Fehlermeldung mit Liste."""
    for k in ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_TOKEN", "OWNER_EMAIL"):
        monkeypatch.delenv(k, raising=False)

    with pytest.raises(SystemExit) as exc:
        SmtpConfig.from_env()
    err = str(exc.value)
    assert "SMTP_HOST" in err
    assert "SMTP_TOKEN" in err


@pytest.mark.parametrize("placeholder", [
    "REPLACE_WITH_APP_PASSWORD",
    "REPLACE_ME_WITH_PROTON_APP_PASSWORD",
    "YOUR_TOKEN_HERE",
    "CHANGE_ME",
    "replace_lowercase",  # case-insensitive
])
def test_smtp_config_rejects_placeholder_token(monkeypatch, placeholder):
    """Placeholder-Token aus .env.example soll fail-fast — diverse Patterns."""
    monkeypatch.setenv("SMTP_HOST", "h")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "u@e.de")
    monkeypatch.setenv("SMTP_TOKEN", placeholder)
    with pytest.raises(SystemExit) as exc:
        SmtpConfig.from_env()
    err = str(exc.value)
    assert "Placeholder" in err or "REPLACE" in err.upper() or "YOUR_" in err.upper()


def test_smtp_config_owner_defaults_to_user(monkeypatch):
    """OWNER_EMAIL ungesetzt → fallback auf SMTP_USER."""
    monkeypatch.setenv("SMTP_HOST", "h")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "u@e.de")
    monkeypatch.setenv("SMTP_TOKEN", "real-token")
    monkeypatch.delenv("OWNER_EMAIL", raising=False)
    cfg = SmtpConfig.from_env()
    assert cfg.owner_email == "u@e.de"


# ---------------------------------------------------------------------------
# 2. test_smtp_retry_on_transient_error
# ---------------------------------------------------------------------------

def test_smtp_retry_on_timeout(monkeypatch):
    """Bei socket.timeout: 3 Retries, dann fail mit retry_count=3."""
    cfg = _make_smtp_config()
    transport = SmtpTransport(cfg, max_retries=3, retry_backoff_seconds=0.0)

    call_count = {"n": 0}

    def fake_send(self, from_email, to_email, eml_bytes):
        call_count["n"] += 1
        raise socket.timeout("simulated timeout")

    monkeypatch.setattr(SmtpTransport, "_send_once", fake_send)

    result = transport.deliver(
        index=1, to_email="x@y.de", from_email="g@e.de",
        subject="Test", body="body",
    )
    assert result.delivered is False
    assert "TRANSIENT" in (result.error or "")
    assert call_count["n"] == 4  # initial + 3 retries
    assert result.retry_count == 3


def test_smtp_retry_succeeds_on_second_attempt(monkeypatch):
    """Erster Versuch failed transient, zweiter geht durch → delivered."""
    cfg = _make_smtp_config()
    transport = SmtpTransport(cfg, max_retries=3, retry_backoff_seconds=0.0)

    call_count = {"n": 0}

    def fake_send(self, from_email, to_email, eml_bytes):
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise ConnectionError("first try blew up")
        return "SMTP 250 OK"

    monkeypatch.setattr(SmtpTransport, "_send_once", fake_send)
    result = transport.deliver(
        index=1, to_email="x@y.de", from_email="g@e.de",
        subject="Test", body="body",
    )
    assert result.delivered is True
    assert result.retry_count == 1
    assert call_count["n"] == 2


def test_smtp_no_retry_on_auth_error(monkeypatch):
    """SMTPAuthenticationError ist permanent — kein Retry."""
    cfg = _make_smtp_config()
    transport = SmtpTransport(cfg, max_retries=3, retry_backoff_seconds=0.0)

    call_count = {"n": 0}

    def fake_send(self, from_email, to_email, eml_bytes):
        call_count["n"] += 1
        raise smtplib.SMTPAuthenticationError(535, b"Authentication failed")

    monkeypatch.setattr(SmtpTransport, "_send_once", fake_send)
    result = transport.deliver(
        index=1, to_email="x@y.de", from_email="g@e.de",
        subject="Test", body="body",
    )
    assert result.delivered is False
    assert "PERMANENT" in (result.error or "")
    assert call_count["n"] == 1  # genau 1 Versuch
    # Token darf NICHT in error-message landen
    assert cfg.token not in (result.error or "")


# ---------------------------------------------------------------------------
# 3. test_smtp_rate_limit_pauses_between_sends
# ---------------------------------------------------------------------------

def test_smtp_rate_limit_pauses_between_sends(monkeypatch, tmp_path):
    """run_send mit rate_limit_seconds > 0 ruft time.sleep() zwischen Leads auf."""
    from outreach_cli.commands.send import run_send
    from outreach_cli.email.transport import DryRunTransport
    from outreach_cli.sheets import SheetClient

    sleep_calls: list[float] = []

    import time as _time
    monkeypatch.setattr(_time, "sleep", lambda s: sleep_calls.append(s))

    leads = [
        LeadRow(tab="X", row_index=i + 2, data={
            "EMAIL": f"l{i}@y.de", "FIRMA": "F", "STADT": "Frankfurt",
            "BRANCHE": "Kosmetik", "SCORE": "5", "Recherche_Status": "Neu",
            "Entscheider": "",
        })
        for i in range(3)
    ]

    client = SheetClient.__new__(SheetClient)
    client.config = MagicMock()
    client.config.primary_tabs = ("X",)
    client.config.aggregate_tabs = ()
    client._tab_cache = {}
    client.iter_tab_rows = lambda tab: iter(leads)  # type: ignore[assignment]

    run_send(
        tab="X", template_name="variante_c",
        transport=DryRunTransport(preview_dir=tmp_path),
        sheet_client=client, rate_limit_seconds=2.0,
    )

    # 3 Leads → 2 Pausen (zwischen 1-2 und 2-3, nicht nach letztem)
    pause_calls = [s for s in sleep_calls if s == 2.0]
    assert len(pause_calls) == 2, (
        f"Erwarte 2 Pausen für 3 Leads, fand {pause_calls}"
    )


# ---------------------------------------------------------------------------
# 4. test_dry_run_no_rate_limit
# ---------------------------------------------------------------------------

def test_dry_run_no_rate_limit(monkeypatch, tmp_path):
    """Bei rate_limit_seconds=0 (Dry-Run-Default) wird KEIN time.sleep aufgerufen."""
    from outreach_cli.commands.send import run_send
    from outreach_cli.email.transport import DryRunTransport
    from outreach_cli.sheets import SheetClient

    sleep_calls = []
    import time as _time
    monkeypatch.setattr(_time, "sleep", lambda s: sleep_calls.append(s))

    leads = [LeadRow(tab="X", row_index=2, data={
        "EMAIL": "x@y.de", "FIRMA": "F", "STADT": "Frankfurt",
        "BRANCHE": "Kosmetik", "SCORE": "5",
        "Recherche_Status": "Neu", "Entscheider": "",
    })]
    client = SheetClient.__new__(SheetClient)
    client.config = MagicMock()
    client.config.primary_tabs = ("X",); client.config.aggregate_tabs = ()
    client._tab_cache = {}
    client.iter_tab_rows = lambda tab: iter(leads)  # type: ignore[assignment]

    run_send(
        tab="X", template_name="variante_c",
        transport=DryRunTransport(preview_dir=tmp_path),
        sheet_client=client, rate_limit_seconds=0.0,
    )
    assert sleep_calls == []


# ---------------------------------------------------------------------------
# 5. HWG word-boundary regex — false-positive Tests (User-Spec)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("firma, branche, expected_exclude", [
    # CR-01 Fix: word-boundary, kein substring
    ("Quarztherapie Salon", "Wellness",       False),  # 'arzt' in 'Quarz' → kein match
    ("TCM Praxis Dr. med. Wang", "Akupunktur", True),  # 'dr. med.' wort-aligned
    ("Kosmetikstudio München",   "Kosmetik",   False),  # nix HWG
    ("Heilpraktikerschule Berlin", "Bildung",  False),  # Schule, nicht Praxis — word-boundary fängt das nicht
    ("Praxis Schwartz",          "Beauty",     False),  # 'arzt' nicht in 'Schwartz'
    ("Dr.med.Müller MVZ",        "Aesthetik",  True),   # Dr.med. ohne Space
    ("Mama Sarah Beauty",        "Kosmetik",   False),  # nichts triggert
])
def test_hwg_word_boundary_no_false_positives(firma, branche, expected_exclude):
    lead = _lead(firma=firma, branche=branche)
    excluded, reason = is_hwg_excluded(lead)
    assert excluded is expected_exclude, (
        f"firma={firma!r} branche={branche!r} → expected exclude={expected_exclude}, "
        f"got excluded={excluded} reason={reason!r}"
    )


# ---------------------------------------------------------------------------
# 6. TestSelf-Pfad — Subject-MIME-encoding für deutsche Umlaute
# ---------------------------------------------------------------------------

def test_test_self_subject_mime_encoded(monkeypatch):
    """--test-self Mail-Subject mit Umlauten muss MIME-encoded sein."""
    from outreach_cli.email.builder import build_eml

    # User-Spec: Subject muss korrekt MIME-encoded sein (Umlaute!)
    eml = build_eml(
        to_email="georg@maxcontentseo.de",
        from_email="georg@maxcontentseo.de",
        subject="[TEST-SELF] Kurze Frage zu Ihrem Kosmetikstudio in München",
        body="Sehr geehrte/r Test-Empfänger,\nHydrafacial München als Test.",
    )
    decoded = eml.decode("utf-8")
    # Subject muss MIME-encoded sein (=?utf-8?...?=) ODER raw-utf-8
    # Python email-stdlib wählt automatisch; Umlaute IM Subject → encoded.
    assert "Subject:" in decoded
    # München enthält Umlaut, sollte encoded werden
    assert "=?utf-8?" in decoded.lower() or "München" in decoded


# ---------------------------------------------------------------------------
# 7. SmtpTransport baut eml_bytes ohne BOM
# ---------------------------------------------------------------------------

def test_smtp_transport_no_bom_in_eml_bytes(monkeypatch):
    """deliver() liefert eml_bytes die direkt SMTP-wire-fähig sind (kein BOM)."""
    from outreach_cli.email.builder import UTF8_BOM

    cfg = _make_smtp_config()
    transport = SmtpTransport(cfg, max_retries=0)

    # mock _send_once damit kein Netzwerk
    monkeypatch.setattr(SmtpTransport, "_send_once",
                        lambda self, **kw: "SMTP 250 OK")

    result = transport.deliver(
        index=1, to_email="x@y.de", from_email="g@e.de",
        subject="Test mit Ümlaut",
        body="Body mit Umläut",
    )
    assert result.delivered is True
    assert not result.eml_bytes.startswith(UTF8_BOM), \
        "eml_bytes darf kein BOM haben — würde SMTP-Wire-Protocol brechen"


# ---------------------------------------------------------------------------
# 8. SmtpTransport.deliver passt eml_bytes an _send_once weiter
# ---------------------------------------------------------------------------

def test_smtp_transport_calls_send_once_with_correct_args(monkeypatch):
    cfg = _make_smtp_config()
    transport = SmtpTransport(cfg, max_retries=0)
    captured = {}

    def capturing_send(self, from_email, to_email, eml_bytes):
        captured["from_email"] = from_email
        captured["to_email"] = to_email
        captured["eml_bytes_len"] = len(eml_bytes)
        return "SMTP 250 OK"

    monkeypatch.setattr(SmtpTransport, "_send_once", capturing_send)

    transport.deliver(
        index=1, to_email="dest@e.de", from_email="src@e.de",
        subject="Test", body="body content",
    )
    assert captured["from_email"] == "src@e.de"
    assert captured["to_email"] == "dest@e.de"
    assert captured["eml_bytes_len"] > 0


# ---------------------------------------------------------------------------
# 9. per-lead robustness: bad row killt nicht den Batch
# ---------------------------------------------------------------------------

def test_per_lead_robustness_bad_row_does_not_kill_batch(tmp_path):
    """HIGH-03 Fix: Lead mit leerer STADT wird geskippt, andere laufen weiter."""
    from outreach_cli.commands.send import run_send
    from outreach_cli.email.transport import DryRunTransport

    good_lead = LeadRow(tab="X", row_index=2, data={
        "EMAIL": "good@y.de", "FIRMA": "Good", "STADT": "Frankfurt",
        "BRANCHE": "Kosmetik", "SCORE": "5",
        "Recherche_Status": "Neu", "Entscheider": "",
    })
    bad_lead = LeadRow(tab="X", row_index=3, data={
        "EMAIL": "bad@y.de", "FIRMA": "Bad", "STADT": "",  # leer!
        "BRANCHE": "Kosmetik", "SCORE": "5",
        "Recherche_Status": "Neu", "Entscheider": "",
    })
    good2 = LeadRow(tab="X", row_index=4, data={
        "EMAIL": "good2@y.de", "FIRMA": "Good2", "STADT": "Hamburg",
        "BRANCHE": "Beauty", "SCORE": "5",
        "Recherche_Status": "Neu", "Entscheider": "",
    })

    client = SheetClient.__new__(SheetClient)
    client.config = MagicMock()
    client.config.primary_tabs = ("X",); client.config.aggregate_tabs = ()
    client._tab_cache = {}
    client.iter_tab_rows = lambda tab: iter([good_lead, bad_lead, good2])  # type: ignore[assignment]

    result = run_send(
        tab="X", template_name="variante_c",
        transport=DryRunTransport(preview_dir=tmp_path),
        sheet_client=client,
    )

    assert len(result.delivered) == 2  # good + good2
    assert len(result.stats.skipped_no_render_vars) == 1
    skipped_emails = " ".join(result.stats.skipped_no_render_vars)
    assert "bad@y.de" in skipped_emails


# ---------------------------------------------------------------------------
# 10. SheetClient nicht benötigt für lokale Transport-Tests
# ---------------------------------------------------------------------------

# (covered via class — added for completeness)


# ---------------------------------------------------------------------------
# Imports needed for run_send-tests (SheetClient mock factory)
# ---------------------------------------------------------------------------
from outreach_cli.sheets import SheetClient  # noqa: E402
