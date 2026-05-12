"""NeverBounce v4 API-Client (Primary, ZeroBounce ist Fallback).

Endpoint: GET https://api.neverbounce.com/v4/single/check?email=X&api_key=Y

Free Tier: 1000 Verifikationen/Monat (10× besser als ZeroBounce-Trial).
Status-Werte: valid / invalid / catchall / unknown / disposable

Mapping zu unseren Buckets (gleich wie ZB):
  valid                                  → SEND
  catchall                               → SEND_WITH_WARN
  invalid / unknown / disposable         → SKIP + Sheet "Email-Ungültig"
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Optional


_API_BASE = "https://api.neverbounce.com/v4"
_HTTP_TIMEOUT = 15.0


class NeverBounceError(RuntimeError):
    """Generischer API-Fehler."""


class NeverBounceQuotaError(NeverBounceError):
    """API-Key ungültig oder Quota erschöpft."""


@dataclass(frozen=True)
class NeverBounceConfig:
    api_key: str

    @classmethod
    def from_env(cls) -> "NeverBounceConfig":
        key = (os.getenv("NEVERBOUNCE_API_KEY") or "").strip()
        if not key:
            raise SystemExit(
                "FEHLER: NEVERBOUNCE_API_KEY fehlt in .env / Umgebung.\n"
                "Kostenlosen API-Key auf https://app.neverbounce.com/ erstellen "
                "(1000/Monat free)."
            )
        upper = key.upper()
        if upper.startswith("REPLACE_") or upper.startswith("YOUR_") or upper == "CHANGE_ME":
            raise SystemExit(
                f"FEHLER: NEVERBOUNCE_API_KEY ist Placeholder ({key!r}). "
                "Echten Key aus dem NeverBounce-Dashboard eintragen."
            )
        return cls(api_key=key)


@dataclass(frozen=True)
class VerifyResponse:
    """Normalisierter Response — kompatibel zur ZeroBounce-VerifyResponse-Shape.

    `status` ist auf unsere kanonische Form normalisiert:
      - NeverBounce "catchall" → wir mappen direkt; das Pipeline-Bucketing kennt
        beide Forms ("catchall" UND "catch-all") seit dem Multi-Provider-Refactor.
    """
    address: str
    status: str  # NB-Roh: valid/invalid/catchall/unknown/disposable
    sub_status: str = ""
    free_email: bool = False
    mx_found: bool = False
    did_you_mean: str = ""
    raw: Optional[dict] = None
    provider: str = "neverbounce"


class NeverBounceClient:
    def __init__(self, cfg: NeverBounceConfig):
        self._cfg = cfg

    def validate(self, email: str, *, ip_address: str = "") -> VerifyResponse:
        """Single-Email-Validation via /v4/single/check."""
        params = {
            "key": self._cfg.api_key,  # NeverBounce nutzt `key`, nicht `api_key`
            "email": email,
        }
        url = f"{_API_BASE}/single/check?{urllib.parse.urlencode(params)}"
        try:
            with urllib.request.urlopen(url, timeout=_HTTP_TIMEOUT) as resp:
                payload = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            # 402 Payment Required = Free-Quota erschöpft bei NeverBounce
            # 429 Too Many Requests = Rate-Limit (Trial-Account)
            if e.code in (402, 429):
                raise NeverBounceQuotaError(
                    f"NeverBounce Quota/Rate-Limit (HTTP {e.code}) für {email!r}."
                ) from e
            raise NeverBounceError(
                f"NeverBounce HTTP {e.code} für {email!r}: {e.reason}"
            ) from e
        except urllib.error.URLError as e:
            raise NeverBounceError(f"NeverBounce nicht erreichbar: {e}") from e
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as e:
            raise NeverBounceError(f"Antwort nicht parsebar: {payload[:200]!r}") from e

        # NB-Response-Struktur:
        # { "status": "success", "result": "valid", "flags": [...], "execution_time": 123 }
        # ODER bei API-Fehler:
        # { "status": "auth_failure", "message": "...", "execution_time": 0 }
        api_status = str(data.get("status", "")).lower()
        if api_status == "success":
            result = str(data.get("result", "unknown")).lower()
            flags = data.get("flags") or []
            # Sub-Status aus Flags: NB nutzt 'role_account', 'disposable', 'free_email_host' etc.
            # Wir bauen sub_status für Kompatibilität mit ZB-Bucketing-Logic (role_based-Relax).
            sub_status = ""
            if "role_account" in flags:
                sub_status = "role_based"
            elif "disposable" in flags:
                sub_status = "disposable"
            free_email = "free_email_host" in flags
            return VerifyResponse(
                address=email,
                status=result,  # valid/invalid/catchall/unknown/disposable
                sub_status=sub_status,
                free_email=free_email,
                mx_found=("has_dns" in flags),
                did_you_mean=str(data.get("suggested_correction") or ""),
                raw=data,
            )

        # API-Fehler-Pfad
        msg = str(data.get("message") or "") or api_status
        if "auth" in api_status or "invalid_api_key" in msg.lower():
            raise NeverBounceQuotaError(f"NeverBounce auth_failure: {msg}")
        if "throttle" in api_status.lower() or "rate" in msg.lower():
            raise NeverBounceQuotaError(f"NeverBounce rate-limit: {msg}")
        raise NeverBounceError(f"NeverBounce error ({api_status}): {msg}")
