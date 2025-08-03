"""Gmail client main module - entry point for Gmail functionality."""

import contextlib
import sys
from pathlib import Path

# Add workspace packages to path
src_dir = Path(__file__).parent
for package_dir in [
    "message/src",
    "mail_client_api/src",
    "gmail_message_impl/src",
    "gmail_client_impl/src",
]:
    package_path = src_dir / package_dir
    if package_path.exists():
        sys.path.insert(0, str(package_path))

# Import API and implementation modules
import mail_client_api  # noqa: E402
with contextlib.suppress(ImportError):
    from gmail_client_impl import get_client_impl  # noqa: E402
    # Set up dependency injection properly
    mail_client_api.get_client = get_client_impl

# Re-export the configured get_client function
from mail_client_api import get_client  # noqa: E402

__all__ = ["get_client"]
