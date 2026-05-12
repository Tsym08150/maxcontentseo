"""Batch-Verifikation: cache-first, dann ZeroBounce-API, dann Bucketing.

Status-Routing (per User-Spec):
  valid                                              → SEND
  catch-all                                          → SEND_WITH_WARN (proceed, aber yellow flag)
  invalid / unknown / spamtrap / abuse / do_not_mail → SKIP + Sheet auf "Email-Ungültig"

Pipeline:
  1. Cache-Lookup für alle Emails (fresh-only)
  2. Für gecachete Emails: Bucket sofort.
  3. Für uncached: ZeroBounceClient.validate() → Cache schreiben → Bucket.
  4. Bei API-Quota-Fehler mitten im Batch: graceful stop, restliche als UNKNOWN markieren
     mit Hinweis "Quota voll, manuell prüfen".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Iterable, Optional

from .cache import EmailVerifyCache, CachedVerification, DEFAULT_TTL_DAYS
from .zerobounce import (
    ZeroBounceClient,
    ZeroBounceConfig,
    ZeroBounceError,
    ZeroBounceQuotaError,
)


class VerificationBucket(str, Enum):
    SEND = "send"                 # Status: valid
    SEND_WITH_WARN = "send_warn"  # Status: catch-all
    SKIP = "skip"                 # Status: invalid/unknown/spamtrap/abuse/do_not_mail
    QUOTA_ABORT = "quota_abort"   # API-Quota voll → user manuell prüfen
    ERROR = "error"               # API-Fehler / Netzwerk


# Status → Bucket Mapping
_BUCKET_MAP: dict[str, VerificationBucket] = {
    "valid": VerificationBucket.SEND,
    "catch-all": VerificationBucket.SEND_WITH_WARN,
    "invalid": VerificationBucket.SKIP,
    "unknown": VerificationBucket.SKIP,
    "spamtrap": VerificationBucket.SKIP,
    "abuse": VerificationBucket.SKIP,
    "do_not_mail": VerificationBucket.SKIP,
}


def _bucket_for_status(status: str) -> VerificationBucket:
    return _BUCKET_MAP.get(status.lower(), VerificationBucket.SKIP)


@dataclass(frozen=True)
class VerificationDecision:
    email: str
    bucket: VerificationBucket
    status: str  # ZeroBounce-status (oder Synthetic wie "quota_abort")
    sub_status: str = ""
    did_you_mean: str = ""
    source: str = "api"  # "api" | "cache" | "error"
    error_msg: str = ""


@dataclass
class BatchVerifyResult:
    decisions: list[VerificationDecision] = field(default_factory=list)
    api_calls_made: int = 0
    cache_hits: int = 0
    quota_aborted_at: Optional[str] = None  # erste E-Mail, die nicht mehr verifiziert wurde

    def by_bucket(self, bucket: VerificationBucket) -> list[VerificationDecision]:
        return [d for d in self.decisions if d.bucket == bucket]

    @property
    def send_emails(self) -> list[str]:
        return [d.email for d in self.decisions if d.bucket == VerificationBucket.SEND]

    @property
    def send_with_warn_emails(self) -> list[str]:
        return [d.email for d in self.decisions if d.bucket == VerificationBucket.SEND_WITH_WARN]

    @property
    def skip_emails(self) -> list[str]:
        return [d.email for d in self.decisions if d.bucket == VerificationBucket.SKIP]

    @property
    def sendable_emails(self) -> list[str]:
        """SEND + SEND_WITH_WARN — Caller filtert ggf. warns raus."""
        return self.send_emails + self.send_with_warn_emails


def _default_cache_path() -> Path:
    """outreach-cli/cache/verified-emails.json — relativ zum Package."""
    # verifier/pipeline.py → parent = verifier/ → parent.parent = outreach_cli/ →
    # parent.parent.parent = outreach-cli/
    return Path(__file__).resolve().parent.parent.parent / "cache" / "verified-emails.json"


def verify_batch(
    emails: Iterable[str],
    *,
    client: Optional[ZeroBounceClient] = None,
    cache: Optional[EmailVerifyCache] = None,
    ttl_days: int = DEFAULT_TTL_DAYS,
) -> BatchVerifyResult:
    """Verifiziert eine Liste Emails. Cache-first.

    Args:
        emails: Liste der zu prüfenden Adressen (lowercased intern).
        client: Optional vor-konfigurierter ZeroBounceClient (für Tests).
        cache: Optional vor-konfigurierter EmailVerifyCache (für Tests).
        ttl_days: Cache-TTL in Tagen.

    Returns BatchVerifyResult mit decision-Liste + Stats.
    """
    if cache is None:
        cache = EmailVerifyCache(_default_cache_path(), ttl_days=ttl_days)

    result = BatchVerifyResult()
    # Dedupe — gleiche Email nur einmal prüfen, auch wenn Liste sie mehrfach enthält
    seen: dict[str, VerificationDecision] = {}
    unique_emails = []
    for raw in emails:
        e = (raw or "").strip().lower()
        if not e or e in seen or e in [u for u in unique_emails]:
            continue
        unique_emails.append(e)

    api_unavailable = False  # einmal eingetreten → restliche als ERROR markieren

    for email in unique_emails:
        # 1. Cache-Lookup
        cached = cache.get(email)
        if cached is not None:
            decision = VerificationDecision(
                email=email,
                bucket=_bucket_for_status(cached.status),
                status=cached.status,
                sub_status=cached.sub_status,
                did_you_mean=cached.did_you_mean,
                source="cache",
            )
            result.decisions.append(decision)
            result.cache_hits += 1
            continue

        # 2. API-Call
        if api_unavailable:
            # Quota-Abbruch: rest als ERROR markieren
            result.decisions.append(VerificationDecision(
                email=email,
                bucket=VerificationBucket.QUOTA_ABORT,
                status="quota_abort",
                source="error",
                error_msg="API-Quota erschöpft / API nicht erreichbar",
            ))
            continue

        if client is None:
            # Lazy: erst hier ZeroBounceClient.from_env() — vermeidet API-Key-Pflicht
            # für reine Cache-Hits (z.B. wenn alle Emails schon im Cache sind).
            try:
                client = ZeroBounceClient(ZeroBounceConfig.from_env())
            except SystemExit as e:
                # API-Key fehlt → kompletter Batch wird unverifiziert.
                api_unavailable = True
                result.decisions.append(VerificationDecision(
                    email=email,
                    bucket=VerificationBucket.ERROR,
                    status="config_error",
                    source="error",
                    error_msg=str(e),
                ))
                continue

        try:
            resp = client.validate(email)
        except ZeroBounceQuotaError as e:
            api_unavailable = True
            result.quota_aborted_at = email
            result.decisions.append(VerificationDecision(
                email=email,
                bucket=VerificationBucket.QUOTA_ABORT,
                status="quota_abort",
                source="error",
                error_msg=str(e),
            ))
            continue
        except ZeroBounceError as e:
            result.decisions.append(VerificationDecision(
                email=email,
                bucket=VerificationBucket.ERROR,
                status="api_error",
                source="error",
                error_msg=str(e),
            ))
            continue

        result.api_calls_made += 1

        # Cache schreiben
        cache.put(
            email,
            status=resp.status,
            sub_status=resp.sub_status,
            did_you_mean=resp.did_you_mean,
            free_email=resp.free_email,
        )

        result.decisions.append(VerificationDecision(
            email=email,
            bucket=_bucket_for_status(resp.status),
            status=resp.status,
            sub_status=resp.sub_status,
            did_you_mean=resp.did_you_mean,
            source="api",
        ))

    # Cache persistieren (nur bei API-Calls — kein Sinn wenn nur Cache-Hits)
    if result.api_calls_made > 0:
        try:
            cache.save()
        except OSError:
            pass  # Cache-Schreibfehler ist non-fatal

    return result
