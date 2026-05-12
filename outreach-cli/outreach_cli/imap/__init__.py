"""IMAP-Layer für outreach-cli — Bounce-Check via ProtonMail Bridge."""
from .client import BridgeImapClient, ImapConnectError, ImapAuthError
from .parser import BounceMessage, parse_bounce

__all__ = [
    "BridgeImapClient",
    "ImapConnectError",
    "ImapAuthError",
    "BounceMessage",
    "parse_bounce",
]
