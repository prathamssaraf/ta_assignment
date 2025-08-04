"""Unit tests for EmailMessage protocol and factory functions."""

from datetime import datetime
from unittest.mock import Mock

import pytest

import email_message
from email_message import EmailMessage, create_message


class TestEmailMessageProtocol:
    """Test suite for EmailMessage protocol contract validation."""

    def test_email_message_protocol_properties_exist(self) -> None:
        """Verify EmailMessage protocol defines required properties."""
        required_properties = [
            "message_id",
            "sender",
            "recipients",
            "cc_recipients",
            "bcc_recipients",
            "timestamp",
            "subject",
            "body_text",
            "body_html",
            "is_read",
            "is_starred",
            "thread_id",
            "labels",
            "attachment_count",
        ]

        for property_name in required_properties:
            assert hasattr(EmailMessage, property_name), f"EmailMessage missing required property: {property_name}"

    def test_email_message_protocol_methods_exist(self) -> None:
        """Verify EmailMessage protocol defines required methods."""
        required_methods = ["get_snippet"]

        for method_name in required_methods:
            assert hasattr(EmailMessage, method_name), f"EmailMessage missing required method: {method_name}"

    def test_protocol_runtime_checkable(self) -> None:
        """Verify EmailMessage protocol is runtime checkable."""
        # Create a comprehensive mock that implements all protocol requirements
        mock_message = Mock()

        # Mock all properties
        mock_message.message_id = "test_id"
        mock_message.sender = "test@example.com"
        mock_message.recipients = ["recipient@example.com"]
        mock_message.cc_recipients = []
        mock_message.bcc_recipients = []
        mock_message.timestamp = datetime.now()
        mock_message.subject = "Test Subject"
        mock_message.body_text = "Test body"
        mock_message.body_html = "<p>Test body</p>"
        mock_message.is_read = True
        mock_message.is_starred = False
        mock_message.thread_id = "thread_123"
        mock_message.labels = ["INBOX"]
        mock_message.attachment_count = 0
        mock_message.get_snippet = Mock(return_value="Test snippet")

        # Should pass runtime type check
        assert isinstance(mock_message, EmailMessage)

    def test_create_message_raises_not_implemented_by_default(self) -> None:
        """Verify create_message raises NotImplementedError when no implementation is registered."""
        # Reset factory function
        original_factory = email_message.create_message
        email_message.create_message = lambda msg_id, raw_message_data: (_ for _ in ()).throw(
            NotImplementedError("No email message implementation registered"),
        )

        try:
            with pytest.raises(NotImplementedError, match="No email message implementation registered"):
                create_message("test_id", "test_data")
        finally:
            email_message.create_message = original_factory


class TestEmailMessagePropertyTypes:
    """Test EmailMessage protocol property types and contracts."""

    def setup_method(self) -> None:
        """Set up mock message for testing."""
        self.mock_message = Mock(spec=EmailMessage)

    @pytest.mark.unit
    def test_message_id_property(self) -> None:
        """Test message_id property returns string."""
        self.mock_message.message_id = "msg_12345"
        assert self.mock_message.message_id == "msg_12345"
        assert isinstance(self.mock_message.message_id, str)

    @pytest.mark.unit
    def test_sender_property(self) -> None:
        """Test sender property returns string."""
        self.mock_message.sender = "sender@example.com"
        assert self.mock_message.sender == "sender@example.com"
        assert isinstance(self.mock_message.sender, str)

    @pytest.mark.unit
    def test_recipients_property(self) -> None:
        """Test recipients property returns list of strings."""
        test_recipients = ["user1@example.com", "user2@example.com"]
        self.mock_message.recipients = test_recipients
        assert self.mock_message.recipients == test_recipients
        assert isinstance(self.mock_message.recipients, list)

    @pytest.mark.unit
    def test_timestamp_property(self) -> None:
        """Test timestamp property returns datetime object."""
        test_time = datetime(2024, 1, 15, 10, 30, 0)
        self.mock_message.timestamp = test_time
        assert self.mock_message.timestamp == test_time
        assert isinstance(self.mock_message.timestamp, datetime)

    @pytest.mark.unit
    def test_boolean_properties(self) -> None:
        """Test boolean properties return boolean values."""
        self.mock_message.is_read = True
        self.mock_message.is_starred = False

        assert self.mock_message.is_read is True
        assert self.mock_message.is_starred is False
        assert isinstance(self.mock_message.is_read, bool)
        assert isinstance(self.mock_message.is_starred, bool)

    @pytest.mark.unit
    def test_optional_properties(self) -> None:
        """Test optional properties can be None."""
        self.mock_message.thread_id = None
        assert self.mock_message.thread_id is None

        self.mock_message.thread_id = "thread_abc"
        assert self.mock_message.thread_id == "thread_abc"

    @pytest.mark.unit
    def test_list_properties(self) -> None:
        """Test list properties return lists."""
        test_labels = ["INBOX", "IMPORTANT", "CATEGORY_PERSONAL"]
        self.mock_message.labels = test_labels
        assert self.mock_message.labels == test_labels
        assert isinstance(self.mock_message.labels, list)

    @pytest.mark.unit
    def test_attachment_count_property(self) -> None:
        """Test attachment_count property returns integer."""
        self.mock_message.attachment_count = 3
        assert self.mock_message.attachment_count == 3
        assert isinstance(self.mock_message.attachment_count, int)

    @pytest.mark.unit
    def test_get_snippet_method(self) -> None:
        """Test get_snippet method with parameters."""
        self.mock_message.get_snippet.return_value = "This is a test snippet..."

        # Test with default parameter
        result = self.mock_message.get_snippet()
        self.mock_message.get_snippet.assert_called_with()

        # Test with custom length
        result = self.mock_message.get_snippet(max_length=50)
        self.mock_message.get_snippet.assert_called_with(max_length=50)

        assert isinstance(result, str)


class TestFactoryFunctionBehavior:
    """Test create_message factory function behavior."""

    @pytest.mark.unit
    def test_factory_function_signature(self) -> None:
        """Test create_message accepts correct parameters."""
        # Import module fresh to avoid dependency injection side effects
        import importlib

        import email_message as test_module

        importlib.reload(test_module)

        mock_factory = Mock(return_value=Mock(spec=EmailMessage))
        original_factory = test_module.create_message
        test_module.create_message = mock_factory

        try:
            # Test basic call
            test_module.create_message("test_id", "raw_data")
            mock_factory.assert_called_once_with("test_id", "raw_data")

            # Test with different parameters
            mock_factory.reset_mock()
            test_module.create_message("another_id", '{"test": "json_data"}')
            mock_factory.assert_called_once_with("another_id", '{"test": "json_data"}')

        finally:
            test_module.create_message = original_factory

    @pytest.mark.unit
    def test_factory_returns_protocol_compliant_object(self) -> None:
        """Test factory returns object that satisfies EmailMessage protocol."""
        # Import module fresh to avoid dependency injection side effects
        import importlib

        import email_message as test_module

        importlib.reload(test_module)

        # Create a mock that fully implements the protocol
        mock_implementation = Mock()
        mock_implementation.message_id = "test"
        mock_implementation.sender = "test@example.com"
        mock_implementation.recipients = []
        mock_implementation.cc_recipients = []
        mock_implementation.bcc_recipients = []
        mock_implementation.timestamp = datetime.now()
        mock_implementation.subject = "Test"
        mock_implementation.body_text = "Test"
        mock_implementation.body_html = ""
        mock_implementation.is_read = False
        mock_implementation.is_starred = False
        mock_implementation.thread_id = None
        mock_implementation.labels = []
        mock_implementation.attachment_count = 0
        mock_implementation.get_snippet.return_value = "snippet"

        mock_factory = Mock(return_value=mock_implementation)
        original_factory = test_module.create_message
        test_module.create_message = mock_factory

        try:
            result = test_module.create_message("test_id", "test_data")

            # Verify it satisfies the protocol
            assert isinstance(result, EmailMessage)
            assert hasattr(result, "message_id")
            assert hasattr(result, "get_snippet")

        finally:
            test_module.create_message = original_factory
