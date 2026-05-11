"""gspread-Wrapper mit header-bewusster Lookup-/Update-Logik.

Aktuelles Schema (Stand 2026-05-11 nach Phase 1-6 Migration):
- Primary tabs (Stadt-Tabs): Muenchen, Hamburg, Frankfurt, Frankfurt_Umland, Bad Homburg
- Aggregate tab: Alle_Leads (Master mit allen Leads aller Städte)
- Header werden über HEADER_ALIASES tolerant gematcht (alt-Frankfurt '.', alt-Muenchen
  'KONTAKTIERT' / 'FOLLOW-UP', Alle_Leads/Frankfurt_Umland 'Stadt' klein-s).

Mutation-Verträge (siehe set_status):
- Aggregat-Sync ist BEST-EFFORT, nicht atomar. Partielles Schreiben wird im
  Result reportet (partial_failure=True) — Caller entscheidet wie weiter.
- LETZTE_ANTWORT_AM-Spalte fehlt → DATUM wird NICHT geschrieben (kein
  destruktiver Fallback auf KONTAKTIERT_AM). Status-Update läuft trotzdem
  durch. Hard-Warning im Result.
- Idempotency: wenn Lead bereits den Ziel-Status hat (und ggf. das Ziel-Datum),
  wird der Write übersprungen. Override mit `force=True`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Iterable, Optional, Sequence

import gspread
from google.oauth2.service_account import Credentials

from .config import (
    HEADER_ALIASES,
    H_ANTWORT,
    H_EMAIL,
    H_FIRMA,
    H_FOLLOWUP,
    H_KONTAKTIERT,
    H_RECHERCHE_STATUS,
    H_SCORE,
    H_SEO_PROBLEM,
    H_STADT,
    H_VERKAUFSSTATUS,
    Config,
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


# ---------------------------------------------------------------------------
# Reine Hilfsfunktionen — alle ohne Netzwerk, daher direkt unit-testbar.
# ---------------------------------------------------------------------------

def _col_letter(idx_zero: int) -> str:
    """Zero-based Spaltenindex -> A1-Buchstabe (0->A, 25->Z, 26->AA)."""
    n = idx_zero + 1
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _find_header(headers: list[str], name: str) -> Optional[int]:
    """Case-insensitive Header-Lookup mit Alias-Fallback. Erster Treffer gewinnt
    (Reihenfolge: Canonical zuerst, dann Aliase aus HEADER_ALIASES)."""
    candidates = [name] + list(HEADER_ALIASES.get(name, ()))
    for cand in candidates:
        target = cand.strip().lower()
        for i, h in enumerate(headers):
            if h.strip().lower() == target:
                return i
    return None


def _row_to_dict(headers: list[str], row: list[str]) -> dict[str, str]:
    """Padded Row -> Dict per Header. Kurze Rows werden mit '' aufgefüllt."""
    return {h: (row[i] if i < len(row) else "") for i, h in enumerate(headers)}


def _normalize_row(headers: list[str], row: list[str]) -> dict[str, str]:
    """Wie _row_to_dict + canonical-key-enrichment für aliased headers."""
    raw = _row_to_dict(headers, row)
    enriched = dict(raw)
    for canonical, aliases in HEADER_ALIASES.items():
        if canonical in raw:
            continue
        for alias in aliases:
            if alias in raw:
                enriched[canonical] = raw[alias]
                break
    return enriched


def _lead_value(lead: "LeadRow", column: str) -> str:
    """Header-aware Wert-Lookup auf einem LeadRow.
    Erst exact-key, dann case-insensitive Match. Behebt CR-01-Fall wo
    canonical-key fehlt aber alias-key vorhanden ist und nicht in HEADER_ALIASES."""
    if column in lead.data:
        return lead.data[column].strip()
    target = column.strip().lower()
    for k, v in lead.data.items():
        if k.strip().lower() == target:
            return v.strip()
    return ""


def _parse_date(s: str) -> Optional[date]:
    """Akzeptiert TT.MM.JJJJ, JJJJ-MM-TT, TT/MM/JJJJ. Sonst None."""
    raw = (s or "").strip()
    if not raw:
        return None
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def _date_column_for_status(status: str) -> Optional[str]:
    """Welche Datumsspalte gehört zu welchem Status? None => kein Datum."""
    if status.startswith("Geantwortet") or status == "Bounce":
        return H_ANTWORT
    if status == "Angeschrieben":
        return H_KONTAKTIERT
    if status == "Follow-up gesendet":
        return H_FOLLOWUP
    return None


# ---------------------------------------------------------------------------
# Datenmodell
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LeadRow:
    tab: str
    row_index: int
    data: dict[str, str]

    @property
    def email(self) -> str:
        return self.data.get(H_EMAIL, "").strip()

    @property
    def firma(self) -> str:
        return self.data.get(H_FIRMA, "").strip()

    @property
    def stadt(self) -> str:
        return self.data.get(H_STADT, "").strip()

    @property
    def recherche_status(self) -> str:
        return _lead_value(self, H_RECHERCHE_STATUS)

    @property
    def verkaufsstatus(self) -> str:
        return _lead_value(self, H_VERKAUFSSTATUS)

    @property
    def status(self) -> str:  # Backward-compat
        return self.recherche_status

    @property
    def score(self) -> str:
        return self.data.get(H_SCORE, "").strip()

    @property
    def seo_problem(self) -> str:
        return self.data.get(H_SEO_PROBLEM, "").strip()

    @property
    def followup_am(self) -> str:
        return self.data.get(H_FOLLOWUP, "").strip()

    @property
    def kontaktiert_am(self) -> str:
        return self.data.get(H_KONTAKTIERT, "").strip()

    def value(self, column: str) -> str:
        """Header-aware Wert-Lookup. Bevorzugt für Status-Spalten."""
        return _lead_value(self, column)


@dataclass
class WriteAttempt:
    """Was bei einem einzelnen Tab-Write passierte."""
    tab: str
    row_index: int
    success: bool
    skipped_idempotent: bool = False
    date_column_written: Optional[str] = None
    date_value_written: Optional[str] = None
    error: Optional[str] = None


@dataclass
class SetStatusResult:
    """Ergebnis eines set_status-Calls über primary + secondary Tabs.

    partial_failure ist True wenn mindestens ein Write versucht und gescheitert
    ist, während mindestens ein anderer durchging — Inkonsistenz zwischen Tabs.
    """
    primary: Optional[LeadRow]
    secondary: Optional[LeadRow]
    column_written: str
    attempts: list[WriteAttempt] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def writes_succeeded(self) -> int:
        return sum(1 for a in self.attempts if a.success and not a.skipped_idempotent)

    @property
    def writes_skipped(self) -> int:
        return sum(1 for a in self.attempts if a.skipped_idempotent)

    @property
    def writes_failed(self) -> int:
        return sum(1 for a in self.attempts if not a.success)

    @property
    def partial_failure(self) -> bool:
        """True wenn ≥1 write OK und ≥1 write FAIL — Tabs nun inkonsistent."""
        return self.writes_failed > 0 and self.writes_succeeded > 0

    @property
    def total_failure(self) -> bool:
        """Alle versuchten Writes (ohne Idempotency-Skips) fehlgeschlagen."""
        return self.writes_failed > 0 and self.writes_succeeded == 0


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class SheetsAPIError(RuntimeError):
    """Wrapper um gspread.APIError mit Tab/Operation-Kontext."""


# ---------------------------------------------------------------------------
# Sheet-Client
# ---------------------------------------------------------------------------

class SheetClient:
    def __init__(self, config: Config):
        self.config = config
        creds = Credentials.from_service_account_file(
            str(config.credentials_path), scopes=SCOPES
        )
        self._gc = gspread.authorize(creds)
        self._sh = self._gc.open_by_key(config.sheet_id)
        self._tab_cache: dict[str, tuple[list[str], list[list[str]]]] = {}

    # ----- Tab-Laden / Cache --------------------------------------------------

    def _load_tab(self, tab: str) -> tuple[list[str], list[list[str]]]:
        if tab in self._tab_cache:
            return self._tab_cache[tab]
        try:
            ws = self._sh.worksheet(tab)
            values = ws.get_all_values()
        except gspread.exceptions.APIError as e:
            raise SheetsAPIError(f"API-Fehler beim Lesen von Tab {tab!r}: {e}") from e
        if not values:
            self._tab_cache[tab] = ([], [])
            return ([], [])
        headers, data = values[0], values[1:]
        self._tab_cache[tab] = (headers, data)
        return (headers, data)

    def _invalidate(self, tab: str) -> None:
        self._tab_cache.pop(tab, None)

    # ----- Iteration ----------------------------------------------------------

    def iter_tab_rows(self, tab: str) -> Iterable[LeadRow]:
        headers, data = self._load_tab(tab)
        for offset, row in enumerate(data):
            yield LeadRow(
                tab=tab,
                row_index=offset + 2,
                data=_normalize_row(headers, row),
            )

    # ----- Queries ------------------------------------------------------------

    def find_by_email(
        self, email: str, tabs: Optional[Sequence[str]] = None
    ) -> Optional[LeadRow]:
        """Linearer Scan über `tabs` (default: primary_tabs). Erster Treffer gewinnt.

        Auth/Quota-Fehler (`gspread.APIError`) werden als `SheetsAPIError`
        weitergeworfen — damit Caller unterscheiden können zwischen
        "nicht gefunden" und "Scan abgebrochen".
        """
        target = email.strip().lower()
        if not target:
            return None
        scan_tabs = list(tabs) if tabs is not None else list(self.config.primary_tabs)
        if not scan_tabs:
            return None
        for tab in scan_tabs:
            try:
                for lead in self.iter_tab_rows(tab):
                    if lead.email.lower() == target:
                        return lead
            except gspread.exceptions.WorksheetNotFound:
                continue
            except gspread.exceptions.APIError as e:
                raise SheetsAPIError(
                    f"API-Fehler beim Scan von Tab {tab!r}: {e}"
                ) from e
        return None

    def find_in_aggregate(self, email: str) -> Optional[LeadRow]:
        return self.find_by_email(email, tabs=self.config.aggregate_tabs)

    def _match_tab(self, stadt: str) -> Optional[str]:
        for t in self.config.primary_tabs:
            if t.lower() == stadt.lower():
                return t
        return None

    def followups_on(self, stadt: str, the_date: date) -> list[LeadRow]:
        targets = {
            the_date.strftime("%d.%m.%Y"),
            the_date.strftime("%Y-%m-%d"),
        }
        tab_match = self._match_tab(stadt)
        scan = [tab_match] if tab_match else list(self.config.primary_tabs)
        results: list[LeadRow] = []
        for tab in scan:
            try:
                for lead in self.iter_tab_rows(tab):
                    if lead.followup_am not in targets:
                        continue
                    if tab_match or lead.stadt.lower() == stadt.lower():
                        results.append(lead)
            except gspread.exceptions.WorksheetNotFound:
                continue
        return results

    def hot_leads(self, today: date, status_column: str = H_VERKAUFSSTATUS) -> list[LeadRow]:
        dead = {"Geantwortet - kein Interesse", "Bounce"}
        results: list[LeadRow] = []
        for tab in self.config.primary_tabs:
            try:
                for lead in self.iter_tab_rows(tab):
                    status_val = _lead_value(lead, status_column)
                    if status_val == "Geantwortet - Interesse":
                        results.append(lead)
                        continue
                    if status_val in dead:
                        continue
                    fu = _parse_date(lead.followup_am)
                    if fu is None or fu < today:
                        continue
                    try:
                        score_val = int(lead.score)
                    except (ValueError, TypeError):
                        score_val = 0
                    if score_val >= 6:
                        results.append(lead)
            except gspread.exceptions.WorksheetNotFound:
                continue
        return results

    # ----- Mutations ----------------------------------------------------------

    def _write_status_for_lead(
        self,
        lead: LeadRow,
        status: str,
        status_column: str,
        when: Optional[date],
        force: bool = False,
    ) -> WriteAttempt:
        """Schreibt Status + ggf. Datum für EINEN LeadRow. Atomar pro Tab via batch_update.

        Verhalten:
        - **Idempotency**: wenn `force=False` und current_status == status und
          ggf. current_date == target_date, wird NICHT geschrieben.
        - **No destructive fallback**: wenn die routing-Datumsspalte
          (z.B. LETZTE_ANTWORT_AM) fehlt, wird KEIN Fallback auf eine andere
          Datumsspalte geschrieben — nur Warning.
        - **APIError-Wrapping**: gspread-Errors landen in WriteAttempt.error,
          KEIN raise. Caller (set_status) entscheidet weiter.
        """
        attempt = WriteAttempt(tab=lead.tab, row_index=lead.row_index, success=False)

        try:
            headers, _ = self._load_tab(lead.tab)
        except SheetsAPIError as e:
            attempt.error = str(e)
            return attempt

        status_col_idx = _find_header(headers, status_column)
        if status_col_idx is None:
            attempt.error = (
                f"Status-Spalte {status_column!r} fehlt in Tab {lead.tab!r}"
            )
            return attempt

        # Datums-Routing
        date_col_idx: Optional[int] = None
        date_target_header: Optional[str] = _date_column_for_status(status)
        date_value_str: Optional[str] = None
        if when is not None and date_target_header:
            date_col_idx = _find_header(headers, date_target_header)
            if date_col_idx is None:
                # KEIN destruktiver Fallback. Warnung — Status-Update geht trotzdem durch.
                attempt.error = None  # nicht-fatal
                # Wir setzen success=True wenn Status durchgeht, plus separate Warning.
                # Aber wir merken uns dass Datum nicht geschrieben werden konnte:
                date_target_header = None
            else:
                date_value_str = when.strftime("%d.%m.%Y")

        # Idempotency-Check (header-aware + format-tolerant)
        # Vergleicht parsed dates, nicht Strings — sonst "11.05.2026" != "2026-05-11"
        # bei mixed-format Sheets und wir schreiben unnötig (N-04).
        current_status = _lead_value(lead, status_column)
        date_already_ok = True
        if date_col_idx is not None and date_value_str is not None:
            current_date_str = _lead_value(lead, date_target_header) if date_target_header else ""
            current_date_obj = _parse_date(current_date_str)
            date_already_ok = (current_date_obj == when)

        if (not force) and current_status == status and date_already_ok:
            attempt.success = True
            attempt.skipped_idempotent = True
            attempt.date_column_written = None
            attempt.date_value_written = None
            return attempt

        # Updates aufbauen
        updates: list[dict] = [{
            "range": f"{_col_letter(status_col_idx)}{lead.row_index}",
            "values": [[status]],
        }]
        if date_col_idx is not None and date_value_str is not None:
            updates.append({
                "range": f"{_col_letter(date_col_idx)}{lead.row_index}",
                "values": [[date_value_str]],
            })
            attempt.date_column_written = date_target_header
            attempt.date_value_written = date_value_str

        # Atomar pro Tab via batch_update
        try:
            ws = self._sh.worksheet(lead.tab)
            ws.batch_update(updates, value_input_option="USER_ENTERED")
            self._invalidate(lead.tab)
            attempt.success = True
        except gspread.exceptions.APIError as e:
            attempt.error = f"batch_update failed: {e}"
            attempt.success = False
        except gspread.exceptions.GSpreadException as e:
            attempt.error = f"gspread error: {e}"
            attempt.success = False
        return attempt

    def set_status(
        self,
        email: str,
        status: str,
        when: Optional[date] = None,
        column: str = H_VERKAUFSSTATUS,
        force: bool = False,
    ) -> SetStatusResult:
        """Setzt `column` (default Verkaufsstatus) für Lead per Email.
        Aggregat-Sync: best-effort. Partial-Failures werden im Result reportet,
        NICHT als Exception bubbled. Caller entscheidet Recovery."""
        warnings: list[str] = []

        # Find primary+secondary. APIError → SheetsAPIError → propagiert hoch.
        primary = self.find_by_email(email)
        try:
            secondary = self.find_in_aggregate(email)
        except SheetsAPIError as e:
            warnings.append(f"Aggregat-Lookup fehlgeschlagen: {e}")
            secondary = None

        result = SetStatusResult(
            primary=primary, secondary=secondary, column_written=column,
            warnings=warnings,
        )

        if primary is None and secondary is None:
            warnings.append(f"Lead {email!r} weder in Primary- noch in Aggregat-Tabs gefunden.")
            return result

        # Inkonsistenz-Warnung VOR Schreibvorgang (header-aware)
        if primary and secondary:
            p_val = _lead_value(primary, column)
            s_val = _lead_value(secondary, column)
            if p_val != s_val:
                warnings.append(
                    f"[INKONSISTENZ] {column}: {primary.tab}={p_val!r} vs "
                    f"{secondary.tab}={s_val!r}. Beide werden auf {status!r} gesetzt."
                )

        # Datums-Routing pre-check für no-destructive-fallback Warnung
        date_target = _date_column_for_status(status)
        if when is not None and date_target:
            for lead in (primary, secondary):
                if lead is None:
                    continue
                headers, _ = self._load_tab(lead.tab)
                if _find_header(headers, date_target) is None:
                    warnings.append(
                        f"[{lead.tab}] {date_target!r}-Spalte fehlt — Datum NICHT "
                        f"geschrieben. Spalte ergänzen, sonst geht das Datum verloren."
                    )

        # Schreiben — beide independent, partial-failure tolerierbar
        for lead in (primary, secondary):
            if lead is None:
                continue
            attempt = self._write_status_for_lead(lead, status, column, when, force=force)
            result.attempts.append(attempt)

        return result
