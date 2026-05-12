"""Pipeline-Tests mit Mock-Client — kein echter ZeroBounce-API-Call."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pytest

from outreach_cli.verifier.cache import EmailVerifyCache
from outreach_cli.verifier.pipeline import (
    BatchVerifyResult,
    VerificationBucket,
    verify_batch,
)
from outreach_cli.verifier.zerobounce import (
    VerifyResponse,
    ZeroBounceClient,
    ZeroBounceError,
    ZeroBounceQuotaError,
)


class MockClient:
    """Mock-ZeroBounceClient — gibt vorgefertigte Status-Werte zurück.

    responses-Werte können sein:
      - str (status) → sub_status=""
      - tuple[str, str] (status, sub_status)
      - Exception → wird beim Aufruf geworfen
    """
    def __init__(self, responses):
        self.responses = responses
        self.calls: list[str] = []

    def validate(self, email: str, *, ip_address: str = "") -> VerifyResponse:
        self.calls.append(email)
        v = self.responses[email]
        if isinstance(v, Exception):
            raise v
        if isinstance(v, tuple):
            status, sub_status = v
        else:
            status, sub_status = v, ""
        return VerifyResponse(
            address=email, status=status, sub_status=sub_status,
            free_email=False, mx_found=True, did_you_mean="",
            raw={"status": status, "sub_status": sub_status},
        )

    def get_credits(self) -> int:
        return 99


def test_bucketing_status_to_bucket(tmp_path: Path):
    client = MockClient({
        "a@x.de": "valid",
        "b@x.de": "catch-all",
        "c@x.de": "invalid",
        "d@x.de": "unknown",
        "e@x.de": "spamtrap",
        "f@x.de": "abuse",
        "g@x.de": "do_not_mail",
    })
    cache = EmailVerifyCache(tmp_path / "v.json")
    r = verify_batch(client.responses.keys(), client=client, cache=cache)

    assert r.api_calls_made == 7
    assert r.cache_hits == 0

    by = {d.email: d.bucket for d in r.decisions}
    assert by["a@x.de"] == VerificationBucket.SEND
    assert by["b@x.de"] == VerificationBucket.SEND_WITH_WARN
    assert by["c@x.de"] == VerificationBucket.SKIP
    assert by["d@x.de"] == VerificationBucket.SKIP
    assert by["e@x.de"] == VerificationBucket.SKIP
    assert by["f@x.de"] == VerificationBucket.SKIP
    assert by["g@x.de"] == VerificationBucket.SKIP


def test_cache_hit_skips_api_call(tmp_path: Path):
    cache = EmailVerifyCache(tmp_path / "v.json")
    cache.put("cached@x.de", status="valid")

    client = MockClient({"new@x.de": "invalid"})
    r = verify_batch(["cached@x.de", "new@x.de"], client=client, cache=cache)

    # Nur 1 API-Call (für new@x.de), cached@x.de aus Cache
    assert r.api_calls_made == 1
    assert r.cache_hits == 1
    assert client.calls == ["new@x.de"]


def test_quota_abort_marks_remaining_as_quota(tmp_path: Path):
    client = MockClient({
        "first@x.de": "valid",
        "boom@x.de": ZeroBounceQuotaError("quota voll"),
        "third@x.de": "valid",  # darf nicht mehr abgefragt werden
    })
    cache = EmailVerifyCache(tmp_path / "v.json")
    r = verify_batch(["first@x.de", "boom@x.de", "third@x.de"], client=client, cache=cache)

    assert r.quota_aborted_at == "boom@x.de"
    by = {d.email: d.bucket for d in r.decisions}
    assert by["first@x.de"] == VerificationBucket.SEND
    assert by["boom@x.de"] == VerificationBucket.QUOTA_ABORT
    assert by["third@x.de"] == VerificationBucket.QUOTA_ABORT
    # third@ darf NICHT API-aufgerufen worden sein
    assert "third@x.de" not in client.calls


def test_api_error_continues_with_next(tmp_path: Path):
    """Generischer API-Fehler bricht NICHT den ganzen Batch ab."""
    client = MockClient({
        "ok@x.de": "valid",
        "err@x.de": ZeroBounceError("HTTP 500 oder so"),
        "ok2@x.de": "invalid",
    })
    cache = EmailVerifyCache(tmp_path / "v.json")
    r = verify_batch(["ok@x.de", "err@x.de", "ok2@x.de"], client=client, cache=cache)

    by = {d.email: d.bucket for d in r.decisions}
    assert by["ok@x.de"] == VerificationBucket.SEND
    assert by["err@x.de"] == VerificationBucket.ERROR
    assert by["ok2@x.de"] == VerificationBucket.SKIP


def test_dedupe_same_email_twice(tmp_path: Path):
    """Duplikate in der Input-Liste verursachen nur 1 API-Call."""
    client = MockClient({"a@x.de": "valid"})
    cache = EmailVerifyCache(tmp_path / "v.json")
    r = verify_batch(["a@x.de", "a@x.de", "A@X.DE"], client=client, cache=cache)
    assert r.api_calls_made == 1
    assert len(r.decisions) == 1


def test_sendable_emails_excludes_skip(tmp_path: Path):
    client = MockClient({
        "valid@x.de": "valid",
        "catch@x.de": "catch-all",
        "bad@x.de": "invalid",
    })
    cache = EmailVerifyCache(tmp_path / "v.json")
    r = verify_batch(client.responses.keys(), client=client, cache=cache)
    sendable = set(r.sendable_emails)
    assert "valid@x.de" in sendable
    assert "catch@x.de" in sendable
    assert "bad@x.de" not in sendable


def test_empty_input_returns_empty(tmp_path: Path):
    cache = EmailVerifyCache(tmp_path / "v.json")
    r = verify_batch([], client=None, cache=cache)
    assert r.decisions == []
    assert r.api_calls_made == 0
    assert r.cache_hits == 0


def test_whitespace_email_ignored(tmp_path: Path):
    client = MockClient({"real@x.de": "valid"})
    cache = EmailVerifyCache(tmp_path / "v.json")
    r = verify_batch(["", "  ", "real@x.de"], client=client, cache=cache)
    assert len(r.decisions) == 1
    assert r.decisions[0].email == "real@x.de"


def test_do_not_mail_with_role_based_is_relaxed_to_send_with_warn(tmp_path: Path):
    """B2B-Outreach-Relaxation: do_not_mail+role_based → SEND_WITH_WARN.

    Echte Suppressions (do_not_mail+disposable/toxic/global_suppression) bleiben SKIP.
    """
    client = MockClient({
        "info@studio-a.de": ("do_not_mail", "role_based"),
        "kontakt@studio-b.de": ("do_not_mail", "role_based_catch_all"),
        "user@studio-c.de": ("do_not_mail", "disposable"),         # echte Suppression
        "blocked@studio-d.de": ("do_not_mail", "global_suppression"),
        "test@studio-e.de": ("do_not_mail", "toxic"),
        "naked@studio-f.de": ("do_not_mail", ""),                  # ohne sub → bleibt SKIP
    })
    cache = EmailVerifyCache(tmp_path / "v.json")
    r = verify_batch(client.responses.keys(), client=client, cache=cache)

    by = {d.email: d.bucket for d in r.decisions}
    assert by["info@studio-a.de"] == VerificationBucket.SEND_WITH_WARN
    assert by["kontakt@studio-b.de"] == VerificationBucket.SEND_WITH_WARN
    assert by["user@studio-c.de"] == VerificationBucket.SKIP        # disposable
    assert by["blocked@studio-d.de"] == VerificationBucket.SKIP     # global_suppression
    assert by["test@studio-e.de"] == VerificationBucket.SKIP        # toxic
    assert by["naked@studio-f.de"] == VerificationBucket.SKIP       # kein sub → konservativ


def test_role_based_with_valid_status_stays_send(tmp_path: Path):
    """`role_based` darf bei status=valid den SEND-Bucket nicht runterstufen."""
    client = MockClient({
        "info@x.de": ("valid", "role_based"),
        "kontakt@y.de": ("valid", "alias_address"),
    })
    cache = EmailVerifyCache(tmp_path / "v.json")
    r = verify_batch(client.responses.keys(), client=client, cache=cache)
    by = {d.email: d.bucket for d in r.decisions}
    assert by["info@x.de"] == VerificationBucket.SEND
    assert by["kontakt@y.de"] == VerificationBucket.SEND


def test_cache_hit_respects_relaxation_too(tmp_path: Path):
    """Wenn ein gecachter Eintrag do_not_mail+role_based ist, kommt SEND_WITH_WARN raus."""
    cache = EmailVerifyCache(tmp_path / "v.json")
    cache.put(
        "info@cached.de",
        status="do_not_mail",
        sub_status="role_based",
    )
    r = verify_batch(["info@cached.de"], client=None, cache=cache)
    assert len(r.decisions) == 1
    assert r.decisions[0].bucket == VerificationBucket.SEND_WITH_WARN
    assert r.decisions[0].source == "cache"


def test_cache_persists_only_when_api_called(tmp_path: Path):
    """save() läuft nur wenn api_calls_made > 0 — sonst kein I/O nötig."""
    cache_path = tmp_path / "v.json"
    cache = EmailVerifyCache(cache_path)
    cache.put("cached@x.de", status="valid")
    # save() noch nicht aufgerufen — Datei existiert nicht
    assert not cache_path.exists()

    # Pure cache-hit, kein API-Call
    r = verify_batch(["cached@x.de"], client=None, cache=cache)
    assert r.cache_hits == 1
    assert r.api_calls_made == 0
    # save() wurde NICHT automatisch aufgerufen
    assert not cache_path.exists()
