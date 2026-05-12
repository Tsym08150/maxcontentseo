"""NeverBounce-Client + Provider-Selection Tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional
from unittest.mock import patch, MagicMock

import pytest

from outreach_cli.verifier.cache import EmailVerifyCache
from outreach_cli.verifier.neverbounce import (
    NeverBounceClient,
    NeverBounceConfig,
    NeverBounceError,
    NeverBounceQuotaError,
    VerifyResponse as NBResponse,
)
from outreach_cli.verifier.pipeline import (
    VerificationBucket,
    _select_provider_client,
    verify_batch,
)


# ---------------------------------------------------------------------------
# NeverBounceClient.validate — Response-Parsing
# ---------------------------------------------------------------------------

def _mock_urlopen(payload_dict, status_code=200):
    """Erzeugt ein MagicMock das urlopen-Response simuliert."""
    m = MagicMock()
    m.read.return_value = json.dumps(payload_dict).encode("utf-8")
    m.__enter__ = lambda s: m
    m.__exit__ = lambda *a: None
    return m


@patch("outreach_cli.verifier.neverbounce.urllib.request.urlopen")
def test_nb_validate_valid_status(mock_urlopen):
    mock_urlopen.return_value = _mock_urlopen({
        "status": "success", "result": "valid",
        "flags": ["has_dns"], "execution_time": 100,
    })
    cli = NeverBounceClient(NeverBounceConfig(api_key="testkey"))
    resp = cli.validate("test@example.de")
    assert resp.status == "valid"
    assert resp.address == "test@example.de"
    assert resp.mx_found is True


@patch("outreach_cli.verifier.neverbounce.urllib.request.urlopen")
def test_nb_validate_role_account_flag_yields_role_based_sub(mock_urlopen):
    """NB 'role_account'-Flag wird auf sub_status='role_based' gemappt
    (für Konsistenz mit ZB-Bucketing/Relaxation-Logik)."""
    mock_urlopen.return_value = _mock_urlopen({
        "status": "success", "result": "valid",
        "flags": ["has_dns", "role_account"],
    })
    cli = NeverBounceClient(NeverBounceConfig(api_key="k"))
    resp = cli.validate("info@studio.de")
    assert resp.status == "valid"
    assert resp.sub_status == "role_based"


@patch("outreach_cli.verifier.neverbounce.urllib.request.urlopen")
def test_nb_validate_catchall(mock_urlopen):
    mock_urlopen.return_value = _mock_urlopen({
        "status": "success", "result": "catchall",
    })
    cli = NeverBounceClient(NeverBounceConfig(api_key="k"))
    resp = cli.validate("any@catchall-domain.de")
    assert resp.status == "catchall"  # NB-Form, kein Hyphen


@patch("outreach_cli.verifier.neverbounce.urllib.request.urlopen")
def test_nb_validate_disposable(mock_urlopen):
    """NB 'disposable' ist Top-Level Result-Status (bei ZB ist es sub_status)."""
    mock_urlopen.return_value = _mock_urlopen({
        "status": "success", "result": "disposable",
        "flags": ["disposable"],
    })
    cli = NeverBounceClient(NeverBounceConfig(api_key="k"))
    resp = cli.validate("temp@mailinator.com")
    assert resp.status == "disposable"
    assert resp.sub_status == "disposable"


@patch("outreach_cli.verifier.neverbounce.urllib.request.urlopen")
def test_nb_auth_failure_raises_quota_error(mock_urlopen):
    mock_urlopen.return_value = _mock_urlopen({
        "status": "auth_failure", "message": "invalid_api_key",
    })
    cli = NeverBounceClient(NeverBounceConfig(api_key="badkey"))
    with pytest.raises(NeverBounceQuotaError):
        cli.validate("x@y.de")


@patch("outreach_cli.verifier.neverbounce.urllib.request.urlopen")
def test_nb_http_402_raises_quota_error(mock_urlopen):
    """HTTP 402 (Payment Required) = Free-Quota voll."""
    from urllib.error import HTTPError
    mock_urlopen.side_effect = HTTPError(
        "url", 402, "Payment Required", {}, None
    )
    cli = NeverBounceClient(NeverBounceConfig(api_key="k"))
    with pytest.raises(NeverBounceQuotaError):
        cli.validate("x@y.de")


@patch("outreach_cli.verifier.neverbounce.urllib.request.urlopen")
def test_nb_http_500_raises_generic_error(mock_urlopen):
    from urllib.error import HTTPError
    mock_urlopen.side_effect = HTTPError("url", 500, "Server Error", {}, None)
    cli = NeverBounceClient(NeverBounceConfig(api_key="k"))
    with pytest.raises(NeverBounceError):
        cli.validate("x@y.de")


# ---------------------------------------------------------------------------
# Provider-Selection in pipeline.py
# ---------------------------------------------------------------------------

def test_provider_selection_picks_neverbounce_when_set(monkeypatch):
    monkeypatch.setenv("NEVERBOUNCE_API_KEY", "real-nb-key")
    monkeypatch.setenv("ZEROBOUNCE_API_KEY", "real-zb-key")
    client = _select_provider_client()
    assert client.__class__.__name__ == "NeverBounceClient"


def test_provider_selection_falls_back_to_zerobounce(monkeypatch):
    monkeypatch.delenv("NEVERBOUNCE_API_KEY", raising=False)
    monkeypatch.setenv("ZEROBOUNCE_API_KEY", "real-zb-key")
    client = _select_provider_client()
    assert client.__class__.__name__ == "ZeroBounceClient"


def test_provider_selection_skips_placeholder_keys(monkeypatch):
    """Placeholder-Werte (REPLACE_, YOUR_) gelten als nicht-konfiguriert."""
    monkeypatch.setenv("NEVERBOUNCE_API_KEY", "REPLACE_ME_WITH_NB_KEY")
    monkeypatch.setenv("ZEROBOUNCE_API_KEY", "real-zb-key")
    client = _select_provider_client()
    # NB ist Placeholder → fällt auf ZB durch
    assert client.__class__.__name__ == "ZeroBounceClient"


def test_provider_selection_raises_when_neither_configured(monkeypatch):
    monkeypatch.delenv("NEVERBOUNCE_API_KEY", raising=False)
    monkeypatch.delenv("ZEROBOUNCE_API_KEY", raising=False)
    with pytest.raises(SystemExit):
        _select_provider_client()


# ---------------------------------------------------------------------------
# pipeline.verify_batch mit NB-Responses
# ---------------------------------------------------------------------------

class _NBMockClient:
    """MockClient für NB-style status values."""
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def validate(self, email, *, ip_address=""):
        self.calls.append(email)
        v = self.responses[email]
        if isinstance(v, Exception):
            raise v
        if isinstance(v, tuple):
            status, sub_status = v
        else:
            status, sub_status = v, ""
        return NBResponse(
            address=email, status=status, sub_status=sub_status,
            free_email=False, mx_found=True, did_you_mean="",
            raw={"result": status},
        )


def test_pipeline_nb_catchall_to_send_with_warn(tmp_path: Path):
    """NB 'catchall' (ohne Hyphen) → SEND_WITH_WARN-Bucket."""
    client = _NBMockClient({"info@x.de": "catchall"})
    cache = EmailVerifyCache(tmp_path / "v.json")
    r = verify_batch(["info@x.de"], client=client, cache=cache)
    assert r.decisions[0].bucket == VerificationBucket.SEND_WITH_WARN


def test_pipeline_nb_disposable_top_level_skip(tmp_path: Path):
    """NB 'disposable' als Top-Level-Status → SKIP (bei ZB war es sub_status)."""
    client = _NBMockClient({"temp@mailinator.com": "disposable"})
    cache = EmailVerifyCache(tmp_path / "v.json")
    r = verify_batch(["temp@mailinator.com"], client=client, cache=cache)
    assert r.decisions[0].bucket == VerificationBucket.SKIP


def test_pipeline_nb_quota_error_aborts_remaining(tmp_path: Path):
    """NeverBounceQuotaError → restliche Adressen als QUOTA_ABORT."""
    client = _NBMockClient({
        "first@x.de": "valid",
        "boom@x.de": NeverBounceQuotaError("quota voll"),
        "third@x.de": "valid",
    })
    cache = EmailVerifyCache(tmp_path / "v.json")
    r = verify_batch(["first@x.de", "boom@x.de", "third@x.de"],
                     client=client, cache=cache)
    by = {d.email: d.bucket for d in r.decisions}
    assert by["first@x.de"] == VerificationBucket.SEND
    assert by["boom@x.de"] == VerificationBucket.QUOTA_ABORT
    assert by["third@x.de"] == VerificationBucket.QUOTA_ABORT
    assert "third@x.de" not in client.calls


def test_pipeline_nb_valid_with_role_based_stays_send(tmp_path: Path):
    """Auch bei NB-Pfad: valid + role_based bleibt SEND (nicht runter)."""
    client = _NBMockClient({"info@x.de": ("valid", "role_based")})
    cache = EmailVerifyCache(tmp_path / "v.json")
    r = verify_batch(["info@x.de"], client=client, cache=cache)
    assert r.decisions[0].bucket == VerificationBucket.SEND


# ---------------------------------------------------------------------------
# Bucket-Map Coverage
# ---------------------------------------------------------------------------

def test_bucket_map_accepts_both_catchall_forms():
    """ZB 'catch-all' und NB 'catchall' mappen beide auf SEND_WITH_WARN."""
    from outreach_cli.verifier.pipeline import _bucket_for_status
    assert _bucket_for_status("catch-all") == VerificationBucket.SEND_WITH_WARN
    assert _bucket_for_status("catchall") == VerificationBucket.SEND_WITH_WARN


def test_bucket_map_disposable_top_level_skip():
    """NB 'disposable' (Top-Level) → SKIP."""
    from outreach_cli.verifier.pipeline import _bucket_for_status
    assert _bucket_for_status("disposable") == VerificationBucket.SKIP
