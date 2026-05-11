"""Template-Engine für outreach-cli send.

Templates liegen als .txt-Dateien mit YAML-Frontmatter in diesem Paket.
Format:
    ---
    subject: "Kurze Frage zu Ihrem Kosmetikstudio in {stadt}"
    version: "C"
    ---
    Sehr geehrte/r {name},

    [Body mit {beispiel_keyword} etc.]

    Mit freundlichen Grüßen
    Georg Stopfer

Render-Engine: Python stdlib `str.format`. **Fail-fast bei fehlender Variable**
(KeyError, nicht silent empty) — Schutz vor halb-fertigen Personalisierungen.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

TEMPLATES_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Template:
    name: str
    subject_tpl: str
    body_tpl: str
    metadata: dict[str, str]


class TemplateNotFoundError(FileNotFoundError):
    pass


class TemplateParseError(ValueError):
    pass


class MissingTemplateVariableError(KeyError):
    """KeyError-Subklasse — bei Render mit fehlender Variable."""


def parse_template(raw: str) -> tuple[dict[str, str], str]:
    """Trennt YAML-Frontmatter von Body.

    Returns: (metadata_dict, body_text)
    Raises: TemplateParseError wenn Frontmatter fehlt oder kaputt.
    """
    lines = raw.splitlines()
    if not lines or lines[0].strip() != "---":
        raise TemplateParseError(
            "Template muss mit '---' starten (YAML-Frontmatter)."
        )
    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        raise TemplateParseError(
            "Frontmatter nicht geschlossen — zweites '---' fehlt."
        )

    metadata: dict[str, str] = {}
    for line in lines[1:end_idx]:
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            raise TemplateParseError(f"Frontmatter-Zeile ohne ':': {line!r}")
        key, _, value = line.partition(":")
        # Quotes drumherum strippen
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        metadata[key.strip()] = value

    # Body = alles nach dem zweiten '---'. Führendes Leerzeichen weg.
    body_lines = lines[end_idx + 1:]
    # Erstes leeres Trennzeile entfernen
    while body_lines and body_lines[0].strip() == "":
        body_lines.pop(0)
    body = "\n".join(body_lines)
    return metadata, body


def load_template(name: str, templates_dir: Path | None = None) -> Template:
    """Lädt Template anhand Name (ohne .txt-Suffix).

    Beispiel: load_template("variante_c") → templates/variante_c.txt
    """
    base = templates_dir or TEMPLATES_DIR
    path = base / f"{name}.txt"
    if not path.exists():
        raise TemplateNotFoundError(f"Template nicht gefunden: {path}")
    raw = path.read_text(encoding="utf-8-sig")
    metadata, body = parse_template(raw)
    subject = metadata.get("subject", "")
    if not subject:
        raise TemplateParseError(
            f"Template {name!r} hat keinen 'subject' im Frontmatter."
        )
    return Template(
        name=name,
        subject_tpl=subject,
        body_tpl=body,
        metadata=metadata,
    )


def render(template: Template, variables: Mapping[str, str]) -> tuple[str, str]:
    """Rendert Subject + Body mit str.format. Fail-fast bei fehlender Variable.

    Returns: (subject, body)
    Raises: MissingTemplateVariableError wenn eine {var} nicht in variables ist.
    """
    try:
        subject = template.subject_tpl.format(**variables)
        body = template.body_tpl.format(**variables)
    except KeyError as e:
        raise MissingTemplateVariableError(
            f"Template {template.name!r} verlangt Variable {e.args[0]!r}, "
            f"die nicht in den Lead-Daten gegeben ist."
        ) from None
    return subject, body
