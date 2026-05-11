"""Tests für die Mutation-Pfade in sheets.py — speziell die Review-Fixes:

- CR-02: partial_failure handling
- CR-03: no destructive LETZTE_ANTWORT_AM → KONTAKTIERT_AM fallback
- HI-02: APIError wrapping als SheetsAPIError
- LO-05: Idempotency-skip
- CR-01-related: _lead_value header-aware lookup

Mock-Strategie: kein echter SheetClient. Wir testen die Hilfsfunktionen direkt
plus einen Fake-Client der nur das nötige für _write_status_for_lead und
set_status anbietet.
"""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

import gspread.exceptions
import pytest

from outreach_cli.config import (
    H_ANTWORT,
    H_KONTAKTIERT,
    H_RECHERCHE_STATUS,
    H_VERKAUFSSTATUS,
)
from outreach_cli.sheets import (
    LeadRow,
    SetStatusResult,
    SheetClient,
    SheetsAPIError,
    WriteAttempt,
    _lead_value,
    _normalize_row,
)


# --- _lead_value (CR-01-related) ----------------------------------------

def test_lead_value_exact_key():
    lead = LeadRow(tab="t", row_index=2, data={"Verkaufsstatus": "Bounce"})
    assert _lead_value(lead, "Verkaufsstatus") == "Bounce"


def test_lead_value_case_insensitive_fallback():
    """Wenn canonical-Key nicht da, aber case-insensitiv-Variante schon."""
    lead = LeadRow(tab="t", row_index=2, data={"verkaufsstatus": "Bounce"})
    assert _lead_value(lead, "Verkaufsstatus") == "Bounce"


def test_lead_value_missing_returns_empty():
    lead = LeadRow(tab="t", row_index=2, data={"FIRMA": "Test"})
    assert _lead_value(lead, "Verkaufsstatus") == ""


def test_lead_value_strips_whitespace():
    lead = LeadRow(tab="t", row_index=2, data={"Verkaufsstatus": "  Bounce  "})
    assert _lead_value(lead, "Verkaufsstatus") == "Bounce"


# --- WriteAttempt / SetStatusResult (CR-02 logic) -----------------------

def _attempt(success: bool, skipped: bool = False, error: str | None = None) -> WriteAttempt:
    return WriteAttempt(
        tab="t", row_index=2, success=success,
        skipped_idempotent=skipped, error=error,
    )


def test_setstatusresult_all_succeeded():
    r = SetStatusResult(
        primary=None, secondary=None, column_written="x",
        attempts=[_attempt(True), _attempt(True)],
    )
    assert r.writes_succeeded == 2
    assert r.writes_failed == 0
    assert not r.partial_failure
    assert not r.total_failure


def test_setstatusresult_partial_failure():
    """Ein write OK, einer FAIL = inkonsistente Tabs."""
    r = SetStatusResult(
        primary=None, secondary=None, column_written="x",
        attempts=[_attempt(True), _attempt(False, error="quota")],
    )
    assert r.writes_succeeded == 1
    assert r.writes_failed == 1
    assert r.partial_failure is True
    assert r.total_failure is False


def test_setstatusresult_total_failure():
    """Alle Writes FAIL → total_failure."""
    r = SetStatusResult(
        primary=None, secondary=None, column_written="x",
        attempts=[_attempt(False, error="x"), _attempt(False, error="y")],
    )
    assert r.writes_succeeded == 0
    assert r.writes_failed == 2
    assert r.total_failure is True
    assert r.partial_failure is False


def test_setstatusresult_idempotent_skips_not_counted_as_writes():
    """Skips zählen nicht als writes_succeeded — sind aber auch keine failures."""
    r = SetStatusResult(
        primary=None, secondary=None, column_written="x",
        attempts=[_attempt(True, skipped=True), _attempt(True, skipped=True)],
    )
    assert r.writes_succeeded == 0
    assert r.writes_skipped == 2
    assert r.writes_failed == 0
    assert not r.partial_failure
    assert not r.total_failure


# --- _write_status_for_lead via Fake-Client ----------------------------

class _FakeWorksheet:
    def __init__(self, throw_on_batch: bool = False):
        self.batches: list[list[dict]] = []
        self.throw = throw_on_batch

    def batch_update(self, updates, **kw):
        if self.throw:
            raise gspread.exceptions.APIError(MagicMock())
        self.batches.append(updates)


class _FakeSpreadsheet:
    def __init__(self, worksheets: dict[str, _FakeWorksheet]):
        self._ws = worksheets

    def worksheet(self, name):
        return self._ws[name]


def _make_client_with(
    headers: list[str],
    data: list[list[str]],
    tab: str = "Hamburg",
    throw_on_batch: bool = False,
) -> SheetClient:
    """Baut einen SheetClient ohne echte Auth — nur für Mutation-Tests."""
    client = SheetClient.__new__(SheetClient)
    client.config = MagicMock()
    client.config.primary_tabs = (tab,)
    client.config.aggregate_tabs = ()
    fake_ws = _FakeWorksheet(throw_on_batch=throw_on_batch)
    client._sh = _FakeSpreadsheet({tab: fake_ws})
    client._tab_cache = {tab: (headers, data)}
    client._fake_ws = fake_ws  # for test inspection
    return client


def _lead(tab: str, headers: list[str], row: list[str], row_index: int = 2) -> LeadRow:
    return LeadRow(tab=tab, row_index=row_index, data=_normalize_row(headers, row))


# --- CR-03: No destructive fallback when LETZTE_ANTWORT_AM missing ----

def test_write_letzte_antwort_am_missing_does_not_clobber_kontaktiert():
    """Wenn LETZTE_ANTWORT_AM-Spalte fehlt: KONTAKTIERT_AM darf NICHT
    überschrieben werden. Status wird trotzdem geschrieben."""
    headers = ["EMAIL", "Verkaufsstatus", "KONTAKTIERT_AM"]  # ohne LETZTE_ANTWORT_AM
    row = ["x@y.de", "", "01.05.2026"]  # original outreach date
    client = _make_client_with(headers, [row])
    lead = _lead("Hamburg", headers, row)

    attempt = client._write_status_for_lead(
        lead, status="Geantwortet - kein Interesse",
        status_column=H_VERKAUFSSTATUS,
        when=date(2026, 5, 11),
    )

    assert attempt.success is True
    # Es darf NUR der Status geschrieben werden, nicht das Datum
    assert len(client._fake_ws.batches) == 1
    written = client._fake_ws.batches[0]
    assert len(written) == 1, f"Expected only status write, got {written}"
    # Range muss Verkaufsstatus-Spalte sein (B2), nicht KONTAKTIERT_AM (C2)
    assert written[0]["range"] == "B2"
    assert written[0]["values"] == [["Geantwortet - kein Interesse"]]
    # Keine date_column_written
    assert attempt.date_column_written is None


# --- LO-05: Idempotency ------------------------------------------------

def test_write_idempotency_skips_when_status_and_date_match():
    """Status bereits 'Bounce' und LETZTE_ANTWORT_AM bereits = target_date →
    kein write, attempt.skipped_idempotent=True."""
    headers = ["EMAIL", "Verkaufsstatus", "LETZTE_ANTWORT_AM"]
    row = ["x@y.de", "Bounce", "11.05.2026"]
    client = _make_client_with(headers, [row])
    lead = _lead("Hamburg", headers, row)

    attempt = client._write_status_for_lead(
        lead, status="Bounce",
        status_column=H_VERKAUFSSTATUS,
        when=date(2026, 5, 11),
    )

    assert attempt.success is True
    assert attempt.skipped_idempotent is True
    assert client._fake_ws.batches == [], "Kein Write erwartet"


def test_write_idempotency_writes_when_status_matches_but_date_differs():
    """Nur Status ist bereits korrekt, Datum nicht → write läuft."""
    headers = ["EMAIL", "Verkaufsstatus", "LETZTE_ANTWORT_AM"]
    row = ["x@y.de", "Bounce", "01.05.2026"]
    client = _make_client_with(headers, [row])
    lead = _lead("Hamburg", headers, row)

    attempt = client._write_status_for_lead(
        lead, status="Bounce",
        status_column=H_VERKAUFSSTATUS,
        when=date(2026, 5, 11),
    )

    assert attempt.success is True
    assert attempt.skipped_idempotent is False
    assert len(client._fake_ws.batches) == 1


def test_write_idempotency_force_overrides_skip():
    """force=True schreibt auch wenn alles bereits passt."""
    headers = ["EMAIL", "Verkaufsstatus", "LETZTE_ANTWORT_AM"]
    row = ["x@y.de", "Bounce", "11.05.2026"]
    client = _make_client_with(headers, [row])
    lead = _lead("Hamburg", headers, row)

    attempt = client._write_status_for_lead(
        lead, status="Bounce",
        status_column=H_VERKAUFSSTATUS,
        when=date(2026, 5, 11),
        force=True,
    )

    assert attempt.success is True
    assert attempt.skipped_idempotent is False
    assert len(client._fake_ws.batches) == 1


def test_write_no_date_when_status_not_a_date_status():
    """Status 'Nicht kontaktiert' hat keine Datumsspalte — nur Status-write."""
    headers = ["EMAIL", "Verkaufsstatus", "LETZTE_ANTWORT_AM"]
    row = ["x@y.de", "Angeschrieben", ""]
    client = _make_client_with(headers, [row])
    lead = _lead("Hamburg", headers, row)

    attempt = client._write_status_for_lead(
        lead, status="Nicht kontaktiert",
        status_column=H_VERKAUFSSTATUS,
        when=date(2026, 5, 11),
    )

    assert attempt.success is True
    assert len(client._fake_ws.batches) == 1
    assert len(client._fake_ws.batches[0]) == 1  # nur status
    assert attempt.date_column_written is None


# --- CR-02: APIError während batch_update wird in attempt.error gepackt -

def test_write_apierror_becomes_failed_attempt_not_exception():
    headers = ["EMAIL", "Verkaufsstatus", "LETZTE_ANTWORT_AM"]
    row = ["x@y.de", "", ""]
    client = _make_client_with(headers, [row], throw_on_batch=True)
    lead = _lead("Hamburg", headers, row)

    # Sollte KEINE Exception werfen — error landet in WriteAttempt
    attempt = client._write_status_for_lead(
        lead, status="Bounce",
        status_column=H_VERKAUFSSTATUS,
        when=date(2026, 5, 11),
    )

    assert attempt.success is False
    assert attempt.error is not None
    assert "batch_update failed" in attempt.error or "gspread error" in attempt.error


# --- Missing status column ---------------------------------------------

def test_write_idempotency_format_tolerant():
    """N-04: Idempotency check compares parsed dates, not strings.
    Sheet hat '2026-05-11' (ISO), wir generieren '11.05.2026' — sollte als
    gleich erkannt werden."""
    headers = ["EMAIL", "Verkaufsstatus", "LETZTE_ANTWORT_AM"]
    row = ["x@y.de", "Bounce", "2026-05-11"]  # ISO im Sheet
    client = _make_client_with(headers, [row])
    lead = _lead("Hamburg", headers, row)

    attempt = client._write_status_for_lead(
        lead, status="Bounce",
        status_column=H_VERKAUFSSTATUS,
        when=date(2026, 5, 11),  # generiert '11.05.2026'
    )

    assert attempt.success is True
    assert attempt.skipped_idempotent is True, \
        "ISO und DE-Format vom selben Datum müssen als gleich erkannt werden"
    assert client._fake_ws.batches == []


# --- HI-02: find_by_email APIError wrapping --------------------------------

def test_find_by_email_apierror_wraps_with_tab_context():
    """N-01: Test-Coverage für HI-02 — gspread.APIError aus iter_tab_rows
    soll als SheetsAPIError mit Tab-Name geworfen werden."""
    headers = ["EMAIL", "FIRMA"]
    row = ["other@example.com", "Other GmbH"]
    client = _make_client_with(headers, [row], tab="Hamburg")

    # Trigger APIError beim Lesen, indem wir _load_tab throwen lassen
    def throwing_load(_tab):
        raise gspread.exceptions.APIError(MagicMock())

    client._load_tab = throwing_load

    with pytest.raises(SheetsAPIError) as exc_info:
        client.find_by_email("x@y.de", tabs=["Hamburg"])
    assert "Hamburg" in str(exc_info.value)


def test_find_by_email_worksheet_not_found_is_skipped_silently():
    """WorksheetNotFound bleibt skip-silent, kein SheetsAPIError."""
    client = _make_client_with(["EMAIL"], [["a@b.de"]], tab="Hamburg")

    def missing_load(_tab):
        raise gspread.exceptions.WorksheetNotFound("Doesnt exist")

    client._load_tab = missing_load

    # Sollte None zurückgeben, KEINE Exception
    result = client.find_by_email("x@y.de", tabs=["Hamburg"])
    assert result is None


def test_write_missing_status_column_returns_failed_attempt():
    headers = ["EMAIL", "FIRMA"]  # weder Verkaufsstatus noch Recherche_Status
    row = ["x@y.de", "Test GmbH"]
    client = _make_client_with(headers, [row])
    lead = _lead("Hamburg", headers, row)

    attempt = client._write_status_for_lead(
        lead, status="Bounce",
        status_column=H_VERKAUFSSTATUS,
        when=None,
    )

    assert attempt.success is False
    assert "fehlt" in (attempt.error or "")
    assert client._fake_ws.batches == []
