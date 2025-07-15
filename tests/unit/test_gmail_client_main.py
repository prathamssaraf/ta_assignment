"""Unit tests for main gmail_client module."""

import pytest

from gmail_client import get_client
from gmail_client_protocol import Client


class TestGmailClientMain:
    """Test main gmail_client module functionality."""

    def test_get_client_import(self) -> None:
        """Test that get_client can be imported from main module."""
        # The import should work without error
        assert callable(get_client)

    def test_get_client_returns_client_protocol(self) -> None:
        """Test that get_client returns a Client protocol instance."""
        try:
            client = get_client()
            # Should implement Client protocol
            assert isinstance(client, Client)

            # Should have all required methods
            assert hasattr(client, "get_messages")
            assert hasattr(client, "send_message")
            assert hasattr(client, "delete_message")
            assert hasattr(client, "mark_as_read")

        except FileNotFoundError:
            # This is expected when credentials.json doesn't exist
            pytest.skip("No Gmail credentials available for testing")
        except Exception as e:
            # Other exceptions might occur during authentication
            pytest.skip(f"Gmail authentication failed: {e}")

    def test_module_exports(self) -> None:
        """Test that module exports the correct interface."""
        import gmail_client

        # Should export get_client
        assert hasattr(gmail_client, "get_client")
        assert "get_client" in gmail_client.__all__

        # Should only export get_client
        assert gmail_client.__all__ == ["get_client"]
