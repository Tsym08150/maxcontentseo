"""Zentrale Do-Not-Contact (DNC) Suppression.

Eine Datei, eine Wahrheit. ALLE Sender (outreach-cli send, one_shot_send.py,
send_outreach.ps1) MUESSEN vor jedem Send is_suppressed() / load_suppression()
konsultieren.

Dateiformat (Tools/do_not_contact.txt):
  - eine Email pro Zeile, lowercased
  - optionaler Kommentar nach '#'  (z.B. "x@y.de  # DNC - Grund Datum")
  - Leerzeilen und reine Kommentarzeilen werden ignoriert

Fehlende Datei => leere Menge (kein Crash beim Send). Ein DNC-Treffer ist hart.
Pfad ueberschreibbar via ENV OUTREACH_DNC_FILE (fuer Tests/Dry-Runs).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Optional

DEFAULT_DNC_PATH = Path(r"D:\000 SEO Business\Tools\do_not_contact.txt")


def dnc_path() -> Path:
    """Aktiver DNC-Dateipfad. ENV OUTREACH_DNC_FILE > Default."""
    env = os.environ.get("OUTREACH_DNC_FILE")
    return Path(env) if env else DEFAULT_DNC_PATH


def load_suppression(path: Optional[Path] = None) -> set[str]:
    """Liest die DNC-Datei in eine Menge lowercased Emails.

    Fehlende Datei => leere Menge (fail-open NUR bei fehlender Datei; ein
    vorhandener Eintrag wirkt hart).
    """
    p = path or dnc_path()
    if not p.exists():
        return set()
    out: set[str] = set()
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip().lower()
        if line:
            out.add(line)
    return out


def is_suppressed(email: str, suppressed: Optional[Iterable[str]] = None) -> bool:
    """True wenn email auf der DNC-Liste steht (case-insensitive).

    `suppressed` kann eine vorab geladene Menge sein (spart Datei-IO im Loop).
    """
    s = set(suppressed) if suppressed is not None else load_suppression()
    return email.strip().lower() in s
