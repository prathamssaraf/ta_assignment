"""Gmail Client - Natural import entry point."""

try:
    from gmail_client_impl import get_client_impl
    get_client = get_client_impl
except ImportError:
    def get_client(*args, **kwargs):
        raise ImportError(
            "Gmail implementation not available. "
            "Install with: uv sync --extra full"
        )

def main():
    """Entry point for gmail-client CLI."""
    import sys
    print("Gmail Client CLI")
    print("Usage: from gmail_client import get_client")
    sys.exit(0)

__all__ = ["get_client", "main"]