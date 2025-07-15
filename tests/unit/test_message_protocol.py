"""Unit tests for Message protocol."""

import pytest
from unittest.mock import Mock

from message import Message


class TestMessageProtocol:
    """Test Message protocol interface."""

    def test_message_protocol_properties(self) -> None:
        """Test that Message protocol defines required properties."""
        # Create mock that conforms to Message protocol
        mock_message = Mock(spec=Message)
        mock_message.id = "test-id"
        mock_message.from_ = "sender@example.com"
        mock_message.to = "recipient@example.com"
        mock_message.subject = "Test Subject"
        mock_message.body = "Test body content"
        mock_message.date = "2025-01-15 10:00:00"

        # Verify protocol compliance
        assert isinstance(mock_message, Message)
        assert mock_message.id == "test-id"
        assert mock_message.from_ == "sender@example.com"
        assert mock_message.to == "recipient@example.com"
        assert mock_message.subject == "Test Subject"
        assert mock_message.body == "Test body content"
        assert mock_message.date == "2025-01-15 10:00:00"

    def test_message_protocol_runtime_checkable(self) -> None:
        """Test that Message protocol is runtime checkable."""
        mock_message = Mock()
        mock_message.id = "test"
        mock_message.from_ = "test@example.com"
        mock_message.to = "test@example.com"
        mock_message.subject = "test"
        mock_message.body = "test"
        mock_message.date = "test"

        # Should pass runtime check
        assert isinstance(mock_message, Message)

    def test_message_protocol_missing_properties(self) -> None:
        """Test that objects missing required properties fail runtime check."""
        incomplete_mock = Mock()
        incomplete_mock.id = "test"
        # Missing other required properties

        # Should fail runtime check
        assert not isinstance(incomplete_mock, Message)
