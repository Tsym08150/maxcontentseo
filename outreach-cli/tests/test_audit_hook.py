"""audit_hook Tests — sanitize, find_latest, extract_hook."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from outreach_cli.audit_hook import (
    AuditHookExtractError,
    AuditHookNotFoundError,
    extract_hook,
    find_latest_outreach_file,
    get_audit_hook,
    sanitize_domain,
)


# ---------------------------------------------------------------------------
# sanitize_domain
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw,expected", [
    ("vitaminbude.de", "vitaminbude-de"),
    ("VITAMINBUDE.DE", "vitaminbude-de"),
    ("https://www.example.com/", "example-com"),
    ("http://example.com/path?q=1", "example-com"),
    ("www.example.com", "example-com"),
    ("foo.bar.baz", "foo-bar-baz"),
    ("with-dash.de", "with-dash-de"),
    ("  spaced.de  ", "spaced-de"),
    ("https://example.de#anchor", "example-de"),
])
def test_sanitize_domain_normalizes(raw, expected):
    assert sanitize_domain(raw) == expected


def test_sanitize_domain_empty():
    assert sanitize_domain("") == ""
    assert sanitize_domain("  ") == ""


# ---------------------------------------------------------------------------
# find_latest_outreach_file
# ---------------------------------------------------------------------------

def _make_file(dir: Path, name: str, mtime_offset: float = 0) -> Path:
    p = dir / name
    p.write_text("dummy", encoding="utf-8")
    if mtime_offset:
        import os
        new = time.time() + mtime_offset
        os.utime(p, (new, new))
    return p


def test_find_latest_picks_newest_by_mtime(tmp_path: Path):
    old = _make_file(tmp_path, "outreach-test-de-20260501.txt", mtime_offset=-100)
    new = _make_file(tmp_path, "outreach-test-de-20260513.txt", mtime_offset=0)
    found = find_latest_outreach_file("test.de", reports_dir=tmp_path)
    assert found == new


def test_find_latest_raises_when_no_match(tmp_path: Path):
    _make_file(tmp_path, "outreach-other-de-20260513.txt")
    with pytest.raises(AuditHookNotFoundError) as exc:
        find_latest_outreach_file("missing.de", reports_dir=tmp_path)
    assert "missing.de" in str(exc.value)
    assert "/audit missing.de" in str(exc.value)


def test_find_latest_empty_domain_raises(tmp_path: Path):
    with pytest.raises(AuditHookNotFoundError):
        find_latest_outreach_file("", reports_dir=tmp_path)


# ---------------------------------------------------------------------------
# extract_hook
# ---------------------------------------------------------------------------

_SAMPLE_OUTREACH = """Betreff: Kurze Frage zu Ihrem Shop in München

Sehr geehrter Herr Villinger,

Beim Aufruf einzelner URL-Varianten Ihres Shops erscheint eine 404-Fehlerseite.

Zusätzlich erscheint der Platzhalter #IndexMetaDescriptionStandard# in der SERP.

Wenn Sie möchten, schicke ich Ihnen einen kurzen Befund-Report.

Mit freundlichen Grüßen
[ABSENDER]
"""


def test_extract_hook_returns_finding_paragraphs(tmp_path: Path):
    p = tmp_path / "outreach-x-de-1.txt"
    p.write_text(_SAMPLE_OUTREACH, encoding="utf-8")
    hook = extract_hook(p)
    assert "404-Fehlerseite" in hook
    assert "IndexMetaDescriptionStandard" in hook
    # CTA + closing nicht enthalten
    assert "Wenn Sie möchten" not in hook
    assert "Mit freundlichen Grüßen" not in hook
    # Greeting nicht enthalten
    assert "Sehr geehrter" not in hook


def test_extract_hook_strips_edge_blank_lines(tmp_path: Path):
    p = tmp_path / "outreach-x-de-2.txt"
    p.write_text(_SAMPLE_OUTREACH, encoding="utf-8")
    hook = extract_hook(p)
    assert not hook.startswith("\n")
    assert not hook.endswith("\n")


def test_extract_hook_preserves_paragraph_breaks(tmp_path: Path):
    """Mehrere Paragraphen bleiben durch Doppel-Newlines getrennt."""
    p = tmp_path / "outreach-x-de-3.txt"
    p.write_text(_SAMPLE_OUTREACH, encoding="utf-8")
    hook = extract_hook(p)
    # Sollte 2 Paragraphen sein, getrennt durch eine Leerzeile
    assert "\n\n" in hook


def test_extract_hook_missing_greeting_raises(tmp_path: Path):
    p = tmp_path / "no_greeting.txt"
    p.write_text("Betreff: X\n\nKein normales Greeting hier.\n\nMit freundlichen Grüßen\n", encoding="utf-8")
    with pytest.raises(AuditHookExtractError, match="Greeting"):
        extract_hook(p)


def test_extract_hook_missing_cta_raises(tmp_path: Path):
    p = tmp_path / "no_cta.txt"
    p.write_text(
        "Betreff: X\n\nSehr geehrte Damen und Herren,\n\nEin Befund.\n\nKein CTA-Marker.\n",
        encoding="utf-8",
    )
    with pytest.raises(AuditHookExtractError, match="CTA-Marker"):
        extract_hook(p)


def test_extract_hook_empty_section_raises(tmp_path: Path):
    """Greeting direkt gefolgt von CTA → leerer Hook → Fehler."""
    p = tmp_path / "empty_hook.txt"
    p.write_text(
        "Sehr geehrte Damen und Herren,\nWenn Sie möchten, schicke ich Ihnen...\n",
        encoding="utf-8",
    )
    with pytest.raises(AuditHookExtractError, match="leer"):
        extract_hook(p)


# ---------------------------------------------------------------------------
# get_audit_hook (Integration)
# ---------------------------------------------------------------------------

def test_get_audit_hook_end_to_end(tmp_path: Path):
    p = tmp_path / "outreach-some-de-20260513.txt"
    p.write_text(_SAMPLE_OUTREACH, encoding="utf-8")
    hook = get_audit_hook("some.de", reports_dir=tmp_path)
    assert "404-Fehlerseite" in hook
    assert "Platzhalter" in hook


def test_get_audit_hook_picks_newest_when_multiple(tmp_path: Path):
    """Wenn mehrere Reports existieren (z.B. -v2, -v3), gewinnt der neueste."""
    older = tmp_path / "outreach-multi-de-20260512-v2.txt"
    older.write_text(_SAMPLE_OUTREACH.replace("404-Fehlerseite", "ALTER-Befund"), encoding="utf-8")
    import os
    os.utime(older, (time.time() - 100, time.time() - 100))

    newer = tmp_path / "outreach-multi-de-20260513-v3.txt"
    newer.write_text(_SAMPLE_OUTREACH.replace("404-Fehlerseite", "NEUER-Befund"), encoding="utf-8")

    hook = get_audit_hook("multi.de", reports_dir=tmp_path)
    assert "NEUER-Befund" in hook
    assert "ALTER-Befund" not in hook
