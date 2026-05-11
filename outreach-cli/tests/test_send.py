"""Tests für outreach-cli send (Phase 1 — Dry-Run).

13 Tests gemäß User-Spec 2026-05-11. Vor SMTP-Integration grün.
"""

from __future__ import annotations

import smtplib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from outreach_cli.commands.send import run_send
from outreach_cli.email.builder import UTF8_BOM, build_eml, write_eml
from outreach_cli.leads.loader import (
    FilterStats,
    derive_render_vars,
    is_hwg_excluded,
    load_filtered_leads,
)
from outreach_cli.sheets import LeadRow, SheetClient
from outreach_cli.templates.engine import (
    MissingTemplateVariableError,
    Template,
    TemplateParseError,
    load_template,
    parse_template,
    render,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _lead(
    *, tab: str = "Frankfurt_Umland",
    row_index: int = 2,
    email: str = "info@kosmetikstudio-test.de",
    firma: str = "Test Kosmetikstudio",
    stadt: str = "Bad Homburg",
    branche: str = "Kosmetik / Anti-Aging",
    score: str = "5",
    rs: str = "Neu",
    entscheider: str = "Frau Müller",
) -> LeadRow:
    return LeadRow(
        tab=tab, row_index=row_index,
        data={
            "EMAIL": email, "FIRMA": firma, "STADT": stadt,
            "BRANCHE": branche, "SCORE": score,
            "Recherche_Status": rs,
            "Entscheider": entscheider,
        },
    )


def _fake_client_with(*leads: LeadRow) -> SheetClient:
    """SheetClient ohne echte Auth — iter_tab_rows() liefert übergebene Leads."""
    client = SheetClient.__new__(SheetClient)
    client.config = MagicMock()
    client.config.primary_tabs = ("Frankfurt_Umland",)
    client.config.aggregate_tabs = ()
    client._tab_cache = {}

    def fake_iter(tab):
        return iter(leads)

    client.iter_tab_rows = fake_iter  # type: ignore[assignment]
    return client


# ---------------------------------------------------------------------------
# 1. test_template_render_basic
# ---------------------------------------------------------------------------

def test_template_render_basic():
    """Alle Placeholders {stadt}, {name}, {beispiel_keyword} korrekt substituiert."""
    tpl = Template(
        name="t", subject_tpl="Test in {stadt}",
        body_tpl="Hallo {name}, {beispiel_keyword}!",
        metadata={},
    )
    subject, body = render(tpl, {
        "stadt": "Bad Homburg", "name": "Frau Müller",
        "beispiel_keyword": "Kosmetik Bad Homburg",
        "firma": "Test GmbH",
    })
    assert subject == "Test in Bad Homburg"
    assert body == "Hallo Frau Müller, Kosmetik Bad Homburg!"


# ---------------------------------------------------------------------------
# 2. test_template_missing_var_fails
# ---------------------------------------------------------------------------

def test_template_missing_var_fails():
    """KeyError-Subklasse bei fehlender Variable — fail-fast, kein silent empty."""
    tpl = Template(
        name="t", subject_tpl="Hi {missing_var}", body_tpl="x",
        metadata={},
    )
    with pytest.raises(MissingTemplateVariableError) as exc:
        render(tpl, {"stadt": "Bad Homburg"})
    assert "missing_var" in str(exc.value)


# ---------------------------------------------------------------------------
# 3. test_template_unicode_umlaute
# ---------------------------------------------------------------------------

def test_template_unicode_umlaute():
    """Deutsche Umlaute & Sonderzeichen werden korrekt durchgereicht
    (Bad-Homburg-Hieroglyphen-Bug-Regression)."""
    # Triple-quoted body lässt typographische Quotes („ “) und em-dash drinnen
    body_tpl = (
        "Sehr geehrte/r {name},\n"
        "„{beispiel_keyword}“ — größtenteils ungenutzt."
    )
    tpl = Template(
        name="t",
        subject_tpl="Kurze Frage zu Ihrem Kosmetikstudio in {stadt} (für Sie)",
        body_tpl=body_tpl,
        metadata={},
    )
    subject, body = render(tpl, {
        "stadt": "Königstein im Taunus",
        "name": "Frau Müller-Schöner",
        "beispiel_keyword": "Schönheitsklinik Königstein",
        "firma": "X",
    })
    # Umlaute erhalten
    assert "Königstein" in subject
    assert "Müller-Schöner" in body
    assert "Schönheitsklinik" in body
    # Sonderzeichen erhalten (typographische Quotes + em-dash)
    assert "„" in body  # „
    assert "“" in body  # "
    assert "—" in body  # —
    assert "größtenteils" in body


# ---------------------------------------------------------------------------
# 4. test_dry_run_creates_eml
# ---------------------------------------------------------------------------

def test_dry_run_creates_eml(tmp_path):
    """Pro filtered Lead landet eine .eml in preview/."""
    from outreach_cli.email.transport import DryRunTransport

    lead = _lead()
    client = _fake_client_with(lead)

    result = run_send(
        tab="Frankfurt_Umland", template_name="variante_c",
        transport=DryRunTransport(preview_dir=tmp_path),
        sheet_client=client,
    )
    assert len(result.delivered) == 1
    eml_path = result.delivered[0].path
    assert eml_path is not None
    assert eml_path.exists()
    content = eml_path.read_bytes()
    # CR-02 Fix: KEIN BOM mehr — .eml ist direkt SMTP-wire-fähig
    assert not content.startswith(UTF8_BOM), (
        "BOM darf nicht im .eml stehen — würde SMTP-Wire-Protocol brechen"
    )
    # Erstes Byte muss ein gültiges Header-Char sein (Content-Type oder ähnlich)
    assert content[:1].isalpha(), f"Erstes Byte sollte Header-Char sein, ist {content[:5]!r}"
    decoded = content.decode("utf-8")
    assert "Bad Homburg" in decoded
    assert "Subject:" in decoded


# ---------------------------------------------------------------------------
# 5. test_dry_run_no_smtp_call
# ---------------------------------------------------------------------------

def test_dry_run_no_smtp_call(tmp_path, monkeypatch):
    """Im Dry-Run-Pfad wird smtplib NIE aufgerufen."""
    from outreach_cli.email.transport import DryRunTransport

    smtp_calls = []

    class _FakeSMTP:
        def __init__(self, *a, **kw):
            smtp_calls.append(("__init__", a, kw))

        def __getattr__(self, name):
            smtp_calls.append((name,))
            return lambda *a, **kw: None

    monkeypatch.setattr(smtplib, "SMTP", _FakeSMTP)
    monkeypatch.setattr(smtplib, "SMTP_SSL", _FakeSMTP)

    lead = _lead()
    client = _fake_client_with(lead)
    run_send(
        tab="Frankfurt_Umland", template_name="variante_c",
        transport=DryRunTransport(preview_dir=tmp_path),
        sheet_client=client,
    )
    assert smtp_calls == [], f"SMTP wurde aufgerufen: {smtp_calls}"


# ---------------------------------------------------------------------------
# 6. test_lead_filter_score_min
# ---------------------------------------------------------------------------

def test_lead_filter_score_min():
    leads = (
        _lead(email="low@x.de", score="3"),
        _lead(email="mid@x.de", score="5"),
        _lead(email="high@x.de", score="7"),
    )
    client = _fake_client_with(*leads)
    filtered, stats = load_filtered_leads(client, tab="X", score_min=5)
    assert stats.total_in_tab == 3
    assert stats.after_score == 2
    emails = sorted(f.email for f in filtered)
    assert emails == ["high@x.de", "mid@x.de"]


# ---------------------------------------------------------------------------
# 7. test_lead_filter_status
# ---------------------------------------------------------------------------

def test_lead_filter_status():
    leads = (
        _lead(email="neu@x.de", rs="Neu"),
        _lead(email="alt@x.de", rs="Angeschrieben"),
        _lead(email="fertig@x.de", rs="Geantwortet - kein Interesse"),
    )
    client = _fake_client_with(*leads)
    filtered, stats = load_filtered_leads(client, tab="X", status="Neu")
    assert stats.after_status == 1
    assert filtered[0].email == "neu@x.de"


# ---------------------------------------------------------------------------
# 8. test_lead_filter_limit
# ---------------------------------------------------------------------------

def test_lead_filter_limit():
    leads = tuple(_lead(email=f"lead{i}@x.de") for i in range(10))
    client = _fake_client_with(*leads)
    filtered, stats = load_filtered_leads(client, tab="X", limit=3)
    assert stats.after_limit == 3
    assert len(filtered) == 3


# ---------------------------------------------------------------------------
# 9. test_hwg_filter_excludes_doctors
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("firma,branche,should_exclude", [
    ("Dr. med. Müller MVZ", "Kosmetik", True),
    ("Praxis Schmidt", "Heilpraktiker / Akupunktur", True),
    ("Praxis Heilpraktikerin Weber", "TCM", True),
    ("Arzt Praxis Berlin", "Allgemeinmedizin", True),
    ("Studio Schöne Haut", "Ärztin Tegel-Aestethics", True),
    ("Kosmetik Bad Homburg", "Kosmetikstudio", False),
])
def test_hwg_filter_excludes_doctors(firma, branche, should_exclude):
    lead = _lead(firma=firma, branche=branche)
    excluded, reason = is_hwg_excluded(lead)
    assert excluded is should_exclude, f"firma={firma!r}, branche={branche!r}, reason={reason!r}"


# ---------------------------------------------------------------------------
# 10. test_hwg_filter_keeps_tcm_generic
# ---------------------------------------------------------------------------

def test_hwg_filter_keeps_tcm_generic():
    """Generische TCM-Studios bleiben drin — nur in Kombi mit Heilpraktiker/Arzt
    werden sie ausgeschlossen."""
    lead_tcm_pure = _lead(firma="TCM Studio Hamburg", branche="TCM / Akupunktur")
    excluded, _ = is_hwg_excluded(lead_tcm_pure)
    assert excluded is False

    lead_tcm_hp = _lead(firma="TCM Heilpraktiker Hamburg", branche="TCM")
    excluded, reason = is_hwg_excluded(lead_tcm_hp)
    assert excluded is True
    assert "heilpraktiker" in reason


# ---------------------------------------------------------------------------
# 11. test_stadt_aus_spalte_nicht_tab
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("entscheider, expected", [
    ("Frau Bitter",       "Sehr geehrte Frau Bitter"),
    ("Herr Bitter",       "Sehr geehrter Herr Bitter"),
    ("Frau Dr. Schmidt",  "Sehr geehrte Frau Dr. Schmidt"),
    ("Herr Dr. Schmidt",  "Sehr geehrter Herr Dr. Schmidt"),
    ("Dr. Schmidt",       "Sehr geehrte/r Dr. Schmidt"),  # Titel ohne Gender
    ("Maria Müller",      "Sehr geehrte/r Maria Müller"),  # Vorname → neutral
    ("",                  "Sehr geehrte Damen und Herren"),
    ("   ",               "Sehr geehrte Damen und Herren"),
])
def test_salutation_grammar(entscheider, expected):
    """Anrede-Konstruktion: 'Frau X' → 'Sehr geehrte Frau X', kein '/r' wenn
    Salutation bereits gendered."""
    from outreach_cli.leads.loader import _build_salutation
    assert _build_salutation(entscheider) == expected


def test_stadt_aus_spalte_nicht_tab():
    """Variable {stadt} kommt aus STADT-Spalte, NICHT aus Tab-Namen."""
    # Lead-Tab heißt 'Frankfurt_Umland', STADT-Spalte sagt 'Bad Homburg'.
    lead = _lead(tab="Frankfurt_Umland", stadt="Bad Homburg")
    vars_ = derive_render_vars(lead)
    assert vars_["stadt"] == "Bad Homburg"
    assert "Frankfurt" not in vars_["stadt"]
    assert "Frankfurt" not in vars_["beispiel_keyword"]
    assert "Bad Homburg" in vars_["beispiel_keyword"]


# ---------------------------------------------------------------------------
# 12. test_eml_encoding_utf8_bom
# ---------------------------------------------------------------------------

def test_eml_no_bom_smtp_wire_compatible():
    """write_eml liefert SMTP-wire-fähige Bytes OHNE BOM-Prefix (CR-02 Fix).

    BOM vor MIME-Header bricht RFC-5322 — erstes Byte muss ein Header-Char sein.
    Test ist Regression-Schutz gegen Re-Adoption der alten BOM-Policy.
    """
    eml_bytes = build_eml(
        to_email="info@spa-königstein.de",
        from_email="georg@maxcontentseo.de",
        subject="Kurze Frage zu Ihrem Studio in Königstein",
        body="Sehr geehrte Frau Müller,\n\nfür Ihren Salon Schöneberg — größere Reichweite.",
    )
    assert not eml_bytes.startswith(UTF8_BOM), "BOM würde SMTP-Wire-Protocol brechen"
    assert eml_bytes[:1].isalpha(), f"Erstes Byte muss Header-Char sein, ist {eml_bytes[:5]!r}"
    decoded = eml_bytes.decode("utf-8")
    assert "Subject:" in decoded
    assert "Content-Type: text/plain" in decoded
    assert "utf-8" in decoded.lower()


# ---------------------------------------------------------------------------
# 13. test_eml_subject_mime_encoded
# ---------------------------------------------------------------------------

def test_eml_subject_mime_encoded():
    """Subject mit Umlauten wird RFC-2047-MIME-encoded (=?UTF-8?...?=)."""
    eml_bytes = build_eml(
        to_email="x@y.de", from_email="georg@maxcontentseo.de",
        subject="Schöne Grüße aus München",
        body="ascii only",
    )
    decoded = eml_bytes.decode("utf-8")
    # MIME-encoded Subject muss `=?utf-8?` enthalten (Python email-stdlib
    # nutzt entweder base64 'b' oder quoted-printable 'q').
    assert "=?utf-8?" in decoded.lower() or "Schöne" in decoded, (
        "Subject sollte entweder MIME-encoded oder raw-UTF-8 sein "
        f"— gefunden: {decoded[:300]!r}"
    )
    # ASCII-only Body sollte NICHT MIME-Subject-encoded sein
    eml2 = build_eml(
        to_email="x@y.de", from_email="georg@maxcontentseo.de",
        subject="Plain ASCII Subject",
        body="ascii only",
    )
    d2 = eml2.decode("utf-8")
    assert "Plain ASCII Subject" in d2
