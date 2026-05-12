"""Tests: rate_limit_seconds > 0 triggert randomisierten Delay 8-25 s."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

import pytest

from outreach_cli.commands.send import run_send
from outreach_cli.email.transport import DeliveryResult


class _StubSheetClient:
    """Minimal Sheet-Stub — set_status no-op."""
    def __init__(self):
        class _Cfg:
            primary_tabs = ("X",)
            aggregate_tabs = ()
            tabs = ("X",)
        self.config = _Cfg()

    def set_status(self, **kwargs):
        from outreach_cli.sheets import SetStatusResult
        return SetStatusResult(primary=None, secondary=None, column_written="", warnings=[])


class _RecTransport:
    def __init__(self):
        self.delivered = []
    def name(self): return "smtp"
    def deliver(self, *, index, to_email, from_email, subject, body):
        self.delivered.append(to_email)
        return DeliveryResult(
            to_email=to_email, subject=subject, body=body, eml_bytes=b"",
            delivered=True, error=None, retry_count=0,
            smtp_response="250 OK", path=None, delivered_at=datetime.now(),
        )


def _patch_loader(monkeypatch, leads):
    from outreach_cli.commands import send as send_mod
    from outreach_cli.leads.loader import FilterStats
    monkeypatch.setattr(
        send_mod, "load_filtered_leads",
        lambda *a, **kw: (list(leads), FilterStats(total_in_tab=len(leads))),
    )
    monkeypatch.setattr(send_mod, "load_template", lambda n: type("T", (), {})())
    monkeypatch.setattr(send_mod, "render", lambda t, v: ("S", "B"))


def _make_lead(email):
    """Lead mit minimaler render_vars-Struktur."""
    class _L:
        def __init__(self, email):
            self.email = email
            self.render_vars = {"name": "X", "firma": "Y", "stadt": "Z", "beispiel_keyword": "K"}
    return _L(email)


def test_rate_limit_zero_no_sleep(monkeypatch):
    """rate_limit_seconds == 0 → keine sleep-Calls."""
    from outreach_cli.commands import send as send_mod
    sleep_calls = []
    monkeypatch.setattr("time.sleep", lambda s: sleep_calls.append(s))

    leads = [_make_lead(f"a{i}@x.de") for i in range(3)]
    _patch_loader(monkeypatch, leads)

    run_send(
        tab="X", template_name="t", transport=_RecTransport(),
        sheet_client=_StubSheetClient(), rate_limit_seconds=0,
    )
    assert sleep_calls == []  # gar keine sleeps


def test_rate_limit_positive_triggers_random_delay(monkeypatch):
    """rate_limit_seconds > 0 → random.randint(8, 25) für jeden Inter-Mail-Gap."""
    sleep_calls: list[float] = []
    randint_calls: list[tuple[int, int]] = []

    # Patch random.randint und time.sleep im send-Modul-Namespace
    from outreach_cli.commands import send as send_mod
    import random as _random_orig
    import time as _time_orig

    real_randint = _random_orig.randint
    def fake_randint(a, b):
        randint_calls.append((a, b))
        return 12  # deterministischer Wert für Assertion
    monkeypatch.setattr(_random_orig, "randint", fake_randint)
    monkeypatch.setattr(_time_orig, "sleep", lambda s: sleep_calls.append(s))

    leads = [_make_lead(f"a{i}@x.de") for i in range(3)]
    _patch_loader(monkeypatch, leads)

    run_send(
        tab="X", template_name="t", transport=_RecTransport(),
        sheet_client=_StubSheetClient(), rate_limit_seconds=1.0,  # any > 0
    )

    # 3 Mails → 2 Inter-Gap-Pausen (zwischen #1↔#2 und #2↔#3, nicht nach der letzten)
    assert len(sleep_calls) == 2
    assert all(s == 12 for s in sleep_calls)
    # random.randint wurde mit den richtigen Bounds aufgerufen
    assert randint_calls == [(8, 25), (8, 25)]


def test_rate_limit_value_is_ignored_only_used_as_on_off(monkeypatch):
    """Wert von rate_limit_seconds > 0 ist egal — Range ist immer 8-25."""
    randint_calls: list[tuple[int, int]] = []
    import random as _random_orig
    import time as _time_orig
    monkeypatch.setattr(_random_orig, "randint", lambda a, b: randint_calls.append((a, b)) or 10)
    monkeypatch.setattr(_time_orig, "sleep", lambda s: None)

    leads = [_make_lead("a@x.de"), _make_lead("b@x.de")]
    _patch_loader(monkeypatch, leads)

    # Wir testen verschiedene Werte — alle müssen (8, 25) auslösen
    for value in (1.0, 2.0, 100.0, 0.5):
        randint_calls.clear()
        run_send(
            tab="X", template_name="t", transport=_RecTransport(),
            sheet_client=_StubSheetClient(), rate_limit_seconds=value,
        )
        assert randint_calls == [(8, 25)], f"rate_limit_seconds={value} → unexpected {randint_calls}"


def test_dry_run_with_positive_rate_still_skips_delay_when_zero(monkeypatch):
    """Nur 1 Lead → keine inter-mail-pause, egal welcher rate_limit_seconds."""
    sleep_calls: list[float] = []
    import time as _time_orig
    monkeypatch.setattr(_time_orig, "sleep", lambda s: sleep_calls.append(s))

    leads = [_make_lead("only@x.de")]
    _patch_loader(monkeypatch, leads)

    run_send(
        tab="X", template_name="t", transport=_RecTransport(),
        sheet_client=_StubSheetClient(), rate_limit_seconds=5.0,
    )
    # 1 Mail → 0 Inter-Gap-Pausen
    assert sleep_calls == []
