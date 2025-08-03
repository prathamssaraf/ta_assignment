"""Unit tests for Client protocol."""

from unittest.mock import Mock

from mail_client_api import Client
from message import Message


class TestClientProtocol:
    """Test Client protocol interface."""

    def test_client_protocol_methods(self) -> None:
        """Test that Client protocol defines required methods."""
        # Create mock that conforms to Client protocol
        mock_client = Mock(spec=Client)
        mock_message = Mock(spec=Message)

        # Configure mock returns
        mock_client.get_messages.return_value = iter([mock_message])
        mock_client.send_message.return_value = True
        mock_client.delete_message.return_value = True
        mock_client.mark_as_read.return_value = True

        # Verify protocol compliance
        assert isinstance(mock_client, Client)

        # Test get_messages
        messages = mock_client.get_messages()
        assert hasattr(messages, "__iter__") and hasattr(messages, "__next__")
        message_list = list(messages)
        assert len(message_list) == 1
        assert isinstance(message_list[0], Message)

        # Test send_message
        result = mock_client.send_message("to@example.com", "Subject", "Body")
        assert result is True
        mock_client.send_message.assert_called_with("to@example.com", "Subject", "Body")

        # Test delete_message
        result = mock_client.delete_message("msg-id")
        assert result is True
        mock_client.delete_message.assert_called_with("msg-id")

        # Test mark_as_read
        result = mock_client.mark_as_read("msg-id")
        assert result is True
        mock_client.mark_as_read.assert_called_with("msg-id")

    def test_client_protocol_runtime_checkable(self) -> None:
        """Test that Client protocol is runtime checkable."""
        mock_client = Mock()
        mock_client.get_messages = Mock(return_value=iter([]))
        mock_client.send_message = Mock(return_value=True)
        mock_client.delete_message = Mock(return_value=True)
        mock_client.mark_as_read = Mock(return_value=True)

        # Should pass runtime check
        assert isinstance(mock_client, Client)

    def test_client_protocol_missing_methods(self) -> None:
        """Test that objects missing required methods fail runtime check."""

        class IncompleteClient:
            def get_messages(self) -> None:
                return iter([])  # type: ignore[return-value]

            # Missing send_message, delete_message, mark_as_read methods

        incomplete_client = IncompleteClient()

        # Should fail runtime check
        assert not isinstance(incomplete_client, Client)

    def test_get_messages_returns_iterator(self) -> None:
        """Test that get_messages returns proper iterator."""
        mock_client = Mock(spec=Client)
        mock_messages = [Mock(spec=Message) for _ in range(3)]
        mock_client.get_messages.return_value = iter(mock_messages)

        messages = mock_client.get_messages()

        # Verify it's an iterator
        assert hasattr(messages, "__iter__")
        assert hasattr(messages, "__next__")

        # Verify content
        message_list = list(messages)
        assert len(message_list) == 3
        for msg in message_list:
            assert isinstance(msg, Message)
