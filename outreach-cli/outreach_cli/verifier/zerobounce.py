"""ZeroBounce v2 API-Client.

Endpoint: GET https://api.zerobounce.net/v2/validate?api_key=X&email=Y[&ip_address=Z]
Credit-Check: GET https://api.zerobounce.net/v2/getcredits?api_key=X

Free Tier: 100 Verifikationen/Monat. Wir cachen aggressiv (siehe cache.py).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Literal, Optional


# Alle Status-Werte aus ZeroBounce v2 Docs.
# https://www.zerobounce.net/docs/email-validation-api-quickstart/v2-status-codes
VerificationStatus = Literal[
    "valid", "invalid", "catch-all", "unknown",
    "spamtrap", "abuse", "do_not_mail",
]

_API_BASE = "https://api.zerobounce.net/v2"
_HTTP_TIMEOUT = 15.0


class ZeroBounceError(RuntimeError):
    """Generischer API-Fehler (HTTP-Fehler, Connection-Refused, etc.)."""


class ZeroBounceQuotaError(ZeroBounceError):
    """API-Key ungültig oder Free-Quota erschöpft."""


@dataclass(frozen=True)
class ZeroBounceConfig:
    api_key: str

    @classmethod
    def from_env(cls) -> "ZeroBounceConfig":
        key = (os.getenv("ZEROBOUNCE_API_KEY") or "").strip()
        if not key:
            raise SystemExit(
                "FEHLER: ZEROBOUNCE_API_KEY fehlt in .env / Umgebung.\n"
                "Kostenlosen API-Key auf https://www.zerobounce.net/ erstellen (100/Monat free)."
            )
        # Placeholder-Check (analog SMTP_TOKEN)
        upper = key.upper()
        if upper.startswith("REPLACE_") or upper.startswith("YOUR_") or upper == "CHANGE_ME":
            raise SystemExit(
                f"FEHLER: ZEROBOUNCE_API_KEY ist Placeholder ({key!r}). "
                "Echten Key aus dem ZeroBounce-Dashboard eintragen."
            )
        return cls(api_key=key)


@dataclass(frozen=True)
class VerifyResponse:
    """Geparsed JSON-Response des Validate-Endpoints.

    Wir behalten NUR die Felder die wir nutzen — die ZeroBounce-Response ist breit.
    """
    address: str
    status: str  # einer von VerificationStatus
    sub_status: str = ""
    free_email: bool = False
    mx_found: bool = False
    did_you_mean: str = ""
    raw: Optional[dict] = None  # für Audit / Forensik


class ZeroBounceClient:
    def __init__(self, cfg: ZeroBounceConfig):
        self._cfg = cfg

    def get_credits(self) -> int:
        """Wie viele Credits noch übrig. -1 = ungültiger Key (per Doku)."""
        url = f"{_API_BASE}/getcredits?api_key={urllib.parse.quote(self._cfg.api_key)}"
        try:
            with urllib.request.urlopen(url, timeout=_HTTP_TIMEOUT) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as e:
            raise ZeroBounceError(f"Credit-Check fehlgeschlagen: {e}") from e
        credits = int(data.get("Credits", -1))
        if credits == -1:
            raise ZeroBounceQuotaError("API-Key ungültig (Credits=-1).")
        return credits

    def validate(self, email: str, *, ip_address: str = "") -> VerifyResponse:
        """Single-Email-Validation. Fängt HTTP- und Parse-Fehler ab."""
        params = {
            "api_key": self._cfg.api_key,
            "email": email,
            "ip_address": ip_address,
        }
        url = f"{_API_BASE}/validate?{urllib.parse.urlencode(params)}"
        try:
            with urllib.request.urlopen(url, timeout=_HTTP_TIMEOUT) as resp:
                payload = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            # 429 = Rate-Limit (= Quota voll bei Free-Tier)
            if e.code == 429:
                raise ZeroBounceQuotaError(
                    f"ZeroBounce Rate-Limit / Quota voll (HTTP 429) für {email!r}."
                ) from e
            raise ZeroBounceError(
                f"ZeroBounce HTTP {e.code} für {email!r}: {e.reason}"
            ) from e
        except urllib.error.URLError as e:
            raise ZeroBounceError(f"ZeroBounce nicht erreichbar: {e}") from e
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as e:
            raise ZeroBounceError(f"Antwort nicht parsebar: {payload[:200]!r}") from e

        # Spezialfall: API gibt manchmal `error` statt validation-result
        if "error" in data and "status" not in data:
            err = data.get("error") or ""
            if "insufficient credits" in err.lower() or "invalid" in err.lower():
                raise ZeroBounceQuotaError(f"ZeroBounce-Quota/Key-Fehler: {err}")
            raise ZeroBounceError(f"ZeroBounce error: {err}")

        return VerifyResponse(
            address=data.get("address", email),
            status=str(data.get("status", "unknown")).lower(),
            sub_status=str(data.get("sub_status") or "").lower(),
            free_email=bool(data.get("free_email", False)),
            mx_found=bool(data.get("mx_found", False)),
            did_you_mean=str(data.get("did_you_mean") or ""),
            raw=data,
        )
