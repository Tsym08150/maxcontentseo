"""Tests: run_send setzt Recherche_Status auf 'Angeschrieben' nach erfolgreichem
SMTP-Delivery — verhindert Doppel-Versand beim nächsten Run mit --status Neu.

DryRun darf KEIN set_status triggern (kein echter Send).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

import pytest

from outreach_cli.commands.send import run_send
from outreach_cli.email.transport import DeliveryResult


class _RecordingSheetClient:
    """Mock-SheetClient — sammelt set_status-Calls."""
    def __init__(self, leads):
        from outreach_cli.leads.loader import FilteredLead
        self._leads = leads
        self.set_status_calls: list[tuple[str, str, str]] = []
        # SheetClient.config wird im run_send referenziert (für AGGREGATE_TABS etc.)
        from outreach_cli.config import Config
        # Echte Config nutzen ist OK — wir brauchen sie nur für tabs-Liste
        import os
        os.environ.setdefault("SHEET_ID", "x")
        os.environ.setdefault("GOOGLE_CREDENTIALS_PATH", "x")
        # Statt echtem Config: stub via object
        class _Cfg:
            primary_tabs = ("Frankfurt_Umland",)
            aggregate_tabs = ("Alle_Leads",)
            tabs = ("Frankfurt_Umland", "Alle_Leads")
        self.config = _Cfg()

    def set_status(self, *, email, status, when=None, column=None, force=False):
        self.set_status_calls.append((email, status, column or ""))
        # Minimaler SetStatusResult
        from outreach_cli.sheets import SetStatusResult
        return SetStatusResult(
            primary=None, secondary=None, column_written=column or "",
            warnings=[],
        )

    # Methoden die load_filtered_leads aufruft
    def iter_tab_rows(self, tab):
        return iter([])  # wir mocken via dependency injection unten


@dataclass
class _FakeLead:
    email: str
    firma: str = "Test"
    stadt: str = "TestStadt"
    score: str = "5"
    recherche_status: str = "Neu"
    render_vars: dict = None

    def __post_init__(self):
        if self.render_vars is None:
            self.render_vars = {
                "name": "Sehr geehrte/r Test",
                "firma": self.firma,
                "stadt": self.stadt,
                "beispiel_keyword": "Kosmetik TestStadt",
            }


class _RecordingTransport:
    """Mock-Transport — gibt immer Success zurück, name() == 'smtp' (Live-Send)."""
    def __init__(self, name="smtp"):
        self._name = name
        self.deliveries: list[str] = []

    def name(self) -> str:
        return self._name

    def deliver(self, *, index, to_email, from_email, subject, body):
        self.deliveries.append(to_email)
        from datetime import datetime
        return DeliveryResult(
            to_email=to_email, subject=subject, body=body, eml_bytes=b"",
            delivered=True,
            error=None, retry_count=0,
            smtp_response="250 OK", path=None,
            delivered_at=datetime.now(),
        )


def test_smtp_send_auto_sets_angeschrieben(monkeypatch):
    """Nach erfolgreichem SMTP-Send muss Recherche_Status = 'Angeschrieben' gesetzt sein."""
    leads = [_FakeLead(email="a@x.de"), _FakeLead(email="b@x.de")]

    sc = _RecordingSheetClient(leads)
    transport = _RecordingTransport(name="smtp")

    from outreach_cli.commands import send as send_mod

    def fake_load(client, *, tab, score_min, status, limit, exclude_hwg):
        from outreach_cli.leads.loader import FilterStats
        return list(leads), FilterStats(total_in_tab=2)

    def fake_template(name):
        # Minimaler Template-Stub — render kennt nur die Vars die wir geben
        class _Tpl:
            subject_tpl = "Test {{stadt}}"
            body_tpl = "Hallo {{name}}, Frage zu {{beispiel_keyword}}."
            frontmatter = {}
        return _Tpl()

    def fake_render(template, vars):
        return (f"Test {vars['stadt']}",
                f"Hallo {vars['name']}, Frage zu {vars['beispiel_keyword']}.")

    monkeypatch.setattr(send_mod, "load_filtered_leads", fake_load)
    monkeypatch.setattr(send_mod, "load_template", fake_template)
    monkeypatch.setattr(send_mod, "render", fake_render)

    result = run_send(
        tab="Frankfurt_Umland", template_name="variante_c", transport=transport,
        sheet_client=sc, rate_limit_seconds=0,
    )

    assert len(result.delivered) == 2
    # 2 set_status-Calls, einer pro erfolgreich gelieferter Mail
    assert len(sc.set_status_calls) == 2
    emails = [c[0] for c in sc.set_status_calls]
    assert "a@x.de" in emails
    assert "b@x.de" in emails
    # Alle als "Angeschrieben" gesetzt
    assert all(c[1] == "Angeschrieben" for c in sc.set_status_calls)
    # Spalte Recherche_Status
    assert all(c[2] == "Recherche_Status" for c in sc.set_status_calls)


def test_dry_run_does_not_set_status(monkeypatch):
    """DryRun darf KEIN set_status triggern — kein echter Send."""
    leads = [_FakeLead(email="a@x.de")]
    sc = _RecordingSheetClient(leads)
    transport = _RecordingTransport(name="dry-run")

    from outreach_cli.commands import send as send_mod
    monkeypatch.setattr(
        send_mod, "load_filtered_leads",
        lambda *a, **kw: (list(leads),
                          __import__("outreach_cli.leads.loader", fromlist=["FilterStats"]).FilterStats(total_in_tab=1)),
    )
    monkeypatch.setattr(send_mod, "load_template", lambda n: type("T", (), {})())
    monkeypatch.setattr(send_mod, "render", lambda t, v: ("S", "B"))

    result = run_send(
        tab="X", template_name="t", transport=transport,
        sheet_client=sc, rate_limit_seconds=0,
    )

    assert len(result.delivered) == 1
    assert sc.set_status_calls == []  # KEINE Status-Updates bei dry-run


def test_failed_delivery_no_status_update(monkeypatch):
    """Wenn Send fehlschlaegt, darf KEIN Status-Update passieren."""
    leads = [_FakeLead(email="fails@x.de")]
    sc = _RecordingSheetClient(leads)

    class _FailingTransport:
        def name(self): return "smtp"
        def deliver(self, *, index, to_email, from_email, subject, body):
            from datetime import datetime
            return DeliveryResult(
                to_email=to_email, subject=subject, body=body, eml_bytes=b"",
                delivered=False,
                error="smtp 550 user unknown", retry_count=3,
                smtp_response="", path=None, delivered_at=datetime.now(),
            )

    from outreach_cli.commands import send as send_mod
    monkeypatch.setattr(
        send_mod, "load_filtered_leads",
        lambda *a, **kw: (list(leads),
                          __import__("outreach_cli.leads.loader", fromlist=["FilterStats"]).FilterStats(total_in_tab=1)),
    )
    monkeypatch.setattr(send_mod, "load_template", lambda n: type("T", (), {})())
    monkeypatch.setattr(send_mod, "render", lambda t, v: ("S", "B"))

    result = run_send(
        tab="X", template_name="t", transport=_FailingTransport(),
        sheet_client=sc, rate_limit_seconds=0,
    )

    assert len(result.delivered) == 0
    assert len(result.failed) == 1
    assert sc.set_status_calls == []  # KEIN Status-Update bei Failure


def test_set_status_exception_is_non_fatal(monkeypatch):
    """Wenn set_status raised, läuft der Send-Loop weiter; Mail #1 bleibt delivered."""
    leads = [_FakeLead(email="ok@x.de"), _FakeLead(email="ok2@x.de")]

    class _BrokenSC(_RecordingSheetClient):
        def set_status(self, **kwargs):
            self.set_status_calls.append((kwargs["email"], kwargs["status"], kwargs.get("column", "")))
            raise RuntimeError("simulated sheet API rate limit")

    sc = _BrokenSC(leads)
    transport = _RecordingTransport(name="smtp")

    from outreach_cli.commands import send as send_mod
    monkeypatch.setattr(
        send_mod, "load_filtered_leads",
        lambda *a, **kw: (list(leads),
                          __import__("outreach_cli.leads.loader", fromlist=["FilterStats"]).FilterStats(total_in_tab=2)),
    )
    monkeypatch.setattr(send_mod, "load_template", lambda n: type("T", (), {})())
    monkeypatch.setattr(send_mod, "render", lambda t, v: ("S", "B"))

    result = run_send(
        tab="X", template_name="t", transport=transport,
        sheet_client=sc, rate_limit_seconds=0,
    )

    # Beide Mails wurden trotz Sync-Failure delivered
    assert len(result.delivered) == 2
    # Sync wurde versucht (2 calls), aber failed (sammelt in sync_failures)
    assert len(sc.set_status_calls) == 2
    assert len(result.sheet_sync_failures) == 2
    assert "ok@x.de" in [f[0] for f in result.sheet_sync_failures]
