"""Audit-Hook Lookup: brückt /audit Skill ↔ outreach-cli send.

/audit (in Claude Code) erzeugt pro Domain eine `reports/outreach-<domain>-<date>.txt`
mit personalisiertem Hook (Trailing-Slash-Befund, Meta-Description-Platzhalter,
Sichtbarkeits-Verlust etc.). Dieser Modul liest die Hook-Paragraphen raus und
liefert sie als String für Template-Injection.

Verwendet von:
  - outreach_cli.commands.send.run_send (wenn template == "variante_audit")
"""

from __future__ import annotations

import re
from pathlib import Path


_REPORTS_DIR = Path(__file__).resolve().parent.parent.parent / "reports"
_DOMAIN_SANITIZE_RE = re.compile(r"[^a-z0-9]+")


class AuditHookNotFoundError(FileNotFoundError):
    """Kein outreach-<domain>-*.txt für diese Domain gefunden."""


class AuditHookExtractError(ValueError):
    """Datei vorhanden, aber Hook-Sektion nicht parseable (kein Greeting / kein CTA)."""


def sanitize_domain(raw: str) -> str:
    """Normalisiert eine Domain auf das `audit`-Skill-File-Naming.

    Beispiele:
      vitaminbude.de              → vitaminbude-de
      https://www.example.com/    → example-com
      EXAMPLE.de                  → example-de
      foo.bar.baz                 → foo-bar-baz
    """
    s = (raw or "").strip().lower()
    # Protocol weg
    s = re.sub(r"^https?://", "", s)
    # www. weg
    s = re.sub(r"^www\.", "", s)
    # Path / Query / Fragment weg — nur Host
    s = s.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
    # Non-alphanumeric → Bindestrich, edges trimmen
    return _DOMAIN_SANITIZE_RE.sub("-", s).strip("-")


def find_latest_outreach_file(domain: str, reports_dir: Path | None = None) -> Path:
    """Findet die neueste `outreach-<sanitized-domain>-*.txt`. Newest = höchste mtime.

    Raises AuditHookNotFoundError wenn kein Match.
    """
    base = reports_dir or _REPORTS_DIR
    sanitized = sanitize_domain(domain)
    if not sanitized:
        raise AuditHookNotFoundError(f"Domain {domain!r} kann nicht sanitiert werden.")
    pattern = f"outreach-{sanitized}-*.txt"
    candidates = sorted(
        base.glob(pattern),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise AuditHookNotFoundError(
            f"Kein Audit-Outreach-Report für Domain {domain!r} "
            f"(sanitized: {sanitized!r}) in {base}/.\n"
            f"Lösung: vorher in Claude Code '/audit {domain}' ausführen — der Skill "
            f"erzeugt reports/{pattern.replace('*', '<date>')}."
        )
    return candidates[0]


def extract_hook(path: Path) -> str:
    """Extrahiert die personalisierten Befund-Paragraphen aus dem outreach-*.txt.

    File-Struktur (von /audit erzeugt):
        Betreff: ...

        Sehr geehrte/r <NAME>,

        <FINDING-PARAGRAPH 1>

        <FINDING-PARAGRAPH 2 (optional)>

        Wenn Sie möchten, schicke ich Ihnen einen kurzen Befund-Report...
        Ein kurzes "Ja" per Antwort genügt.

        Mit freundlichen Grüßen
        [ABSENDER]

    Returns: Lines zwischen Greeting+1 und CTA-Marker, mit erhaltenen Paragraph-Breaks.
    Edges trimmt blanks.

    Raises AuditHookExtractError wenn Greeting oder CTA nicht findbar.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    greeting_idx = next(
        (i for i, l in enumerate(lines) if l.strip().lower().startswith("sehr geehrte")),
        None,
    )
    if greeting_idx is None:
        raise AuditHookExtractError(
            f"{path.name}: Kein 'Sehr geehrte/r ...'-Greeting gefunden. "
            f"Datei-Format weicht von /audit-Konvention ab."
        )

    cta_idx = None
    for i in range(greeting_idx + 1, len(lines)):
        low = lines[i].strip().lower()
        if (
            low.startswith("wenn sie möchten")
            or low.startswith("wenn sie moechten")
            or 'kurzes "ja"' in low
            or "kurzes 'ja'" in low
            or low.startswith("mit freundlichen grüßen")
            or low.startswith("mit freundlichen gruessen")
        ):
            cta_idx = i
            break
    if cta_idx is None:
        raise AuditHookExtractError(
            f"{path.name}: CTA-Marker ('Wenn Sie möchten' / 'Ein kurzes Ja' / "
            f"'Mit freundlichen Grüßen') nicht gefunden."
        )

    hook_lines = lines[greeting_idx + 1:cta_idx]
    while hook_lines and not hook_lines[0].strip():
        hook_lines.pop(0)
    while hook_lines and not hook_lines[-1].strip():
        hook_lines.pop()
    if not hook_lines:
        raise AuditHookExtractError(
            f"{path.name}: Hook-Sektion zwischen Greeting und CTA ist leer."
        )
    return "\n".join(hook_lines)


def get_audit_hook(domain: str, reports_dir: Path | None = None) -> str:
    """Convenience: sanitize → find newest → extract hook. Eine API für send.py.

    Raises AuditHookNotFoundError | AuditHookExtractError.
    """
    return extract_hook(find_latest_outreach_file(domain, reports_dir=reports_dir))
