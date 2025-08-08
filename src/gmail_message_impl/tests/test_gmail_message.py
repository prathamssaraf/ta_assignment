"""Unit tests for GmailEmailMessage parser with comprehensive edge cases."""

import json
from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from gmail_message_impl import GmailEmailMessage


class TestGmailEmailMessage:
    """Test suite for GmailEmailMessage parsing functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        # Valid Gmail API response template
        self.valid_gmail_response = {
            "id": "msg_123",
            "threadId": "thread_456",
            "labelIds": ["INBOX", "UNREAD"],
            "snippet": "This is a test message snippet",
            "internalDate": "1640995200000",  # 2022-01-01 00:00:00 UTC
            "payload": {
                "mimeType": "multipart/mixed",
                "headers": [
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "recipient@example.com"},
                    {"name": "Date", "value": "Sat, 1 Jan 2022 00:00:00 +0000"},
                ],
                "parts": [
                    {
                        "mimeType": "text/plain",
                        "body": {
                            "data": "VGhpcyBpcyBhIHRlc3QgbWVzc2FnZQ=="  # base64: "This is a test message"
                        }
                    }
                ]
            }
        }

    @pytest.mark.unit
    def test_initialization_with_valid_response(self) -> None:
        """Test successful initialization with valid Gmail response."""
        response_json = json.dumps(self.valid_gmail_response)
        
        message = GmailEmailMessage("msg_123", response_json)
        
        assert message.message_id == "msg_123"
        assert message._gmail_data == self.valid_gmail_response

    @pytest.mark.unit
    def test_initialization_with_malformed_json(self) -> None:
        """Test initialization failure with malformed JSON."""
        malformed_json = '{"incomplete": json, "data":'
        
        with pytest.raises(ValueError) as exc_info:
            GmailEmailMessage("msg_123", malformed_json)
        
        assert "Invalid Gmail response JSON" in str(exc_info.value)

    @pytest.mark.unit
    def test_initialization_with_empty_json(self) -> None:
        """Test initialization with empty JSON."""
        empty_json = "{}"
        
        message = GmailEmailMessage("msg_123", empty_json)
        
        assert message.message_id == "msg_123"
        assert message._gmail_data == {}

    @pytest.mark.unit
    def test_initialization_with_null_json(self) -> None:
        """Test initialization with null JSON."""
        null_json = "null"
        
        # Should handle null gracefully
        message = GmailEmailMessage("msg_123", null_json)
        
        assert message.message_id == "msg_123"
        assert message._gmail_data is None

    @pytest.mark.unit
    def test_sender_extraction_simple_email(self) -> None:
        """Test sender extraction from simple email address."""
        response_data = {
            "payload": {
                "headers": [{"name": "From", "value": "test@example.com"}]
            }
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        assert message.sender == "test@example.com"

    @pytest.mark.unit
    def test_sender_extraction_with_display_name(self) -> None:
        """Test sender extraction with display name format."""
        response_data = {
            "payload": {
                "headers": [{"name": "From", "value": "John Doe <john@example.com>"}]
            }
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        assert message.sender == "john@example.com"

    @pytest.mark.unit
    def test_sender_extraction_malformed_header(self) -> None:
        """Test sender extraction with malformed From header."""
        response_data = {
            "payload": {
                "headers": [{"name": "From", "value": "Malformed <incomplete"}]
            }
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        # Should return the raw value when parsing fails
        assert message.sender == "Malformed <incomplete"

    @pytest.mark.unit
    def test_sender_extraction_missing_from_header(self) -> None:
        """Test sender extraction when From header is missing."""
        response_data = {
            "payload": {
                "headers": [{"name": "Subject", "value": "Test"}]  # No From header
            }
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        assert message.sender == ""

    @pytest.mark.unit
    def test_recipients_parsing_single_recipient(self) -> None:
        """Test recipient parsing with single recipient."""
        response_data = {
            "payload": {
                "headers": [{"name": "To", "value": "recipient@example.com"}]
            }
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        assert message.recipients == ["recipient@example.com"]

    @pytest.mark.unit
    def test_recipients_parsing_multiple_recipients(self) -> None:
        """Test recipient parsing with multiple recipients."""
        response_data = {
            "payload": {
                "headers": [{"name": "To", "value": "user1@example.com, John Doe <user2@example.com>, user3@example.com"}]
            }
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        expected = ["user1@example.com", "user2@example.com", "user3@example.com"]
        assert message.recipients == expected

    @pytest.mark.unit
    def test_recipients_parsing_malformed_addresses(self) -> None:
        """Test recipient parsing with malformed email addresses."""
        response_data = {
            "payload": {
                "headers": [{"name": "To", "value": "invalid-email, user@domain.com, <incomplete@"}]
            }
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        # Should extract only valid email addresses
        assert message.recipients == ["user@domain.com"]

    @pytest.mark.unit
    def test_timestamp_from_internal_date(self) -> None:
        """Test timestamp extraction from Gmail internalDate."""
        response_data = {
            "internalDate": "1640995200000"  # 2022-01-01 00:00:00 UTC
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        expected = datetime.fromtimestamp(1640995200, tz=UTC)
        assert message.timestamp == expected

    @pytest.mark.unit
    def test_timestamp_from_date_header_fallback(self) -> None:
        """Test timestamp extraction fallback to Date header."""
        response_data = {
            "payload": {
                "headers": [{"name": "Date", "value": "Sat, 1 Jan 2022 12:00:00 +0000"}]
            }
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        # Should parse the date header when internalDate is missing
        assert message.timestamp.year == 2022
        assert message.timestamp.month == 1
        assert message.timestamp.day == 1

    @pytest.mark.unit
    def test_timestamp_with_malformed_date_header(self) -> None:
        """Test timestamp handling with malformed date header."""
        response_data = {
            "payload": {
                "headers": [{"name": "Date", "value": "Invalid Date Format"}]
            }
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        # Should fallback to current time for unparseable dates
        assert isinstance(message.timestamp, datetime)
        assert message.timestamp.tzinfo == UTC

    @pytest.mark.unit
    def test_body_text_extraction_plain_text(self) -> None:
        """Test body text extraction from plain text part."""
        response_data = {
            "payload": {
                "parts": [
                    {
                        "mimeType": "text/plain",
                        "body": {"data": "VGhpcyBpcyBwbGFpbiB0ZXh0"}  # "This is plain text"
                    }
                ]
            }
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        assert message.body_text == "This is plain text"

    @pytest.mark.unit
    def test_body_text_extraction_with_invalid_base64(self) -> None:
        """Test body text extraction with invalid base64 data."""
        response_data = {
            "payload": {
                "parts": [
                    {
                        "mimeType": "text/plain",
                        "body": {"data": "invalid-base64-data!!!"}
                    }
                ]
            }
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        # Should handle invalid base64 gracefully
        assert message.body_text == ""

    @pytest.mark.unit
    def test_body_html_extraction(self) -> None:
        """Test HTML body extraction."""
        html_content = "<p>This is HTML content</p>"
        html_base64 = "PHA+VGhpcyBpcyBIVE1MIGNvbnRlbnQ8L3A+"
        
        response_data = {
            "payload": {
                "parts": [
                    {
                        "mimeType": "text/html",
                        "body": {"data": html_base64}
                    }
                ]
            }
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        assert message.body_html == html_content

    @pytest.mark.unit
    def test_body_text_fallback_from_html(self) -> None:
        """Test body text fallback when only HTML is available."""
        html_base64 = "PHA+VGhpcyBpcyA8c3Ryb25nPkhUTUw8L3N0cm9uZz4gY29udGVudDwvcD4="  # "<p>This is <strong>HTML</strong> content</p>"
        
        response_data = {
            "payload": {
                "parts": [
                    {
                        "mimeType": "text/html",
                        "body": {"data": html_base64}
                    }
                ]
            }
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        # Should convert HTML to text
        assert "This is HTML content" in message.body_text
        assert "<p>" not in message.body_text  # HTML tags should be removed

    @pytest.mark.unit
    def test_is_read_status_with_unread_label(self) -> None:
        """Test read status with UNREAD label present."""
        response_data = {
            "labelIds": ["INBOX", "UNREAD", "IMPORTANT"]
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        assert message.is_read is False

    @pytest.mark.unit
    def test_is_read_status_without_unread_label(self) -> None:
        """Test read status without UNREAD label."""
        response_data = {
            "labelIds": ["INBOX", "IMPORTANT"]
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        assert message.is_read is True

    @pytest.mark.unit
    def test_is_starred_status(self) -> None:
        """Test starred status detection."""
        response_data = {
            "labelIds": ["INBOX", "STARRED"]
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        assert message.is_starred is True

    @pytest.mark.unit
    def test_attachment_count_with_attachments(self) -> None:
        """Test attachment count with actual attachments."""
        response_data = {
            "payload": {
                "parts": [
                    {
                        "mimeType": "text/plain",
                        "body": {"data": "dGV4dA=="}
                    },
                    {
                        "mimeType": "application/pdf",
                        "filename": "document.pdf",
                        "body": {"attachmentId": "attachment_123"}
                    },
                    {
                        "mimeType": "image/png",
                        "filename": "image.png",
                        "body": {"attachmentId": "attachment_456"}
                    }
                ]
            }
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        assert message.attachment_count == 2

    @pytest.mark.unit
    def test_attachment_count_no_attachments(self) -> None:
        """Test attachment count with no attachments."""
        response_data = {
            "payload": {
                "parts": [
                    {
                        "mimeType": "text/plain",
                        "body": {"data": "dGV4dA=="}
                    }
                ]
            }
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        assert message.attachment_count == 0

    @pytest.mark.unit
    def test_snippet_from_gmail_response(self) -> None:
        """Test snippet extraction from Gmail response."""
        response_data = {
            "snippet": "This is a Gmail-generated snippet"
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        assert message.get_snippet() == "This is a Gmail-generated snippet"

    @pytest.mark.unit
    def test_snippet_truncation_with_long_content(self) -> None:
        """Test snippet truncation for long content."""
        long_snippet = "A" * 150  # 150 characters
        response_data = {
            "snippet": long_snippet
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        snippet = message.get_snippet(max_length=100)
        assert len(snippet) <= 103  # 100 chars + "..."
        assert snippet.endswith("...")

    @pytest.mark.unit
    def test_snippet_fallback_to_body_text(self) -> None:
        """Test snippet fallback to body text when Gmail snippet is missing."""
        response_data = {
            "payload": {
                "parts": [
                    {
                        "mimeType": "text/plain",
                        "body": {"data": "VGhpcyBpcyB0aGUgZmFsbGJhY2sgYm9keSB0ZXh0"}  # "This is the fallback body text"
                    }
                ]
            }
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        assert message.get_snippet() == "This is the fallback body text"

    @pytest.mark.unit
    def test_labels_extraction(self) -> None:
        """Test labels extraction from Gmail response."""
        response_data = {
            "labelIds": ["INBOX", "UNREAD", "IMPORTANT", "CATEGORY_PERSONAL"]
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        expected = ["INBOX", "UNREAD", "IMPORTANT", "CATEGORY_PERSONAL"]
        assert message.labels == expected

    @pytest.mark.unit
    def test_labels_extraction_empty_list(self) -> None:
        """Test labels extraction with empty label list."""
        response_data = {
            "labelIds": []
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        assert message.labels == []

    @pytest.mark.unit
    def test_thread_id_extraction(self) -> None:
        """Test thread ID extraction."""
        response_data = {
            "threadId": "thread_789"
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        assert message.thread_id == "thread_789"

    @pytest.mark.unit
    def test_missing_payload_handling(self) -> None:
        """Test handling of response with missing payload."""
        response_data = {
            "id": "msg_123",
            # No payload
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        # Should handle missing payload gracefully
        assert message.subject == ""
        assert message.sender == ""
        assert message.body_text == ""
        assert message.recipients == []

    @pytest.mark.unit
    def test_nested_multipart_message_parsing(self) -> None:
        """Test parsing of nested multipart messages."""
        response_data = {
            "payload": {
                "mimeType": "multipart/mixed",
                "parts": [
                    {
                        "mimeType": "multipart/alternative",
                        "parts": [
                            {
                                "mimeType": "text/plain",
                                "body": {"data": "UGxhaW4gdGV4dCBjb250ZW50"}  # "Plain text content"
                            },
                            {
                                "mimeType": "text/html",
                                "body": {"data": "PGI+SFRNTCBjb250ZW50PC9iPg=="}  # "<b>HTML content</b>"
                            }
                        ]
                    }
                ]
            }
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        assert message.body_text == "Plain text content"
        assert message.body_html == "<b>HTML content</b>"

    @pytest.mark.unit
    def test_cc_and_bcc_recipients_parsing(self) -> None:
        """Test CC and BCC recipients parsing."""
        response_data = {
            "payload": {
                "headers": [
                    {"name": "Cc", "value": "cc1@example.com, CC User <cc2@example.com>"},
                    {"name": "Bcc", "value": "bcc@example.com"}
                ]
            }
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        assert message.cc_recipients == ["cc1@example.com", "cc2@example.com"]
        assert message.bcc_recipients == ["bcc@example.com"]

    @pytest.mark.unit
    def test_subject_with_special_characters(self) -> None:
        """Test subject extraction with special characters and encoding."""
        response_data = {
            "payload": {
                "headers": [{"name": "Subject", "value": "Test with émojis 🚀 and spéciâl chars"}]
            }
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        assert message.subject == "Test with émojis 🚀 and spéciâl chars"


class TestGmailEmailMessageEdgeCases:
    """Test suite for edge cases and error handling."""

    @pytest.mark.unit
    def test_extremely_malformed_response_data(self) -> None:
        """Test handling of extremely malformed response data."""
        # Malformed JSON with control characters
        malformed_data = '{"payload": {"headers": [{"name": "From", "value": "test\x00\x01\x02@example.com"}]}}'
        
        # Should not crash, but handle gracefully
        message = GmailEmailMessage("msg_123", malformed_data)
        assert message.message_id == "msg_123"

    @pytest.mark.unit
    def test_unicode_handling_in_base64_content(self) -> None:
        """Test handling of Unicode content in base64 encoded body."""
        # Unicode content: "Hello 世界 🌍"
        unicode_base64 = "SGVsbG8g5LiW55WMIPCfjI0="
        
        response_data = {
            "payload": {
                "parts": [
                    {
                        "mimeType": "text/plain",
                        "body": {"data": unicode_base64}
                    }
                ]
            }
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        assert "Hello" in message.body_text
        assert "世界" in message.body_text
        assert "🌍" in message.body_text

    @pytest.mark.unit
    def test_very_large_message_handling(self) -> None:
        """Test handling of very large messages."""
        # Simulate a very large base64 encoded content
        large_content = "A" * 10000  # 10KB of 'A' characters
        large_base64 = "QUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFB" * 200
        
        response_data = {
            "payload": {
                "parts": [
                    {
                        "mimeType": "text/plain",
                        "body": {"data": large_base64}
                    }
                ]
            }
        }
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        # Should handle large content without crashing
        assert len(message.body_text) > 1000
        assert isinstance(message.get_snippet(max_length=200), str)

    @pytest.mark.unit
    def test_missing_critical_fields_handling(self) -> None:
        """Test handling when all critical fields are missing."""
        response_data = {}  # Completely empty response
        
        message = GmailEmailMessage("msg_123", json.dumps(response_data))
        
        # Should provide sensible defaults
        assert message.message_id == "msg_123"
        assert message.sender == ""
        assert message.subject == ""
        assert message.body_text == ""
        assert message.recipients == []
        assert message.labels == []
        assert message.attachment_count == 0
        assert isinstance(message.timestamp, datetime)