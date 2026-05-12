"""Email-Verifier — ZeroBounce-API + JSON-Cache vor --confirm-live."""
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
