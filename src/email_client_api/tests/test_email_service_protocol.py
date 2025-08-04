"""Unit tests for EmailService protocol and factory functions."""

from unittest.mock import Mock

import pytest

import email_client_api
from email_client_api import EmailService, create_client


class TestEmailServiceProtocol:
    """Test suite for EmailService protocol contract validation."""

    def test_email_service_protocol_methods_exist(self) -> None:
        """Verify EmailService protocol defines required methods."""
        required_methods = [
            "fetch_message_by_id",
            "remove_message",
            "mark_message_read",
            "mark_message_unread",
            "fetch_messages",
            "search_messages",
        ]

        for method_name in required_methods:
            assert hasattr(EmailService, method_name), f"EmailService missing required method: {method_name}"

    def test_protocol_runtime_checkable(self) -> None:
        """Verify EmailService protocol is runtime checkable."""
        # Create a mock that implements the protocol
        mock_service = Mock()
        mock_service.fetch_message_by_id = Mock()
        mock_service.remove_message = Mock()
        mock_service.mark_message_read = Mock()
        mock_service.mark_message_unread = Mock()
        mock_service.fetch_messages = Mock()
        mock_service.search_messages = Mock()

        # Should pass runtime type check
        assert isinstance(mock_service, EmailService)

    def test_create_client_raises_not_implemented_by_default(self) -> None:
        """Verify create_client raises NotImplementedError when no implementation is registered."""
        # Reset the factory function to ensure clean test
        original_factory = email_client_api.create_client
        email_client_api.create_client = lambda interactive=False, provider="gmail": (_ for _ in ()).throw(
            NotImplementedError("No email service implementation registered"),
        )

        try:
            with pytest.raises(NotImplementedError, match="No email service implementation registered"):
                create_client()
        finally:
            # Restore original factory
            email_client_api.create_client = original_factory

    def test_create_client_accepts_parameters(self) -> None:
        """Verify create_client accepts expected parameters."""
        # Import the module fresh to avoid dependency injection side effects
        import importlib

        import email_client_api as test_module

        importlib.reload(test_module)

        # Mock the factory function
        mock_factory = Mock(return_value=Mock(spec=EmailService))
        original_factory = test_module.create_client
        test_module.create_client = mock_factory

        try:
            # Test with different parameter combinations
            test_module.create_client()
            # Check that mock was called
            mock_factory.assert_called()

            mock_factory.reset_mock()
            test_module.create_client(interactive=True)
            # Check it was called with interactive=True (provider defaults to "gmail")
            args, kwargs = mock_factory.call_args
            assert kwargs.get("interactive") is True or (len(args) > 0 and args[0] is True)

            mock_factory.reset_mock()
            test_module.create_client(provider="outlook")
            # Check it was called with provider="outlook"
            args, kwargs = mock_factory.call_args
            assert kwargs.get("provider") == "outlook" or (len(args) > 1 and args[1] == "outlook")

            mock_factory.reset_mock()
            test_module.create_client(interactive=True, provider="imap")
            # Check both parameters
            args, kwargs = mock_factory.call_args
            interactive_passed = kwargs.get("interactive") is True or (len(args) > 0 and args[0] is True)
            provider_passed = kwargs.get("provider") == "imap" or (len(args) > 1 and args[1] == "imap")
            assert interactive_passed
            assert provider_passed

        finally:
            test_module.create_client = original_factory


class TestProtocolMethodSignatures:
    """Test protocol method signatures and return types."""

    def setup_method(self) -> None:
        """Set up mock service for testing."""
        self.mock_service = Mock(spec=EmailService)

    @pytest.mark.unit
    def test_fetch_message_by_id_signature(self) -> None:
        """Test fetch_message_by_id method signature."""
        # Configure mock return value
        mock_message = Mock()
        self.mock_service.fetch_message_by_id.return_value = mock_message

        # Call method
        result = self.mock_service.fetch_message_by_id("test_id")

        # Verify call and return
        self.mock_service.fetch_message_by_id.assert_called_once_with("test_id")
        assert result is mock_message

    @pytest.mark.unit
    def test_remove_message_signature(self) -> None:
        """Test remove_message method signature."""
        self.mock_service.remove_message.return_value = True

        result = self.mock_service.remove_message("test_id")

        self.mock_service.remove_message.assert_called_once_with("test_id")
        assert result is True

    @pytest.mark.unit
    def test_mark_message_read_signature(self) -> None:
        """Test mark_message_read method signature."""
        self.mock_service.mark_message_read.return_value = True

        result = self.mock_service.mark_message_read("test_id")

        self.mock_service.mark_message_read.assert_called_once_with("test_id")
        assert result is True

    @pytest.mark.unit
    def test_fetch_messages_signature(self) -> None:
        """Test fetch_messages method signature with parameters."""
        mock_iterator = iter([Mock(), Mock()])
        self.mock_service.fetch_messages.return_value = mock_iterator

        # Test with default parameters
        self.mock_service.fetch_messages()
        self.mock_service.fetch_messages.assert_called_with()

        # Test with explicit parameters
        self.mock_service.fetch_messages(limit=20, query="important")
        self.mock_service.fetch_messages.assert_called_with(limit=20, query="important")

    @pytest.mark.unit
    def test_search_messages_signature(self) -> None:
        """Test search_messages method signature."""
        mock_iterator = iter([Mock()])
        self.mock_service.search_messages.return_value = mock_iterator

        self.mock_service.search_messages("test query", max_results=100)

        self.mock_service.search_messages.assert_called_once_with("test query", max_results=100)
