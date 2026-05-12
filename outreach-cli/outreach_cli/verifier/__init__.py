"""Email-Verifier — NeverBounce (primary) + ZeroBounce (fallback) + JSON-Cache."""
from .neverbounce import (
    NeverBounceConfig,
    NeverBounceClient,
    NeverBounceError,
    NeverBounceQuotaError,
)
from .zerobounce import (
    ZeroBounceConfig,
    ZeroBounceClient,
    ZeroBounceError,
    ZeroBounceQuotaError,
    VerificationStatus,
)
from .cache import EmailVerifyCache, CachedVerification
from .pipeline import (
    VerificationDecision,
    VerificationBucket,
    BatchVerifyResult,
    verify_batch,
)

__all__ = [
    "NeverBounceConfig",
    "NeverBounceClient",
    "NeverBounceError",
    "NeverBounceQuotaError",
    "ZeroBounceConfig",
    "ZeroBounceClient",
    "ZeroBounceError",
    "ZeroBounceQuotaError",
    "VerificationStatus",
    "EmailVerifyCache",
    "CachedVerification",
    "VerificationDecision",
    "VerificationBucket",
    "BatchVerifyResult",
    "verify_batch",
]
