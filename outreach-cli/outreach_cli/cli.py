"""Typer-CLI für outreach-cli."""

from __future__ import annotations

import json
import sys
from datetime import date, datetime
from typing import Optional

import gspread.exceptions as gspread_exceptions
import typer
from rich.console import Console
from rich.table import Table

from .config import (
    ALLOWED_STATUSES,
    DEFAULT_STATUS_COLUMN,
    H_RECHERCHE_STATUS,
    H_VERKAUFSSTATUS,
    Config,
)
from .sheets import LeadRow, SetStatusResult, SheetClient, SheetsAPIError

gspread_exceptions_APIError = gspread_exceptions.APIError

# Stdout auf UTF-8 zwingen (Windows-Konsole sonst gerne cp1252).
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="outreach-cli — kompakter Zugriff auf den Lead-Tracker.",
)
console = Console()

VALID_COLUMNS = (H_VERKAUFSSTATUS, H_RECHERCHE_STATUS)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _client() -> SheetClient:
    return SheetClient(Config.from_env())


def _parse_iso(date_str: Optional[str]) -> date:
    if not date_str:
        return date.today()
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError as e:
        typer.secho(
            f"FEHLER: Datum muss YYYY-MM-DD sein, nicht '{date_str}'.",
            fg="red", err=True,
        )
        raise typer.Exit(2) from e


def _lead_compact(lead: LeadRow) -> dict:
    return {
        "_row_index": lead.row_index,
        "_tab": lead.tab,
        "firma": lead.firma,
        "stadt": lead.stadt,
        "email": lead.email,
        "score": lead.score,
        "recherche_status": lead.recherche_status,
        "verkaufsstatus": lead.verkaufsstatus,
        "kontaktiert_am": lead.kontaktiert_am,
        "followup_am": lead.followup_am,
        "letzte_antwort_am": lead.data.get("LETZTE_ANTWORT_AM", "").strip(),
        "seo_problem": lead.seo_problem,
    }


def _emit_json(payload) -> None:
    typer.echo(json.dumps(payload, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

@app.command()
def followups(
    stadt: str = typer.Option(..., "--stadt", help="z.B. Frankfurt, Hamburg, Bad Homburg"),
    date_: Optional[str] = typer.Option(None, "--date", help="YYYY-MM-DD (Default: heute)"),
    json_out: bool = typer.Option(False, "--json", help="JSON statt Tabelle"),
) -> None:
    """Listet Leads mit FOLLOWUP_AM = heute (oder --date) für die Stadt."""
    target = _parse_iso(date_)
    try:
        leads = _client().followups_on(stadt, target)
    except Exception as e:
        typer.secho(f"API-FEHLER: {e}", fg="red", err=True)
        raise typer.Exit(2) from e

    if json_out:
        _emit_json([_lead_compact(l) for l in leads])
        raise typer.Exit(0)

    if not leads:
        typer.echo(f"Keine Followups für {stadt} am {target.strftime('%d.%m.%Y')}.")
        raise typer.Exit(0)

    table = Table(title=f"Followups {stadt} — {target.strftime('%d.%m.%Y')}")
    table.add_column("FIRMA", style="cyan", no_wrap=True)
    table.add_column("EMAIL")
    table.add_column("SCORE", justify="right")
    table.add_column("SEO_Problem", style="dim")
    for l in leads:
        table.add_row(l.firma, l.email, l.score, l.seo_problem)
    console.print(table)


@app.command()
def status(
    email: str = typer.Option(..., "--email"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """Zeigt aktuellen Status eines Leads. Sucht primary (Stadt-Tab) UND
    Aggregat (Alle_Leads), zeigt beide wenn vorhanden."""
    try:
        client = _client()
        primary = client.find_by_email(email)
        secondary = client.find_in_aggregate(email)
    except Exception as e:
        typer.secho(f"API-FEHLER: {e}", fg="red", err=True)
        raise typer.Exit(2) from e

    if primary is None and secondary is None:
        typer.secho(f"Lead nicht gefunden: {email}", fg="yellow", err=True)
        raise typer.Exit(1)

    if json_out:
        payload = {
            "primary": _lead_compact(primary) if primary else None,
            "secondary": _lead_compact(secondary) if secondary else None,
        }
        _emit_json(payload)
        raise typer.Exit(0)

    def render(lead: LeadRow, label: str) -> None:
        table = Table(title=f"{label} — {lead.tab} Zeile {lead.row_index}", show_header=False, box=None)
        table.add_column("Feld", style="bold")
        table.add_column("Wert")
        for f, v in (
            ("FIRMA", lead.firma),
            ("STADT", lead.stadt),
            ("EMAIL", lead.email),
            ("SCORE", lead.score),
            ("Recherche_Status", lead.recherche_status),
            ("Verkaufsstatus", lead.verkaufsstatus),
            ("KONTAKTIERT_AM", lead.kontaktiert_am),
            ("FOLLOWUP_AM", lead.followup_am),
            ("LETZTE_ANTWORT_AM", lead.data.get("LETZTE_ANTWORT_AM", "").strip()),
            ("SEO_Problem", lead.seo_problem),
        ):
            table.add_row(f, v)
        console.print(table)

    if primary:
        render(primary, "PRIMARY")
    if secondary:
        render(secondary, "SECONDARY (Aggregat)")

    # Inkonsistenz-Hinweis
    if primary and secondary:
        for col, label in (("Recherche_Status", "Recherche_Status"), ("Verkaufsstatus", "Verkaufsstatus")):
            p = primary.data.get(col, "").strip()
            s = secondary.data.get(col, "").strip()
            if p != s:
                typer.secho(
                    f"⚠ INKONSISTENZ {label}: primary={p!r}, secondary={s!r}",
                    fg="yellow",
                )


@app.command("set-status")
def set_status_cmd(
    email: str = typer.Option(..., "--email"),
    status_: str = typer.Option(..., "--status"),
    column: str = typer.Option(
        DEFAULT_STATUS_COLUMN,
        "--column",
        help=f"Welche Spalte schreiben? Default: {DEFAULT_STATUS_COLUMN}. "
             f"Erlaubt: {', '.join(VALID_COLUMNS)}.",
    ),
    date_: Optional[str] = typer.Option(
        None, "--date",
        help="YYYY-MM-DD (Default: heute). Wird nur geschrieben wenn Status eine Datumsspalte hat.",
    ),
    force: bool = typer.Option(
        False, "--force",
        help="Schreibt auch wenn Status+Datum bereits den Ziel-Werten entsprechen.",
    ),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """Setzt Status + ggf. Datumsspalte. Schreibt in Stadt-Tab UND Alle_Leads
    (Aggregat-Sync, best-effort). Default-Spalte: Verkaufsstatus.

    Exit-Codes: 0=alle OK, 1=Lead nicht gefunden, 2=API-/Validierungs-Fehler,
    3=Partial-Failure (Tabs nun inkonsistent — manuelles Recovery nötig)."""
    if status_ not in ALLOWED_STATUSES:
        typer.secho(
            f"FEHLER: Status '{status_}' nicht erlaubt.\nErlaubt: {', '.join(ALLOWED_STATUSES)}",
            fg="red", err=True,
        )
        raise typer.Exit(2)

    if column not in VALID_COLUMNS:
        typer.secho(
            f"FEHLER: --column '{column}' nicht erlaubt. Erlaubt: {', '.join(VALID_COLUMNS)}",
            fg="red", err=True,
        )
        raise typer.Exit(2)

    when = _parse_iso(date_)

    try:
        result: SetStatusResult = _client().set_status(
            email, status_, when=when, column=column, force=force,
        )
    except SystemExit:
        raise
    except (SheetsAPIError, gspread_exceptions_APIError) as e:
        typer.secho(f"API-FEHLER: {e}", fg="red", err=True)
        raise typer.Exit(2) from e

    if result.primary is None and result.secondary is None:
        for w in result.warnings:
            typer.secho(f"  {w}", fg="yellow", err=True)
        raise typer.Exit(1)

    # Aggregierte Datums-Info aus erstem erfolgreichen Attempt
    date_col = next((a.date_column_written for a in result.attempts
                     if a.success and a.date_column_written), None)
    date_val = next((a.date_value_written for a in result.attempts
                     if a.success and a.date_value_written), None)

    if json_out:
        _emit_json({
            "column": result.column_written,
            "date_column": date_col,
            "date_value": date_val,
            "primary": _lead_compact(result.primary) if result.primary else None,
            "secondary": _lead_compact(result.secondary) if result.secondary else None,
            "attempts": [
                {
                    "tab": a.tab, "row": a.row_index,
                    "success": a.success, "skipped_idempotent": a.skipped_idempotent,
                    "date_column": a.date_column_written, "date_value": a.date_value_written,
                    "error": a.error,
                } for a in result.attempts
            ],
            "writes_succeeded": result.writes_succeeded,
            "writes_skipped": result.writes_skipped,
            "writes_failed": result.writes_failed,
            "partial_failure": result.partial_failure,
            "total_failure": result.total_failure,
            "warnings": result.warnings,
        })
        # Exit-Code-Routing identisch zum tabular Modus
        if result.total_failure:
            raise typer.Exit(2)
        if result.partial_failure:
            raise typer.Exit(3)
        raise typer.Exit(0)

    # Tabular output
    if result.total_failure:
        typer.secho(f"FAIL: alle Schreibvorgänge gescheitert für {column}", fg="red")
    elif result.partial_failure:
        typer.secho(f"PARTIAL: {column} → {status_!r} (Tabs nun inkonsistent)", fg="yellow")
    elif result.writes_succeeded == 0 and result.writes_skipped > 0:
        typer.secho(f"NOOP: {column} bereits {status_!r} (kein Write nötig, --force zum Erzwingen)", fg="cyan")
    else:
        typer.secho(f"OK: {column} → {status_!r}", fg="green")

    for a in result.attempts:
        marker = "OK" if a.success and not a.skipped_idempotent else (
            "SKIP" if a.skipped_idempotent else "FAIL")
        typer.echo(f"  [{marker}] {a.tab} Z.{a.row_index}"
                   + (f" — {a.error}" if a.error else ""))
    if date_col and date_val:
        typer.echo(f"  DATUM     {date_col} = {date_val}")
    for w in result.warnings:
        typer.secho(f"  ! {w}", fg="yellow")

    if result.total_failure:
        raise typer.Exit(2)
    if result.partial_failure:
        raise typer.Exit(3)


@app.command()
def hot(
    column: str = typer.Option(
        DEFAULT_STATUS_COLUMN,
        "--column",
        help=f"Status-Spalte für Hot-Definition. Default: {DEFAULT_STATUS_COLUMN}.",
    ),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """Hot Leads: '{Spalte} = Geantwortet - Interesse' ODER
    (FOLLOWUP_AM >= heute UND SCORE >= 6 UND nicht tot)."""
    if column not in VALID_COLUMNS:
        typer.secho(
            f"FEHLER: --column '{column}' nicht erlaubt. Erlaubt: {', '.join(VALID_COLUMNS)}",
            fg="red", err=True,
        )
        raise typer.Exit(2)

    try:
        leads = _client().hot_leads(date.today(), status_column=column)
    except Exception as e:
        typer.secho(f"API-FEHLER: {e}", fg="red", err=True)
        raise typer.Exit(2) from e

    if json_out:
        _emit_json([_lead_compact(l) for l in leads])
        raise typer.Exit(0)

    if not leads:
        typer.echo(f"Keine Hot Leads ({column}).")
        raise typer.Exit(0)

    table = Table(title=f"Hot Leads ({column}) — {date.today().strftime('%d.%m.%Y')}")
    table.add_column("STADT")
    table.add_column("FIRMA", style="cyan", no_wrap=True)
    table.add_column("EMAIL")
    table.add_column("SCORE", justify="right")
    table.add_column(column)
    table.add_column("FOLLOWUP_AM")
    for l in leads:
        table.add_row(
            l.stadt, l.firma, l.email, l.score,
            l.data.get(column, "").strip(), l.followup_am,
        )
    console.print(table)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
