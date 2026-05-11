"""Lead-Loader für outreach-cli send.

Liest Leads direkt aus dem Google-Sheet (kein leads.csv-Zwischenschritt),
wendet Filter an (Tab/Score/Status/Limit) und schließt Heilpraktiker/Ärzte
gemäß HWG-Vorgabe aus.

HWG = Heilwerbegesetz (DE). Outreach an Ärzte/Heilpraktiker erfordert ein
separates rechtssicheres Template — wird bewusst ausgeschlossen bis das
existiert.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from ..sheets import LeadRow, SheetClient

# HWG-Trigger-Worte. Word-boundary regex Match in BRANCHE+FIRMA, NICHT substring
# (Fix REVIEW-send CR-01, 2026-05-11):
#   substring "arzt" matched in "Quarztherapie" — false positive.
#   Wir wollen nur ganze Wörter (oder Wort-Anfang/-Ende mit Whitespace/Interpunktion).
# "TCM" allein ist KEIN Trigger — nur in Kombi mit Heilpraktiker/Arzt.
HWG_TRIGGERS: tuple[str, ...] = (
    "heilpraktiker",
    "heilpraktikerin",
    "dr. med.",
    "dr.med.",
    "arzt",
    "aerztin",
    "ärztin",
)

# Word-boundary-Patterns. `\b` matched zwischen \w und \W, aber Umlaute (ü etc.)
# zählen für `\b` als \w-Char, daher funktioniert das für deutsche Wörter ebenfalls.
# Punkt in "Dr. med." behandeln wir mit explizitem Lookaround statt \b
# (\b nach Punkt funktioniert nicht intuitiv).
def _compile_hwg_pattern(trigger: str) -> re.Pattern:
    if "." in trigger:
        # "Dr. med." mit flexiblem Whitespace + word-boundary nur am Ende
        # "dr. med." → match "Dr. med.", "Dr.med.", "dr.  med." — alle case-insensitive
        # Vor dem 'D'/'d' muss word-boundary sein, nach dem letzten Punkt egal.
        # Pattern: (?<!\w)dr\.\s*med\.
        return re.compile(r"(?<!\w)dr\.\s*med\.", re.IGNORECASE)
    return re.compile(rf"(?<!\w){re.escape(trigger)}(?!\w)", re.IGNORECASE)


_HWG_PATTERNS: tuple[tuple[str, re.Pattern], ...] = tuple(
    (t, _compile_hwg_pattern(t)) for t in HWG_TRIGGERS
)


@dataclass(frozen=True)
class FilteredLead:
    """LeadRow + abgeleitete Render-Variablen für Template-Engine."""
    lead: LeadRow
    render_vars: dict[str, str]

    @property
    def email(self) -> str:
        return self.lead.email

    @property
    def firma(self) -> str:
        return self.lead.firma


@dataclass
class FilterStats:
    total_in_tab: int = 0
    after_score: int = 0
    after_status: int = 0
    after_hwg: int = 0
    after_limit: int = 0
    hwg_excluded: list[str] = field(default_factory=list)
    skipped_no_render_vars: list[str] = field(default_factory=list)  # HIGH-03 Fix


def is_hwg_excluded(lead: LeadRow) -> tuple[bool, Optional[str]]:
    """True wenn Lead unter HWG-Filter fällt. Returns (excluded, reason).

    Word-boundary-Match (CR-01 Fix): "Quarztherapie" matched NICHT auf "arzt".
    """
    haystack = f"{lead.firma} | {lead.data.get('BRANCHE', '')}"
    for trigger, pattern in _HWG_PATTERNS:
        if pattern.search(haystack):
            return True, trigger
    return False, None


def _build_salutation(entscheider: str) -> str:
    """Grammatikalisch korrekte deutsche Geschäftsbrief-Anrede.

    - "Frau X"        → "Sehr geehrte Frau X"
    - "Herr X"        → "Sehr geehrter Herr X"
    - "Dr. X"         → "Sehr geehrte/r Dr. X" (Titel ohne Gender → neutral)
    - "Frau Dr. X"    → "Sehr geehrte Frau Dr. X"
    - "Herr Dr. X"    → "Sehr geehrter Herr Dr. X"
    - leerer string   → "Sehr geehrte Damen und Herren"
    - sonst           → "Sehr geehrte/r {entscheider}"  (Vorname/unsicher)
    """
    e = entscheider.strip()
    if not e:
        return "Sehr geehrte Damen und Herren"
    # Case-sensitive prefix-match — Frau/Herr werden im Sheet so geschrieben.
    if e.startswith("Frau "):
        return f"Sehr geehrte {e}"
    if e.startswith("Herr "):
        return f"Sehr geehrter {e}"
    return f"Sehr geehrte/r {e}"


def derive_render_vars(lead: LeadRow) -> dict[str, str]:
    """Leitet Template-Variablen aus Sheet-Spalten ab.

    Konvention:
      - {stadt}            : aus STADT-Spalte (NICHT Tab-Name) — fail wenn leer
      - {name}             : aus Entscheider-Spalte; fallback "Sehr geehrte Damen und Herren"
      - {beispiel_keyword} : aus BRANCHE (erstes Wort vor '/') + STADT
                             z.B. BRANCHE="Kosmetik / Anti-Aging", STADT="Bad Homburg"
                             → "Kosmetik Bad Homburg"
                             fail wenn BRANCHE leer
      - {firma}            : aus FIRMA-Spalte (für Logs/Internas)
    """
    stadt = lead.stadt.strip()
    if not stadt:
        raise ValueError(
            f"Lead {lead.email!r} ({lead.tab} Z.{lead.row_index}): "
            f"STADT-Spalte leer — Template kann nicht gerendert werden."
        )

    name = _build_salutation(lead.data.get("Entscheider", "").strip())

    branche = lead.data.get("BRANCHE", "").strip()
    if not branche:
        raise ValueError(
            f"Lead {lead.email!r} ({lead.tab} Z.{lead.row_index}): "
            f"BRANCHE-Spalte leer — beispiel_keyword nicht ableitbar."
        )
    # MEDIUM-05 Fix: erstes nicht-leeres Segment nach Split, nicht blindly [0]
    segments = [p.strip() for p in branche.split("/") if p.strip()]
    if not segments:
        raise ValueError(
            f"Lead {lead.email!r}: BRANCHE {branche!r} enthält nur Slashes."
        )
    primary_branche = segments[0]
    beispiel_keyword = f"{primary_branche} {stadt}"

    return {
        "stadt": stadt,
        "name": name,
        "beispiel_keyword": beispiel_keyword,
        "firma": lead.firma,
    }


def load_filtered_leads(
    client: SheetClient,
    tab: str,
    score_min: int = 0,
    status: Optional[str] = None,
    limit: int = 0,
    exclude_hwg: bool = True,
) -> tuple[list[FilteredLead], FilterStats]:
    """Lädt Leads aus Sheet-Tab + wendet Filter an.

    Filter-Reihenfolge:
      1. Score >= score_min (wenn score_min > 0)
      2. Recherche_Status == status (wenn status gesetzt)
      3. HWG-Exklusion (wenn exclude_hwg)
      4. Limit (wenn limit > 0)

    Returns: (FilteredLead-Liste, FilterStats fürs Logging)
    """
    stats = FilterStats()

    all_leads: list[LeadRow] = []
    try:
        for lead in client.iter_tab_rows(tab):
            # Skip Leads ohne Email (leere Zeilen)
            if not lead.email:
                continue
            all_leads.append(lead)
    except Exception as e:
        raise RuntimeError(f"Fehler beim Lesen von Tab {tab!r}: {e}") from e

    stats.total_in_tab = len(all_leads)

    # 1. Score-Filter
    if score_min > 0:
        kept: list[LeadRow] = []
        for l in all_leads:
            try:
                sc = int(l.score) if l.score else 0
            except ValueError:
                sc = 0
            if sc >= score_min:
                kept.append(l)
        all_leads = kept
    stats.after_score = len(all_leads)

    # 2. Status-Filter
    if status is not None:
        all_leads = [l for l in all_leads if l.recherche_status == status]
    stats.after_status = len(all_leads)

    # 3. HWG-Exklusion
    if exclude_hwg:
        kept = []
        for l in all_leads:
            excluded, reason = is_hwg_excluded(l)
            if excluded:
                stats.hwg_excluded.append(
                    f"{l.email} ({l.firma}) — Trigger: {reason!r}"
                )
            else:
                kept.append(l)
        all_leads = kept
    stats.after_hwg = len(all_leads)

    # 4. Limit
    if limit > 0:
        all_leads = all_leads[:limit]
    stats.after_limit = len(all_leads)

    # 5. Render-Variablen ableiten — per-lead robust (HIGH-03 Fix).
    # Eine fehlende STADT/BRANCHE darf den Batch NICHT killen.
    results: list[FilteredLead] = []
    for l in all_leads:
        try:
            vars_ = derive_render_vars(l)
        except ValueError as e:
            stats.skipped_no_render_vars.append(
                f"{l.email} ({l.firma or '?'}) — {e}"
            )
            continue
        results.append(FilteredLead(lead=l, render_vars=vars_))

    return results, stats
