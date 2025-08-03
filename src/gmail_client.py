"""Gmail client main module - entry point for Gmail functionality."""

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

# Re-export the get_client function from the API
from mail_client_api import get_client

# Import the implementation to initialize the client factory (when dependencies available)
try:
    import gmail_client_impl  # noqa: F401
except ImportError:
    # Implementation dependencies not available (e.g., google-api-python-client)
    pass

__all__ = ["get_client"]
