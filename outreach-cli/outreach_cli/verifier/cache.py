"""JSON-File-Cache für ZeroBounce-Verifikationen mit TTL.

Format `cache/verified-emails.json`:
{
  "schema": 1,
  "entries": {
    "info@example.de": {
      "status": "valid",
      "sub_status": "alias_address",
      "verified_at": "2026-05-12T15:30:00+00:00",
      "did_you_mean": "",
      "free_email": false
    },
    ...
  }
}

Default-TTL: 30 Tage. Konfigurierbar per `cache_ttl_days`.
Cache ist case-insensitive (lowercased email als Key).
Korrupte JSON-Datei wird automatisch ignoriert + überschrieben — KEINE Datenverluste
beim Schreiben (atomic write via temp-File + replace).
"""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


_SCHEMA_VERSION = 1
DEFAULT_TTL_DAYS = 30


@dataclass(frozen=True)
class CachedVerification:
    email: str
    status: str
    sub_status: str
    verified_at: datetime
    did_you_mean: str = ""
    free_email: bool = False

    def is_fresh(self, ttl_days: int = DEFAULT_TTL_DAYS, *, now: Optional[datetime] = None) -> bool:
        if now is None:
            now = datetime.now(timezone.utc)
        return (now - self.verified_at) < timedelta(days=ttl_days)


class EmailVerifyCache:
    def __init__(self, path: Path, ttl_days: int = DEFAULT_TTL_DAYS):
        self.path = path
        self.ttl_days = ttl_days
        self._entries: dict[str, CachedVerification] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            # Korrupte Datei → ignorieren, wird beim nächsten save() überschrieben.
            return
        if data.get("schema") != _SCHEMA_VERSION:
            return
        for key, payload in (data.get("entries") or {}).items():
            try:
                self._entries[key.lower()] = CachedVerification(
                    email=key.lower(),
                    status=str(payload["status"]),
                    sub_status=str(payload.get("sub_status", "")),
                    verified_at=datetime.fromisoformat(payload["verified_at"]),
                    did_you_mean=str(payload.get("did_you_mean", "")),
                    free_email=bool(payload.get("free_email", False)),
                )
            except (KeyError, ValueError, TypeError):
                continue  # Einzelne kaputte Einträge silently skip

    def get(self, email: str) -> Optional[CachedVerification]:
        """Gibt frischen Eintrag zurück, oder None (nicht gecached / abgelaufen)."""
        self._ensure_loaded()
        entry = self._entries.get(email.lower())
        if entry is None:
            return None
        if not entry.is_fresh(self.ttl_days):
            return None
        return entry

    def put(
        self,
        email: str,
        *,
        status: str,
        sub_status: str = "",
        did_you_mean: str = "",
        free_email: bool = False,
        verified_at: Optional[datetime] = None,
    ) -> CachedVerification:
        self._ensure_loaded()
        entry = CachedVerification(
            email=email.lower(),
            status=status,
            sub_status=sub_status,
            verified_at=verified_at or datetime.now(timezone.utc),
            did_you_mean=did_you_mean,
            free_email=free_email,
        )
        self._entries[entry.email] = entry
        return entry

    def save(self) -> None:
        """Atomic-Write via temp-File + replace — kein Datenverlust bei Crash."""
        self._ensure_loaded()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": _SCHEMA_VERSION,
            "entries": {
                e.email: {
                    "status": e.status,
                    "sub_status": e.sub_status,
                    "verified_at": e.verified_at.isoformat(),
                    "did_you_mean": e.did_you_mean,
                    "free_email": e.free_email,
                }
                for e in self._entries.values()
            },
        }
        # Temp-File im gleichen Dir → os.replace ist atomic auf gleichem Volume
        fd, tmp_path = tempfile.mkstemp(
            prefix=".verified-emails-", suffix=".json.tmp", dir=str(self.path.parent),
        )
        try:
            import os as _os
            with _os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            _os.replace(tmp_path, self.path)
        except Exception:
            try:
                _os.unlink(tmp_path)
            except Exception:
                pass
            raise

    def size(self) -> int:
        self._ensure_loaded()
        return len(self._entries)

    def stats(self) -> dict[str, int]:
        """Counts pro status — nur frische Einträge."""
        self._ensure_loaded()
        counts: dict[str, int] = {}
        for e in self._entries.values():
            if not e.is_fresh(self.ttl_days):
                continue
            counts[e.status] = counts.get(e.status, 0) + 1
        return counts
