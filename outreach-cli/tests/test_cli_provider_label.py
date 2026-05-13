"""Test: _active_provider_name() spiegelt pipeline-Selection."""

from __future__ import annotations

import pytest

from outreach_cli.cli import _active_provider_name


def test_nb_active_when_only_nb_key(monkeypatch):
    monkeypatch.setenv("NEVERBOUNCE_API_KEY", "real-nb-key")
    monkeypatch.delenv("ZEROBOUNCE_API_KEY", raising=False)
    assert _active_provider_name() == "NeverBounce"


def test_nb_active_when_both_keys_set(monkeypatch):
    """NB hat Priorität — Spiegel zur pipeline._select_provider_client-Logik."""
    monkeypatch.setenv("NEVERBOUNCE_API_KEY", "real-nb-key")
    monkeypatch.setenv("ZEROBOUNCE_API_KEY", "real-zb-key")
    assert _active_provider_name() == "NeverBounce"


def test_zb_fallback_when_nb_missing(monkeypatch):
    monkeypatch.delenv("NEVERBOUNCE_API_KEY", raising=False)
    monkeypatch.setenv("ZEROBOUNCE_API_KEY", "real-zb-key")
    assert _active_provider_name() == "ZeroBounce"


def test_zb_fallback_when_nb_placeholder(monkeypatch):
    monkeypatch.setenv("NEVERBOUNCE_API_KEY", "REPLACE_ME_WITH_KEY")
    monkeypatch.setenv("ZEROBOUNCE_API_KEY", "real-zb-key")
    assert _active_provider_name() == "ZeroBounce"


def test_generic_label_when_neither_configured(monkeypatch):
    """Edge: pure cache-only Run ohne Provider-Konfig → kein hartes Crash, generischer Label."""
    monkeypatch.delenv("NEVERBOUNCE_API_KEY", raising=False)
    monkeypatch.delenv("ZEROBOUNCE_API_KEY", raising=False)
    assert _active_provider_name() == "Email-Verifier"


def test_placeholder_patterns_recognized(monkeypatch):
    """Alle Placeholder-Prefixe (REPLACE_, YOUR_, CHANGE_ME) gelten als nicht-konfiguriert."""
    for placeholder in ("REPLACE_ME_KEY", "YOUR_NB_KEY", "CHANGE_ME"):
        monkeypatch.setenv("NEVERBOUNCE_API_KEY", placeholder)
        monkeypatch.delenv("ZEROBOUNCE_API_KEY", raising=False)
        assert _active_provider_name() == "Email-Verifier", f"Placeholder {placeholder!r} nicht erkannt"
