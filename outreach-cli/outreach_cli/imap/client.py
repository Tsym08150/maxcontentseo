"""ProtonMail-Bridge IMAP-Client.

Bridge-Konvention (gilt für Default-Install):
- Host: 127.0.0.1
- Port: 1143 (NICHT 993)
- Security: STARTTLS (Bridge schickt self-signed cert)
- Username: die in Bridge konfigurierte E-Mail-Adresse (z.B. georg@maxcontentseo.de)
- Password: Bridge-generiertes Token (NICHT das ProtonMail-Login-Password)

Wir verwenden Python's `imaplib.IMAP4` + manuelles STARTTLS mit
unverified SSL-Context (Bridge nutzt always self-signed certs).
"""

from __future__ import annotations

import imaplib
import ssl
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, Optional


class ImapConnectError(RuntimeError):
    """Bridge nicht erreichbar (Service nicht gestartet o.ä.)."""


class ImapAuthError(RuntimeError):
    """LOGIN abgelehnt — falscher User/Token, oder Bridge weiß diese Adresse nicht."""


@dataclass(frozen=True)
class ImapConfig:
    host: str
    port: int
    user: str
    password: str  # NIE loggen

    @classmethod
    def from_env(cls) -> "ImapConfig":
        """Liest aus .env / OS-Env mit Fallback-Kette:
        - User: PROTON_IMAP_USER → SMTP_USER → georg@maxcontentseo.de
        - Pass: PROTONMAIL_BRIDGE_PASSWORD → PROTON_IMAP_PASSWORD → SMTP_TOKEN
        - Host: IMAP_HOST → 127.0.0.1
        - Port: IMAP_PORT → 1143 (Bridge default)
        """
        import os
        host = (os.getenv("IMAP_HOST") or "127.0.0.1").strip()
        port_raw = (os.getenv("IMAP_PORT") or "1143").strip()
        user = (
            os.getenv("PROTON_IMAP_USER")
            or os.getenv("SMTP_USER")
            or "georg@maxcontentseo.de"
        ).strip()
        password = (
            os.getenv("PROTONMAIL_BRIDGE_PASSWORD")
            or os.getenv("PROTON_IMAP_PASSWORD")
            or os.getenv("SMTP_TOKEN")
            or ""
        ).strip()
        if not password:
            raise SystemExit(
                "FEHLER: Bridge-IMAP-Password fehlt. Setze einen davon in .env "
                "ODER als System-Env-Var:\n"
                "  PROTONMAIL_BRIDGE_PASSWORD  (empfohlen)\n"
                "  PROTON_IMAP_PASSWORD\n"
                "  SMTP_TOKEN (fallback)\n"
                "Tipp: Bridge GUI → Mailbox-Settings → Password kopieren."
            )
        try:
            port = int(port_raw)
        except ValueError:
            raise SystemExit(f"FEHLER: IMAP_PORT muss Zahl sein, ist {port_raw!r}")
        return cls(host=host, port=port, user=user, password=password)


class BridgeImapClient:
    """Dünner Wrapper um imaplib für ProtonMail Bridge.

    Verwendung:
        cfg = ImapConfig.from_env()
        with BridgeImapClient(cfg) as cli:
            uids = cli.search_bounces(since_days=2)
            for uid in uids:
                raw = cli.fetch_raw(uid)
                # parse mit parser.parse_bounce(raw)
    """

    def __init__(self, cfg: ImapConfig):
        self._cfg = cfg
        self._conn: Optional[imaplib.IMAP4] = None

    def __enter__(self) -> "BridgeImapClient":
        self._connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _connect(self) -> None:
        """Connect mit STARTTLS, self-signed cert akzeptieren."""
        try:
            conn = imaplib.IMAP4(self._cfg.host, self._cfg.port)
        except OSError as e:
            raise ImapConnectError(
                f"Bridge IMAP nicht erreichbar auf {self._cfg.host}:{self._cfg.port}. "
                f"Läuft Bridge? ({e})"
            ) from e

        # STARTTLS mit self-signed cert
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            conn.starttls(ctx)
        except Exception as e:
            raise ImapConnectError(f"STARTTLS gescheitert: {e}") from e

        try:
            conn.login(self._cfg.user, self._cfg.password)
        except imaplib.IMAP4.error as e:
            msg = str(e)
            hint = ""
            if "no such user" in msg.lower():
                hint = (
                    f"\n\nBridge sagt 'no such user' für {self._cfg.user!r}.\n"
                    "Mögliche Ursachen:\n"
                    "  1. PROTON_IMAP_USER stimmt nicht mit der in Bridge konfigurierten Adresse überein.\n"
                    "     → Bridge GUI öffnen, exakte Adresse als PROTON_IMAP_USER in .env eintragen.\n"
                    "  2. Bridge wurde restartet aber Account neu verbunden — Token könnte rotiert sein.\n"
                    "     → Neues Mailbox-Password aus Bridge GUI kopieren."
                )
            raise ImapAuthError(f"LOGIN gescheitert: {msg}{hint}") from e

        self._conn = conn

    def close(self) -> None:
        if self._conn:
            try:
                self._conn.logout()
            except Exception:
                pass
            self._conn = None

    def _require(self) -> imaplib.IMAP4:
        if not self._conn:
            raise RuntimeError("IMAP not connected — use as context manager")
        return self._conn

    def search_bounces(self, since_days: int = 2) -> list[bytes]:
        """Suche Bounce-Mails im INBOX seit `since_days` Tagen.

        Kombiniert 4 IMAP-SEARCH-Kriterien (OR semantisch via Set-Union):
        - FROM mailer-daemon
        - FROM postmaster
        - SUBJECT "Undelivered"
        - SUBJECT "Delayed Mail"

        Returns UID-Liste (bytes, da imaplib so antwortet).
        """
        conn = self._require()
        typ, _ = conn.select("INBOX", readonly=True)
        if typ != "OK":
            raise RuntimeError("SELECT INBOX failed")

        # IMAP-Datum für SINCE — Format: DD-Mon-YYYY (z.B. 10-May-2026)
        from datetime import timedelta
        since_date = (datetime.now() - timedelta(days=since_days)).strftime("%d-%b-%Y")

        criteria = [
            f'(SINCE {since_date} FROM "mailer-daemon")',
            f'(SINCE {since_date} FROM "postmaster")',
            f'(SINCE {since_date} SUBJECT "Undelivered")',
            f'(SINCE {since_date} SUBJECT "Delayed Mail")',
        ]

        all_uids: set[bytes] = set()
        for crit in criteria:
            typ, data = conn.uid("SEARCH", None, crit)
            if typ == "OK" and data and data[0]:
                for uid in data[0].split():
                    all_uids.add(uid)
        return sorted(all_uids, key=lambda u: int(u))

    def fetch_raw(self, uid: bytes) -> bytes:
        """Hole die RAW-Message (RFC 822) per UID."""
        conn = self._require()
        typ, data = conn.uid("FETCH", uid, "(RFC822)")
        if typ != "OK" or not data:
            raise RuntimeError(f"FETCH UID {uid!r} failed")
        # data is list of tuples like [(b'1 (RFC822 {12345}', b'<body bytes>'), b')']
        for item in data:
            if isinstance(item, tuple) and len(item) >= 2:
                return item[1]
        raise RuntimeError(f"FETCH UID {uid!r}: kein Body in Response")


@contextmanager
def imap_session(cfg: Optional[ImapConfig] = None) -> Iterator[BridgeImapClient]:
    """Convenience-Context: ImapConfig.from_env() + BridgeImapClient."""
    if cfg is None:
        cfg = ImapConfig.from_env()
    with BridgeImapClient(cfg) as cli:
        yield cli
