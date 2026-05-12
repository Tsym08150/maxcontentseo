"""EmailVerifyCache Unit-Tests — TTL, dedupe, atomic write, corruption-handling."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from outreach_cli.verifier.cache import (
    EmailVerifyCache,
    DEFAULT_TTL_DAYS,
)


def test_empty_cache_returns_none(tmp_path: Path):
    c = EmailVerifyCache(tmp_path / "v.json")
    assert c.get("foo@bar.de") is None
    assert c.size() == 0


def test_put_and_get_roundtrip(tmp_path: Path):
    c = EmailVerifyCache(tmp_path / "v.json")
    c.put("Foo@BAR.de", status="valid", sub_status="alias_address")
    e = c.get("foo@bar.de")
    assert e is not None
    assert e.email == "foo@bar.de"
    assert e.status == "valid"
    assert e.sub_status == "alias_address"


def test_case_insensitive_lookup(tmp_path: Path):
    c = EmailVerifyCache(tmp_path / "v.json")
    c.put("Test@Example.DE", status="valid")
    assert c.get("TEST@example.de") is not None
    assert c.get("test@example.de") is not None


def test_ttl_expires_after_30_days(tmp_path: Path):
    c = EmailVerifyCache(tmp_path / "v.json", ttl_days=30)
    old = datetime.now(timezone.utc) - timedelta(days=31)
    c.put("old@example.de", status="valid", verified_at=old)
    assert c.get("old@example.de") is None  # expired


def test_ttl_still_fresh_before_30_days(tmp_path: Path):
    c = EmailVerifyCache(tmp_path / "v.json", ttl_days=30)
    recent = datetime.now(timezone.utc) - timedelta(days=29)
    c.put("recent@example.de", status="valid", verified_at=recent)
    assert c.get("recent@example.de") is not None


def test_save_and_reload(tmp_path: Path):
    p = tmp_path / "v.json"
    c1 = EmailVerifyCache(p)
    c1.put("a@example.de", status="valid")
    c1.put("b@example.de", status="invalid", sub_status="mailbox_not_found")
    c1.save()

    # Fresh instance, same file
    c2 = EmailVerifyCache(p)
    assert c2.get("a@example.de").status == "valid"
    assert c2.get("b@example.de").status == "invalid"
    assert c2.get("b@example.de").sub_status == "mailbox_not_found"


def test_corrupt_json_silently_ignored(tmp_path: Path):
    p = tmp_path / "v.json"
    p.write_text("{ this is not JSON", encoding="utf-8")
    c = EmailVerifyCache(p)
    assert c.get("anything@example.de") is None
    # Should still work (write succeeds)
    c.put("new@example.de", status="valid")
    c.save()
    # File should now be valid JSON
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["schema"] == 1
    assert "new@example.de" in data["entries"]


def test_stats_returns_status_counts(tmp_path: Path):
    c = EmailVerifyCache(tmp_path / "v.json")
    c.put("a@x.de", status="valid")
    c.put("b@x.de", status="valid")
    c.put("c@x.de", status="invalid")
    c.put("d@x.de", status="catch-all")
    s = c.stats()
    assert s["valid"] == 2
    assert s["invalid"] == 1
    assert s["catch-all"] == 1


def test_atomic_write_doesnt_leave_temp_files(tmp_path: Path):
    p = tmp_path / "v.json"
    c = EmailVerifyCache(p)
    c.put("a@x.de", status="valid")
    c.save()
    # Nur die Ziel-Datei darf existieren — keine .tmp-Reste
    files = list(tmp_path.iterdir())
    assert len(files) == 1
    assert files[0].name == "v.json"
