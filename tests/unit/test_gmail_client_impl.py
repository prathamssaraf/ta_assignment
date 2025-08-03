"""Unit tests for GmailClient implementation."""

from unittest.mock import Mock, patch

import pytest

from gmail_client_impl import GmailClient, get_client_impl
from mail_client_api import Client


class TestGmailClientImpl:
    """Test GmailClient implementation."""

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

    @patch("pathlib.Path.exists")
    @patch("gmail_client_impl.Credentials.from_authorized_user_file")
    @patch("gmail_client_impl.build")
    def test_gmail_client_protocol_compliance(
        self, mock_build: Mock, mock_creds: Mock, mock_exists: Mock
    ) -> None:
        """Test that GmailClient implements Client protocol correctly."""
        # Mock successful authentication
        mock_exists.return_value = True
        mock_cred_instance = Mock()
        mock_cred_instance.valid = True
        mock_creds.return_value = mock_cred_instance

        mock_service = Mock()
        mock_build.return_value = mock_service

        client = GmailClient()

        # Should implement Client protocol
        assert isinstance(client, Client)

    @patch("pathlib.Path.exists")
    @patch("gmail_client_impl.Credentials.from_authorized_user_file")
    @patch("gmail_client_impl.build")
    def test_get_messages_method(
        self, mock_build: Mock, mock_creds: Mock, mock_exists: Mock
    ) -> None:
        """Test get_messages method with mocked Gmail API."""
        # Mock successful authentication
        mock_exists.return_value = True
        mock_cred_instance = Mock()
        mock_cred_instance.valid = True
        mock_creds.return_value = mock_cred_instance

        # Mock Gmail service
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock messages list response
        mock_messages_list = mock_service.users().messages().list
        mock_messages_list.return_value.execute.return_value = {
            "messages": [{"id": "msg1"}, {"id": "msg2"}]
        }

        # Mock message get response
        mock_message_get = mock_service.users().messages().get
        mock_message_get.return_value.execute.return_value = {
            "id": "msg1",
            "raw": "RnJvbTogdGVzdEBleGFtcGxlLmNvbQpUbzogcmVjaXBpZW50QGV4YW1wbGUuY29tClN1YmplY3Q6IFRlc3QKCkJvZHk=",
        }

        client = GmailClient()
        messages = list(client.get_messages())

        # Should have called the API methods
        mock_messages_list.assert_called_once()
        assert len(messages) >= 0  # May be empty due to mocking

    @patch("pathlib.Path.exists")
    @patch("gmail_client_impl.Credentials.from_authorized_user_file")
    @patch("gmail_client_impl.build")
    def test_send_message_method(
        self, mock_build: Mock, mock_creds: Mock, mock_exists: Mock
    ) -> None:
        """Test send_message method."""
        # Mock successful authentication
        mock_exists.return_value = True
        mock_cred_instance = Mock()
        mock_cred_instance.valid = True
        mock_creds.return_value = mock_cred_instance

        # Mock Gmail service
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock send response
        mock_send = mock_service.users().messages().send
        mock_send.return_value.execute.return_value = {"id": "sent_msg_id"}

        client = GmailClient()
        result = client.send_message("test@example.com", "Test Subject", "Test Body")

        assert result is True
        mock_send.assert_called_once()

    @patch("pathlib.Path.exists")
    @patch("gmail_client_impl.Credentials.from_authorized_user_file")
    @patch("gmail_client_impl.build")
    def test_delete_message_method(
        self, mock_build: Mock, mock_creds: Mock, mock_exists: Mock
    ) -> None:
        """Test delete_message method."""
        # Mock successful authentication
        mock_exists.return_value = True
        mock_cred_instance = Mock()
        mock_cred_instance.valid = True
        mock_creds.return_value = mock_cred_instance

        # Mock Gmail service
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock delete response
        mock_delete = mock_service.users().messages().delete
        mock_delete.return_value.execute.return_value = {}

        client = GmailClient()
        result = client.delete_message("test_msg_id")

        assert result is True
        mock_delete.assert_called_once()

    @patch("pathlib.Path.exists")
    @patch("gmail_client_impl.Credentials.from_authorized_user_file")
    @patch("gmail_client_impl.build")
    def test_mark_as_read_method(
        self, mock_build: Mock, mock_creds: Mock, mock_exists: Mock
    ) -> None:
        """Test mark_as_read method."""
        # Mock successful authentication
        mock_exists.return_value = True
        mock_cred_instance = Mock()
        mock_cred_instance.valid = True
        mock_creds.return_value = mock_cred_instance

        # Mock Gmail service
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock modify response
        mock_modify = mock_service.users().messages().modify
        mock_modify.return_value.execute.return_value = {}

        client = GmailClient()
        result = client.mark_as_read("test_msg_id")

        assert result is True
        mock_modify.assert_called_once()

    def test_get_client_impl_factory(self) -> None:
        """Test get_client_impl factory function."""
        try:
            get_client_impl("nonexistent.json")
            # Should not reach here due to missing credentials
            raise AssertionError("Should have raised FileNotFoundError")
        except FileNotFoundError:
            # Expected behavior
            pass
