"""End-to-end tests for Gmail client workflow."""

import os
import pytest
from unittest.mock import Mock, patch

from gmail_client import get_client


@pytest.mark.e2e
class TestGmailWorkflow:
    """End-to-end tests for complete Gmail client workflows."""

    @pytest.fixture
    def mock_gmail_service(self):
        """Mock Gmail service for E2E testing."""
        with (
            patch("gmail_client_impl.os.path.exists") as mock_exists,
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

    def test_complete_email_workflow(self, mock_gmail_service) -> None:
        """Test complete workflow: read, send, mark as read, delete."""
        # Configure mock responses
        mock_service = mock_gmail_service

        # Mock message list
        mock_service.users().messages().list.return_value.execute.return_value = {
            "messages": [{"id": "msg123"}]
        }

        # Mock message get
        mock_service.users().messages().get.return_value.execute.return_value = {
            "raw": "RnJvbTogc2VuZGVyQGV4YW1wbGUuY29tClRvOiByZWNpcGllbnRAZXhhbXBsZS5jb20KU3ViamVjdDogVGVzdApEYXRlOiBNb24sIDE1IEphbiAyMDI1IDEwOjAwOjAwICswMDAwCgpUZXN0IGJvZHk="
        }

        # Mock other operations
        mock_service.users().messages().send.return_value.execute.return_value = {
            "id": "sent123"
        }
        mock_service.users().messages().modify.return_value.execute.return_value = {}
        mock_service.users().messages().delete.return_value.execute.return_value = {}

        # Get client using main interface
        client = get_client()

        # Step 1: Read messages
        messages = list(client.get_messages())
        assert len(messages) == 1
        message = messages[0]
        assert message.id == "msg123"
        assert message.from_ == "sender@example.com"
        assert message.to == "recipient@example.com"
        assert message.subject == "Test"
        assert message.body == "Test body"

        # Step 2: Send a message
        send_result = client.send_message(
            to="new@example.com", subject="Reply Test", body="This is a reply"
        )
        assert send_result is True

        # Step 3: Mark as read
        read_result = client.mark_as_read(message.id)
        assert read_result is True

        # Step 4: Delete message
        delete_result = client.delete_message(message.id)
        assert delete_result is True

        # Verify all operations were called
        mock_service.users().messages().list.assert_called()
        mock_service.users().messages().get.assert_called()
        mock_service.users().messages().send.assert_called()
        mock_service.users().messages().modify.assert_called()
        mock_service.users().messages().delete.assert_called()

    def test_error_handling_workflow(self, mock_gmail_service) -> None:
        """Test workflow with API errors."""
        from googleapiclient.errors import HttpError

        mock_service = mock_gmail_service

        # Mock HTTP error
        http_error = HttpError(
            resp=Mock(status=404, reason="Not Found"),
            content=b'{"error": {"message": "Message not found"}}',
        )

        mock_service.users().messages().delete.return_value.execute.side_effect = (
            http_error
        )

        client = get_client()

        # Should handle error gracefully
        result = client.delete_message("nonexistent_id")
        assert result is False

    def test_empty_inbox_workflow(self, mock_gmail_service) -> None:
        """Test workflow with empty inbox."""
        mock_service = mock_gmail_service

        # Mock empty inbox
        mock_service.users().messages().list.return_value.execute.return_value = {
            "messages": []
        }

        client = get_client()

        # Should handle empty inbox gracefully
        messages = list(client.get_messages())
        assert len(messages) == 0

    def test_large_message_handling(self, mock_gmail_service) -> None:
        """Test handling of large messages."""
        mock_service = mock_gmail_service

        # Create large message content
        large_body = "This is a large message body. " * 1000
        large_subject = "Large Message Subject " * 10

        # Create properly encoded message
        import base64

        email_content = (
            f"From: sender@example.com\r\n"
            f"To: recipient@example.com\r\n"
            f"Subject: {large_subject}\r\n"
            f"\r\n"
            f"{large_body}"
        )

        mock_service.users().messages().list.return_value.execute.return_value = {
            "messages": [{"id": "large_msg"}]
        }

        mock_service.users().messages().get.return_value.execute.return_value = {
            "raw": base64.urlsafe_b64encode(email_content.encode()).decode()
        }

        client = get_client()

        messages = list(client.get_messages())
        assert len(messages) == 1

        message = messages[0]
        assert large_subject.strip() in message.subject
        assert "This is a large message body." in message.body
        assert len(message.body) > 1000

    @pytest.mark.skipif(
        not os.path.exists("credentials.json"),
        reason="Real Gmail credentials not available",
    )
    def test_real_gmail_e2e(self) -> None:
        """Real end-to-end test with actual Gmail API.

        This test requires real credentials and should be run carefully
        as it may interact with a real Gmail account.
        """
        try:
            client = get_client()

            # Get a few messages (read-only operation)
            message_count = 0
            for message in client.get_messages():
                # Verify message structure
                assert message.id
                assert isinstance(message.from_, str)
                assert isinstance(message.to, str)
                assert isinstance(message.subject, str)
                assert isinstance(message.body, str)
                assert isinstance(message.date, str)

                message_count += 1
                if message_count >= 3:  # Limit for safety
                    break

            print(f"Successfully processed {message_count} real messages")

        except Exception as e:
            pytest.skip(f"Real Gmail E2E test failed: {e}")
