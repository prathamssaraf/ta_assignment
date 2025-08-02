"""Unit tests for implementation modules."""

from unittest.mock import Mock, patch

import pytest

from gmail_client_impl import GmailClient, get_client_impl
from gmail_message_impl import GmailMessage, get_message_impl
from message import Message


class TestImplementationModules:
    """Test implementation modules for coverage."""

    def test_gmail_client_initialization_failure(self) -> None:
        """Test GmailClient initialization with missing credentials."""
        with pytest.raises(FileNotFoundError, match="Credentials file not found"):
            GmailClient("nonexistent_file.json")

    @patch("pathlib.Path.exists")
    @patch("gmail_client_impl.Credentials.from_authorized_user_file")
    @patch("gmail_client_impl.build")
    def test_gmail_client_service_property(
        self, mock_build: Mock, mock_creds: Mock, mock_exists: Mock
    ) -> None:
        """Test GmailClient service property."""
        # Mock successful authentication
        mock_exists.return_value = True
        mock_cred_instance = Mock()
        mock_cred_instance.valid = True
        mock_creds.return_value = mock_cred_instance

        mock_service = Mock()
        mock_build.return_value = mock_service

        client = GmailClient()

        # Test service property
        assert client.service == mock_service

        # Test service property when not initialized
        client._service = None
        with pytest.raises(RuntimeError, match="Gmail service not initialized"):
            _ = client.service

    def test_gmail_message_protocol_compliance(self) -> None:
        """Test that GmailMessage implements Message protocol correctly."""

        # Create a minimal valid message
        raw_data = {
            "raw": "RnJvbTogdGVzdEBleGFtcGxlLmNvbQpUbzogcmVjaXBpZW50QGV4YW1wbGUuY29tClN1YmplY3Q6IFRlc3QKCkJvZHk="
        }

        message = GmailMessage("test_id", raw_data)

        # Should implement Message protocol
        assert isinstance(message, Message)

        # All properties should be accessible
        assert isinstance(message.id, str)
        assert isinstance(message.from_, str)
        assert isinstance(message.to, str)
        assert isinstance(message.subject, str)
        assert isinstance(message.body, str)
        assert isinstance(message.date, str)

    def test_get_message_impl_factory(self) -> None:
        """Test get_message_impl factory function."""

        raw_data = {"raw": "dGVzdA=="}  # base64 encoded "test"
        message = get_message_impl("test_id", raw_data)

        assert isinstance(message, Message)
        assert message.id == "test_id"

    def test_get_client_impl_factory(self) -> None:
        """Test get_client_impl factory function."""

        try:
            get_client_impl("nonexistent.json")
            # Should not reach here due to missing credentials
            raise AssertionError("Should have raised FileNotFoundError")
        except FileNotFoundError:
            # Expected behavior
            pass
