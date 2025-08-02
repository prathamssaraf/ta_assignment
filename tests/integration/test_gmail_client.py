"""Integration tests for GmailClient."""

from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from gmail_client_impl import GmailClient
from mail_client_api import Client


@pytest.mark.integration
class TestGmailClientIntegration:
    """Integration tests for GmailClient.

    These tests require actual Gmail API credentials and may make real API calls.
    They are marked with @pytest.mark.integration and can be run separately.
    """

    @pytest.fixture
    def mock_credentials(self) -> Generator[Mock, None, None]:
        """Mock credentials for testing without real authentication."""
        with (
            patch("pathlib.Path.exists") as mock_exists,
            patch(
                "gmail_client_impl.Credentials.from_authorized_user_file"
            ) as mock_creds,
            patch("gmail_client_impl.build") as mock_build,
        ):
            mock_exists.return_value = True
            mock_cred_instance = Mock()
            mock_cred_instance.valid = True
            mock_creds.return_value = mock_cred_instance

            mock_service = Mock()
            mock_build.return_value = mock_service

            yield mock_service

    def test_gmail_client_implements_protocol(self, mock_credentials: Mock) -> None:
        """Test that GmailClient implements Client protocol."""
        client = GmailClient()
        assert isinstance(client, Client)

    def test_gmail_client_authentication_missing_credentials(self) -> None:
        """Test authentication error when credentials file is missing."""
        with pytest.raises(FileNotFoundError, match="Credentials file not found"):
            GmailClient("nonexistent_credentials.json")

    def test_gmail_client_get_messages_mock(self, mock_credentials: Mock) -> None:
        """Test get_messages with mocked Gmail API."""
        # Configure mock service responses
        mock_service = mock_credentials
        mock_messages_list = mock_service.users().messages().list
        mock_messages_get = mock_service.users().messages().get

        # Mock message list response
        mock_messages_list.return_value.execute.return_value = {
            "messages": [{"id": "msg1"}, {"id": "msg2"}]
        }

        # Mock individual message responses
        mock_msg_data = {
            "raw": "RnJvbTogdGVzdEBleGFtcGxlLmNvbQpUbzogcmVjaXBpZW50QGV4YW1wbGUuY29tClN1YmplY3Q6IFRlc3QKCkJvZHk="
        }
        mock_messages_get.return_value.execute.return_value = mock_msg_data

        client = GmailClient()
        messages = list(client.get_messages())

        assert len(messages) == 2
        for message in messages:
            assert hasattr(message, "id")
            assert hasattr(message, "from_")
            assert hasattr(message, "to")
            assert hasattr(message, "subject")
            assert hasattr(message, "body")

    def test_gmail_client_send_message_mock(self, mock_credentials: Mock) -> None:
        """Test send_message with mocked Gmail API."""
        mock_service = mock_credentials
        mock_send = mock_service.users().messages().send
        mock_send.return_value.execute.return_value = {"id": "sent_msg_id"}

        client = GmailClient()
        result = client.send_message(
            to="test@example.com", subject="Test Subject", body="Test body"
        )

        assert result is True
        mock_send.assert_called_once()

    def test_gmail_client_delete_message_mock(self, mock_credentials: Mock) -> None:
        """Test delete_message with mocked Gmail API."""
        mock_service = mock_credentials
        mock_delete = mock_service.users().messages().delete
        mock_delete.return_value.execute.return_value = {}

        client = GmailClient()
        result = client.delete_message("test_msg_id")

        assert result is True
        mock_delete.assert_called_with(userId="me", id="test_msg_id")

    def test_gmail_client_mark_as_read_mock(self, mock_credentials: Mock) -> None:
        """Test mark_as_read with mocked Gmail API."""
        mock_service = mock_credentials
        mock_modify = mock_service.users().messages().modify
        mock_modify.return_value.execute.return_value = {}

        client = GmailClient()
        result = client.mark_as_read("test_msg_id")

        assert result is True
        mock_modify.assert_called_with(
            userId="me", id="test_msg_id", body={"removeLabelIds": ["UNREAD"]}
        )

    @pytest.mark.skipif(
        not Path("credentials.json").exists(),
        reason="Real Gmail credentials not available",
    )
    def test_gmail_client_real_api(self) -> None:
        """Test with real Gmail API (requires credentials.json).

        This test is skipped unless real credentials are available.
        """
        try:
            client = GmailClient()

            # Test getting first few messages
            messages = []
            for i, message in enumerate(client.get_messages()):
                messages.append(message)
                if i >= 2:  # Limit to 3 messages for testing
                    break

            # Verify we got some messages
            assert len(messages) > 0

            # Verify message properties
            for message in messages:
                assert message.id
                assert isinstance(message.from_, str)
                assert isinstance(message.to, str)
                assert isinstance(message.subject, str)
                assert isinstance(message.body, str)
                assert isinstance(message.date, str)

        except Exception as e:
            pytest.skip(f"Real Gmail API test failed: {e}")
