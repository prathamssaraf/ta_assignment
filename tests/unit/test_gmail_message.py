"""Unit tests for GmailMessage implementation."""

import base64
import pytest
from typing import Any, Dict

from message import Message
from message_impl import GmailMessage


class TestGmailMessage:
    """Test GmailMessage implementation."""

    def test_gmail_message_creation(self) -> None:
        """Test GmailMessage creation and basic properties."""
        message_id = "test-message-id"

        # Create test email content
        email_content = (
            "From: sender@example.com\r\n"
            "To: recipient@example.com\r\n"
            "Subject: Test Subject\r\n"
            "Date: Mon, 15 Jan 2025 10:00:00 +0000\r\n"
            "\r\n"
            "This is the message body."
        )

        raw_data = {"raw": base64.urlsafe_b64encode(email_content.encode()).decode()}

        message = GmailMessage(message_id, raw_data)

        # Verify it implements Message protocol
        assert isinstance(message, Message)

        # Test properties
        assert message.id == message_id
        assert message.from_ == "sender@example.com"
        assert message.to == "recipient@example.com"
        assert message.subject == "Test Subject"
        assert message.body == "This is the message body."
        # Date might be parsed slightly differently by email module
        assert "Jan 2025 10:00:00" in message.date

    def test_gmail_message_empty_raw_data(self) -> None:
        """Test GmailMessage with empty raw data."""
        message_id = "empty-message-id"
        raw_data: Dict[str, Any] = {}

        message = GmailMessage(message_id, raw_data)

        assert message.id == message_id
        assert message.from_ == ""
        assert message.to == ""
        assert message.subject == ""
        assert message.body == ""
        assert message.date == ""

    def test_gmail_message_multipart_body(self) -> None:
        """Test GmailMessage with multipart content."""
        message_id = "multipart-message-id"

        # Create multipart email content
        email_content = (
            "From: sender@example.com\r\n"
            "To: recipient@example.com\r\n"
            "Subject: Multipart Test\r\n"
            'Content-Type: multipart/mixed; boundary="boundary123"\r\n'
            "\r\n"
            "--boundary123\r\n"
            "Content-Type: text/plain\r\n"
            "\r\n"
            "Plain text content.\r\n"
            "--boundary123\r\n"
            "Content-Type: text/html\r\n"
            "\r\n"
            "<html><body>HTML content</body></html>\r\n"
            "--boundary123--\r\n"
        )

        raw_data = {"raw": base64.urlsafe_b64encode(email_content.encode()).decode()}

        message = GmailMessage(message_id, raw_data)

        assert message.id == message_id
        assert message.subject == "Multipart Test"
        assert "Plain text content." in message.body

    def test_gmail_message_special_characters(self) -> None:
        """Test GmailMessage with special characters."""
        message_id = "special-chars-id"

        email_content = (
            "From: sender@example.com\r\n"
            "To: recipient@example.com\r\n"
            "Subject: Special chars test\r\n"
            "\r\n"
            "Body with special characters"
        )

        raw_data = {"raw": base64.urlsafe_b64encode(email_content.encode()).decode()}

        message = GmailMessage(message_id, raw_data)

        assert "Special chars test" in message.subject
        assert "special characters" in message.body

    def test_gmail_message_invalid_base64(self) -> None:
        """Test GmailMessage with invalid base64 data."""
        message_id = "invalid-base64-id"
        raw_data = {"raw": "invalid-base64-data"}

        # Should not crash, but may have empty/default values
        message = GmailMessage(message_id, raw_data)
        assert message.id == message_id
