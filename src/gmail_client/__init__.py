"""Gmail Client - Natural import entry point."""

import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mail_client_api import Client

try:
    from gmail_client_impl import get_client_impl

    get_client = get_client_impl
except ImportError:

    def get_client(*_args: Any, **_kwargs: Any) -> "Client":  # noqa: ANN401
        msg = "Gmail implementation not available. Install with: uv sync --extra full"
        raise ImportError(msg)


def main() -> None:
    """Entry point for gmail-client CLI."""
    print("Gmail Client CLI")  # noqa: T201
    print("Usage: from gmail_client import get_client")  # noqa: T201
    sys.exit(0)


__all__ = ["get_client", "main"]
