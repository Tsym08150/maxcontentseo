"""Konfigurations- und Konstanten-Layer für outreach-cli."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# .env liegt im Projekt-Root (ein Level über diesem Paket).
_DOTENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_DOTENV_PATH)


# ---------------------------------------------------------------------------
# Status-Whitelist — gilt für beide Spalten (Recherche_Status / Verkaufsstatus).
# ---------------------------------------------------------------------------
ALLOWED_STATUSES: tuple[str, ...] = (
    "Angeschrieben",
    "Follow-up gesendet",
    "Geantwortet - kein Interesse",
    "Geantwortet - Interesse",
    "Bounce",
    "Email-Ungültig",
    "Nicht kontaktiert",
    "DNC",
)

# Stati die einen Lead HART vom Versand ausschliessen — unabhaengig vom
# positiven Status-Filter in load_filtered_leads. Endzustaende + manuelle Sperre.
EXCLUDED_SEND_STATUSES: frozenset[str] = frozenset({
    "DNC",
    "Bounce",
    "Geantwortet - kein Interesse",
})

# ---------------------------------------------------------------------------
# Standard-Header-Namen. Echte Sheet-Header werden via HEADER_ALIASES gematcht.
# ---------------------------------------------------------------------------
H_FIRMA = "FIRMA"
H_STADT = "STADT"
H_EMAIL = "EMAIL"
H_SCORE = "SCORE"
H_RECHERCHE_STATUS = "Recherche_Status"
H_VERKAUFSSTATUS = "Verkaufsstatus"
H_KONTAKTIERT = "KONTAKTIERT_AM"
H_FOLLOWUP = "FOLLOWUP_AM"
H_ANTWORT = "LETZTE_ANTWORT_AM"
H_SEO_PROBLEM = "SEO_Problem"

# Default-Statusspalte für set-status. Kann via --column überschrieben werden.
DEFAULT_STATUS_COLUMN = H_VERKAUFSSTATUS

# Alias-Map: Standard-Header → Liste alternativer Schreibweisen, die im Sheet
# vorkommen können. _find_header probiert zuerst exact-match, dann Aliase.
# Lower-cased, da Lookup case-insensitive ist.
HEADER_ALIASES: dict[str, tuple[str, ...]] = {
    H_FIRMA: (".",),                          # Alt-Frankfurt
    H_STADT: ("Stadt",),                      # Alle_Leads, Frankfurt_Umland
    H_KONTAKTIERT: ("KONTAKTIERT", "KONTAKTIERT AM", "Kontaktiert"),  # Alt-Muenchen
    H_FOLLOWUP: ("FOLLOW-UP", "FOLLOW_UP", "FOLLOWUP"),               # Alt-Muenchen
}


# ---------------------------------------------------------------------------
# Tab-Klassifikation
# ---------------------------------------------------------------------------
# Primary = wo Leads "leben" (Stadt-Tabs). find_by_email scant zuerst diese.
# Aggregate = Schatten-Tabs die parallel gepflegt werden (Alle_Leads als Master).
# set_status updated immer in beiden, wenn der Lead in beiden steht.
DEFAULT_PRIMARY_TABS = ("Muenchen", "Hamburg", "Frankfurt", "Frankfurt_Umland", "Bad Homburg")
DEFAULT_AGGREGATE_TABS = ("Alle_Leads",)


@dataclass(frozen=True)
class Config:
    sheet_id: str
    credentials_path: Path
    primary_tabs: tuple[str, ...]
    aggregate_tabs: tuple[str, ...]

    @property
    def tabs(self) -> tuple[str, ...]:
        """Alle Tabs (primary + aggregate). Reihenfolge: primary zuerst,
        weil find_by_email-Suche so beim Stadt-Tab landet, nicht beim Aggregat."""
        return self.primary_tabs + self.aggregate_tabs

    @classmethod
    def from_env(cls) -> "Config":
        sheet_id = (os.getenv("SHEET_ID") or "").strip()
        creds = (os.getenv("GOOGLE_CREDENTIALS_PATH") or "").strip()

        primary_raw = os.getenv("PRIMARY_TABS")
        aggregate_raw = os.getenv("AGGREGATE_TABS")

        # Backward-compat: alte TABS-Variable als primary_tabs interpretieren
        if not primary_raw:
            primary_raw = os.getenv("TABS") or ",".join(DEFAULT_PRIMARY_TABS)
        if not aggregate_raw:
            aggregate_raw = ",".join(DEFAULT_AGGREGATE_TABS)

        if not sheet_id:
            raise SystemExit("FEHLER: SHEET_ID fehlt in .env")
        if not creds:
            raise SystemExit("FEHLER: GOOGLE_CREDENTIALS_PATH fehlt in .env")

        creds_path = Path(creds)
        if not creds_path.exists():
            raise SystemExit(f"FEHLER: Credentials-Datei nicht gefunden: {creds_path}")

        primary = tuple(t.strip() for t in primary_raw.split(",") if t.strip())
        aggregate = tuple(t.strip() for t in aggregate_raw.split(",") if t.strip())
        if not primary:
            raise SystemExit("FEHLER: PRIMARY_TABS in .env ist leer.")

        return cls(
            sheet_id=sheet_id,
            credentials_path=creds_path,
            primary_tabs=primary,
            aggregate_tabs=aggregate,
        )


@dataclass(frozen=True)
class SmtpConfig:
    """SMTP-Config für outreach send Phase 2. Aus .env."""
    host: str
    port: int
    user: str
    token: str  # App-Password — NIE loggen
    owner_email: str  # Default-From, Test-Self-Empfänger

    @classmethod
    def from_env(cls) -> "SmtpConfig":
        host = (os.getenv("SMTP_HOST") or "").strip()
        port_raw = (os.getenv("SMTP_PORT") or "").strip()
        user = (os.getenv("SMTP_USER") or "").strip()
        token = (os.getenv("SMTP_TOKEN") or "").strip()
        owner = (os.getenv("OWNER_EMAIL") or user).strip()

        missing = []
        if not host:
            missing.append("SMTP_HOST")
        if not port_raw:
            missing.append("SMTP_PORT")
        if not user:
            missing.append("SMTP_USER")
        if not token:
            missing.append("SMTP_TOKEN")
        if missing:
            raise SystemExit(
                f"FEHLER: SMTP-Config unvollständig — fehlend in .env: "
                f"{', '.join(missing)}"
            )
        # Placeholder-Check: User hat .env.example kopiert ohne zu editieren?
        # Match alle gängigen Placeholder-Patterns (case-insensitive).
        upper = token.upper()
        if upper.startswith("REPLACE_") or upper.startswith("YOUR_") or upper == "CHANGE_ME":
            raise SystemExit(
                f"FEHLER: SMTP_TOKEN ist noch ein Placeholder ({token!r}). "
                f"Echtes App-Password aus ProtonMail eintragen."
            )
        try:
            port = int(port_raw)
        except ValueError:
            raise SystemExit(f"FEHLER: SMTP_PORT muss Zahl sein, ist {port_raw!r}")
        return cls(
            host=host, port=port, user=user, token=token, owner_email=owner,
        )
