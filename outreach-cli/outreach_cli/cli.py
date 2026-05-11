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


@app.command()
def send(
    tab: Optional[str] = typer.Option(None, "--tab", help="Sheet-Tab, z.B. Frankfurt_Umland (bei --test-self nicht nötig)"),
    template: str = typer.Option(..., "--template", help="Template-Name ohne .txt"),
    score_min: int = typer.Option(0, "--score-min", help="SCORE >= N"),
    status_filter: Optional[str] = typer.Option(
        None, "--status", help="Recherche_Status-Filter (z.B. 'Neu')"
    ),
    limit: int = typer.Option(0, "--limit", help="Max N Leads (0 = unbegrenzt)"),
    hwg_filter: bool = typer.Option(
        True, "--hwg-filter/--no-hwg-filter",
        help="Heilpraktiker/Arzt-Filter (HWG). Default: AKTIV. Nur deaktivieren mit echtem Grund.",
    ),
    dry_run: bool = typer.Option(
        True, "--dry-run/--no-dry-run",
        help="Dry-Run = nur .eml in preview/ schreiben. --no-dry-run = SMTP (benötigt --test-self ODER --confirm-live).",
    ),
    test_self: bool = typer.Option(
        False, "--test-self",
        help="Sendet GENAU 1 Mail an OWNER_EMAIL (aus .env). Implies --no-dry-run.",
    ),
    confirm_live: bool = typer.Option(
        False, "--confirm-live",
        help="Echter Batch-Versand. Implies --no-dry-run. ACHTUNG: schreibt an echte Leads.",
    ),
    rate_limit: float = typer.Option(
        2.0, "--rate-limit",
        help="Pause in Sekunden zwischen Versanden (Domain-Reputation-Schutz). Default: 2s.",
    ),
    from_email: Optional[str] = typer.Option(
        None, "--from", help="From-Header (default: OWNER_EMAIL aus .env)"
    ),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """Outreach-Mails generieren oder versenden.

    Drei Modi (mutex):
      --dry-run        (default): Generiert .eml in preview/. Kein Netzwerk.
      --test-self      : 1 Mail an OWNER_EMAIL. Verifiziert SMTP-Setup.
      --confirm-live   : Echter Batch-Versand (alle gefilterten Leads).

    Beispiele:
      py -m outreach_cli send --tab Frankfurt_Umland --template variante_c --limit 3
      py -m outreach_cli send --template variante_c --test-self
      py -m outreach_cli send --tab Frankfurt_Umland --template variante_c --score-min 5 --status Neu --limit 20 --confirm-live
    """
    if test_self and confirm_live:
        typer.secho("FEHLER: --test-self und --confirm-live mutex.", fg="red", err=True)
        raise typer.Exit(2)
    if test_self or confirm_live:
        dry_run = False
    if not dry_run and not (test_self or confirm_live):
        typer.secho(
            "FEHLER: --no-dry-run benötigt --test-self ODER --confirm-live "
            "(Schutz gegen versehentlichen Live-Versand).",
            fg="red", err=True,
        )
        raise typer.Exit(2)
    if confirm_live and not tab:
        typer.secho("FEHLER: --confirm-live benötigt --tab.", fg="red", err=True)
        raise typer.Exit(2)
    if dry_run and not tab:
        typer.secho("FEHLER: --dry-run benötigt --tab.", fg="red", err=True)
        raise typer.Exit(2)

    # Lazy imports
    from .commands.send import run_send, SendRunResult
    from .config import SmtpConfig
    from .email.transport import DryRunTransport, MailTransport
    from .email.sender import SmtpTransport
    from .templates.engine import (
        MissingTemplateVariableError,
        TemplateNotFoundError,
        TemplateParseError,
        load_template,
        render,
    )

    # Transport + From wählen
    transport: MailTransport
    actual_from = from_email
    if dry_run:
        from pathlib import Path
        preview = Path(__file__).resolve().parent.parent / "preview"
        transport = DryRunTransport(preview_dir=preview)
        if not actual_from:
            actual_from = "georg@maxcontentseo.de"
        rate_for_run = 0.0  # dry-run braucht kein Rate-Limit
    else:
        try:
            smtp_cfg = SmtpConfig.from_env()
        except SystemExit as e:
            typer.secho(str(e), fg="red", err=True)
            raise typer.Exit(2) from e
        transport = SmtpTransport(smtp_cfg)
        if not actual_from:
            actual_from = smtp_cfg.owner_email
        rate_for_run = rate_limit

    # ----- Test-Self-Sonderpfad -----
    if test_self:
        _run_test_self(
            transport=transport,
            template_name=template,
            from_email=actual_from,
            owner_email=actual_from,
        )
        return

    # ----- Normal-Pfad (Dry-Run oder Confirm-Live) -----
    try:
        result = run_send(
            tab=tab,
            template_name=template,
            transport=transport,
            score_min=score_min,
            status=status_filter,
            limit=limit,
            exclude_hwg=hwg_filter,
            from_email=actual_from,
            rate_limit_seconds=rate_for_run,
        )
    except TemplateNotFoundError as e:
        typer.secho(f"FEHLER: {e}", fg="red", err=True)
        raise typer.Exit(2) from e
    except TemplateParseError as e:
        typer.secho(f"FEHLER (Template-Parse): {e}", fg="red", err=True)
        raise typer.Exit(2) from e
    except (SheetsAPIError, gspread_exceptions_APIError) as e:
        typer.secho(f"API-FEHLER: {e}", fg="red", err=True)
        raise typer.Exit(2) from e

    _render_send_result(
        result, json_out=json_out, hwg_filter=hwg_filter,
        score_min=score_min, status_filter=status_filter, limit=limit,
    )


def _run_test_self(
    *, transport, template_name: str, from_email: str, owner_email: str
) -> None:
    """Sendet GENAU 1 Mail an owner_email mit Test-Lead-Daten."""
    from datetime import datetime as _dt
    import time as _time
    from .templates.engine import load_template, render, MissingTemplateVariableError

    # Hardcoded Test-Lead — User-Spec
    test_vars = {
        "stadt": "Frankfurt",
        "name": "Sehr geehrte/r Test-Empfänger",
        "beispiel_keyword": "Hydrafacial Frankfurt",
        "firma": "Test Studio",
    }

    try:
        tpl = load_template(template_name)
        subject, body = render(tpl, test_vars)
    except MissingTemplateVariableError as e:
        typer.secho(f"FEHLER: Template-Render fehlgeschlagen: {e}", fg="red", err=True)
        raise typer.Exit(2) from e

    # Subject mit [TEST-SELF] Präfix damit man die Mail im Posteingang erkennt
    subject = f"[TEST-SELF] {subject}"

    typer.secho(
        f"TEST-SELF: 1 Mail an {owner_email} via {transport.name()}",
        fg="cyan",
    )
    typer.echo(f"  Subject:  {subject}")
    typer.echo(f"  Template: {template_name}")
    typer.echo(f"  Body-Vars: {test_vars}")
    typer.echo("  Sende...")

    result = transport.deliver(
        index=0,
        to_email=owner_email,
        from_email=from_email,
        subject=subject,
        body=body,
    )

    if not result.delivered:
        typer.secho(f"FAIL: {result.error}", fg="red", err=True)
        raise typer.Exit(2)

    # 10s warten (User-Spec) — Mail Server-Side delivery-window
    typer.echo(f"  [OK] gesendet um {result.delivered_at.strftime('%H:%M:%S')}")
    typer.echo(f"  SMTP-Response: {result.smtp_response}")
    typer.echo(f"  Retries:       {result.retry_count}")
    typer.echo("  Warte 10s auf Server-Side-Delivery...")
    _time.sleep(10)
    typer.secho(
        f"  ✓ Test-Self abgeschlossen. Bitte ProtonMail-Postfach prüfen "
        f"({_dt.now().strftime('%H:%M:%S')}).",
        fg="green",
    )


def _render_send_result(
    result, *, json_out: bool, hwg_filter: bool,
    score_min: int, status_filter: Optional[str], limit: int,
) -> None:
    s = result.stats
    if json_out:
        _emit_json({
            "tab": result.tab,
            "template": result.template_name,
            "transport": result.transport_name,
            "preview_dir": str(result.preview_dir) if result.preview_dir else None,
            "stats": {
                "total_in_tab": s.total_in_tab,
                "after_score": s.after_score,
                "after_status": s.after_status,
                "after_hwg": s.after_hwg,
                "after_limit": s.after_limit,
                "hwg_excluded": s.hwg_excluded,
                "skipped_no_render_vars": s.skipped_no_render_vars,
            },
            "delivered": [
                {
                    "to": d.to_email, "subject": d.subject,
                    "path": str(d.path) if d.path else None,
                    "smtp_response": d.smtp_response,
                    "retry_count": d.retry_count,
                } for d in result.delivered
            ],
            "failed": [
                {"to": d.to_email, "error": d.error, "retries": d.retry_count}
                for d in result.failed
            ],
            "render_errors": [
                {"email": e, "error": msg}
                for e, msg in result.skipped_render_errors
            ],
        })
        if result.failed:
            raise typer.Exit(2)
        raise typer.Exit(0)

    label = result.transport_name.upper()
    typer.secho(f"{label}: {result.tab} → {result.template_name}", fg="cyan")
    typer.echo(f"  Total im Tab:       {s.total_in_tab}")
    if score_min > 0:
        typer.echo(f"  Nach Score >= {score_min}:    {s.after_score}")
    if status_filter:
        typer.echo(f"  Nach Status='{status_filter}':  {s.after_status}")
    if hwg_filter:
        typer.echo(f"  Nach HWG-Filter:    {s.after_hwg}")
        if s.hwg_excluded:
            typer.secho(f"  HWG-ausgeschlossen ({len(s.hwg_excluded)}):", fg="yellow")
            for x in s.hwg_excluded:
                typer.echo(f"    - {x}")
    if limit > 0:
        typer.echo(f"  Nach Limit={limit}:       {s.after_limit}")
    if s.skipped_no_render_vars:
        typer.secho(
            f"  Skip (keine Render-Vars, {len(s.skipped_no_render_vars)}):", fg="yellow",
        )
        for x in s.skipped_no_render_vars:
            typer.echo(f"    - {x}")

    if result.preview_dir:
        typer.echo(f"\n  Preview-Dir:  {result.preview_dir}")
    typer.secho(f"  Delivered: {len(result.delivered)}", fg="green")
    for d in result.delivered:
        path_or_smtp = (
            d.path.name if d.path else f"smtp:{(d.smtp_response or '')[:40]}"
        )
        typer.echo(f"    • {path_or_smtp}  ←  {d.to_email}  ({d.subject!r})")

    if result.failed:
        typer.secho(f"\n  Failed ({len(result.failed)}):", fg="red")
        for d in result.failed:
            typer.echo(f"    ❌ {d.to_email}: {d.error} (nach {d.retry_count} retries)")

    if result.skipped_render_errors:
        typer.secho(
            f"\n  Render-Fehler ({len(result.skipped_render_errors)}):",
            fg="red",
        )
        for em, msg in result.skipped_render_errors:
            typer.echo(f"    ❌ {em}: {msg}")

    if result.failed:
        raise typer.Exit(2)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
