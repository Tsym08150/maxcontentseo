"""Unit tests für die reine Logik in sheets.py — keine Netzwerk-Calls."""

from __future__ import annotations

from datetime import date

import pytest

from outreach_cli.config import (
    H_ANTWORT,
    H_FIRMA,
    H_FOLLOWUP,
    H_KONTAKTIERT,
    H_STADT,
)
from outreach_cli.sheets import (
    LeadRow,
    _col_letter,
    _date_column_for_status,
    _find_header,
    _normalize_row,
    _parse_date,
    _row_to_dict,
)


# ---- _col_letter ---------------------------------------------------------

def test_col_letter_basic():
    assert _col_letter(0) == "A"
    assert _col_letter(25) == "Z"


def test_col_letter_double_digit():
    assert _col_letter(26) == "AA"
    assert _col_letter(51) == "AZ"
    assert _col_letter(52) == "BA"


# ---- _find_header (mit Alias-Map) ---------------------------------------

def test_find_header_exact_case_insensitive():
    headers = ["FIRMA", "email", "Recherche_Status"]
    assert _find_header(headers, "EMAIL") == 1
    assert _find_header(headers, "recherche_status") == 2


def test_find_header_strips_whitespace():
    assert _find_header(["  FIRMA  ", "EMAIL"], "firma") == 0


def test_find_header_missing_returns_none():
    assert _find_header(["FIRMA", "EMAIL"], "STADTTEIL") is None


def test_find_header_alias_dot_for_firma():
    """Frankfurt-Alt-Schema: Spalte 1 hieß '.', soll als FIRMA matchen."""
    headers = [".", "STADT", "EMAIL"]
    assert _find_header(headers, H_FIRMA) == 0


def test_find_header_alias_stadt_lowercase():
    """Alle_Leads / Frankfurt_Umland: 'Stadt' (klein-s) soll als STADT matchen."""
    headers = ["Stadt", "FIRMA", "EMAIL"]
    assert _find_header(headers, H_STADT) == 0


def test_find_header_alias_kontaktiert_old():
    """Alt-Muenchen: 'KONTAKTIERT' (ohne _AM) soll als KONTAKTIERT_AM matchen."""
    headers = ["EMAIL", "KONTAKTIERT", "FOLLOW-UP"]
    assert _find_header(headers, H_KONTAKTIERT) == 1


def test_find_header_alias_followup_old():
    """Alt-Muenchen: 'FOLLOW-UP' (Bindestrich) soll als FOLLOWUP_AM matchen."""
    headers = ["EMAIL", "KONTAKTIERT", "FOLLOW-UP"]
    assert _find_header(headers, H_FOLLOWUP) == 2


def test_find_header_first_match_wins_when_duplicate():
    """Bei case-insensitiv identischen Headern gewinnt der erste in Reihenfolge.
    (Case-insensitive Spalten gibt's in Sheets nicht, das ist nur theoretisch.)"""
    headers = ["Stadt", "STADT"]
    assert _find_header(headers, H_STADT) == 0


# ---- _row_to_dict --------------------------------------------------------

def test_row_to_dict_exact_length():
    assert _row_to_dict(["A", "B"], ["x", "y"]) == {"A": "x", "B": "y"}


def test_row_to_dict_pads_short_rows():
    assert _row_to_dict(["A", "B", "C"], ["x"]) == {"A": "x", "B": "", "C": ""}


def test_row_to_dict_ignores_extra_cells():
    assert _row_to_dict(["A", "B"], ["x", "y", "z"]) == {"A": "x", "B": "y"}


# ---- _normalize_row (alias-aware) ---------------------------------------

def test_normalize_row_canonical_keys_pass_through():
    headers = ["FIRMA", "STADT", "EMAIL"]
    out = _normalize_row(headers, ["Test", "Frankfurt", "x@y.de"])
    assert out["FIRMA"] == "Test"
    assert out["STADT"] == "Frankfurt"


def test_normalize_row_alias_creates_canonical_key():
    """Sheet hat 'Stadt' (klein-s) — out-Dict soll ZUSÄTZLICH 'STADT' liefern."""
    headers = ["Stadt", "FIRMA"]
    out = _normalize_row(headers, ["Hamburg", "TestGmbH"])
    assert out["Stadt"] == "Hamburg"  # Original-Key erhalten
    assert out["STADT"] == "Hamburg"  # Canonical-Alias eingeführt


def test_normalize_row_old_muenchen_headers():
    """KONTAKTIERT → KONTAKTIERT_AM, FOLLOW-UP → FOLLOWUP_AM."""
    headers = ["EMAIL", "KONTAKTIERT", "FOLLOW-UP"]
    out = _normalize_row(headers, ["x@y.de", "01.05.2026", "08.05.2026"])
    assert out["KONTAKTIERT_AM"] == "01.05.2026"
    assert out["FOLLOWUP_AM"] == "08.05.2026"


# ---- _parse_date ---------------------------------------------------------

@pytest.mark.parametrize("raw, expected", [
    ("11.05.2026", date(2026, 5, 11)),
    ("2026-05-11", date(2026, 5, 11)),
    ("11/05/2026", date(2026, 5, 11)),
    ("  07.05.2026  ", date(2026, 5, 7)),
])
def test_parse_date_valid(raw, expected):
    assert _parse_date(raw) == expected


@pytest.mark.parametrize("raw", ["", "   ", "kaputt", "2026/05/11", "32.01.2026"])
def test_parse_date_invalid(raw):
    assert _parse_date(raw) is None


# ---- _date_column_for_status --------------------------------------------

@pytest.mark.parametrize("status, expected_header", [
    ("Geantwortet - kein Interesse", H_ANTWORT),
    ("Geantwortet - Interesse", H_ANTWORT),
    ("Bounce", H_ANTWORT),
    ("Angeschrieben", H_KONTAKTIERT),
    ("Follow-up gesendet", H_FOLLOWUP),
    ("Nicht kontaktiert", None),
])
def test_date_column_for_status(status, expected_header):
    assert _date_column_for_status(status) == expected_header


# ---- LeadRow properties --------------------------------------------------

def test_leadrow_property_strip():
    lead = LeadRow(
        tab="Frankfurt",
        row_index=42,
        data={
            "FIRMA": "  Test GmbH ",
            "EMAIL": " info@test.de\n",
            "Recherche_Status": "Angeschrieben",
            "Verkaufsstatus": "Geantwortet - Interesse",
        },
    )
    assert lead.firma == "Test GmbH"
    assert lead.email == "info@test.de"
    assert lead.recherche_status == "Angeschrieben"
    assert lead.verkaufsstatus == "Geantwortet - Interesse"
    assert lead.status == lead.recherche_status  # Backward-compat


def test_leadrow_missing_keys_return_empty_string():
    lead = LeadRow(tab="X", row_index=2, data={})
    assert lead.firma == ""
    assert lead.email == ""
    assert lead.recherche_status == ""
    assert lead.verkaufsstatus == ""


def test_leadrow_constructed_from_normalize_row_with_aliases():
    """Wenn LeadRow aus alias-headers normalisiert wurde, sind beide Keys da."""
    headers = ["Stadt", "FIRMA", "EMAIL", "KONTAKTIERT"]
    row = ["Hamburg", "X-GmbH", "a@b.de", "01.01.2026"]
    data = _normalize_row(headers, row)
    lead = LeadRow(tab="t", row_index=2, data=data)
    assert lead.stadt == "Hamburg"           # via STADT alias
    assert lead.kontaktiert_am == "01.01.2026"  # via KONTAKTIERT_AM alias
