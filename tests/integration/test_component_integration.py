"""Integration tests for component interactions and dependency injection."""

import json
from unittest.mock import Mock, patch

import pytest

import email_analytics

# Import components to trigger dependency injection
import email_client_api
import email_message


class TestDependencyInjection:
    """Test dependency injection between components works correctly."""

    @pytest.mark.integration
    def test_email_service_factory_injection(self) -> None:
        """Test that Gmail implementation is properly injected into email_client_api."""
        # Import Gmail implementation to trigger injection
        import gmail_client_impl  # noqa: F401

        # Mock the actual Gmail service creation to avoid real API calls
        with patch("gmail_client_impl._service.GmailEmailService") as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service

            # Factory should now return Gmail implementation
            service = email_client_api.create_client(interactive=False)

            # Verify we got a service instance
            assert service is not None
            mock_service_class.assert_called_once_with(enable_interactive_auth=False)

    @pytest.mark.integration
    def test_email_message_factory_injection(self) -> None:
        """Test that Gmail message implementation is properly injected."""
        # Import Gmail message implementation to trigger injection
        import gmail_message_impl  # noqa: F401

        # Mock the Gmail message creation
        test_data = json.dumps(
            {
                "id": "test_123",
                "payload": {
                    "headers": [
                        {"name": "From", "value": "test@example.com"},
                        {"name": "Subject", "value": "Test Subject"},
                    ]
                },
                "internalDate": "1640995200000",  # Unix timestamp in milliseconds
            }
        )

        # Factory should now return Gmail message implementation
        message = email_message.create_message("test_123", test_data)

        # Verify we got a message instance with expected properties
        assert message is not None
        assert hasattr(message, "message_id")
        assert hasattr(message, "sender")
        assert hasattr(message, "subject")

    @pytest.mark.integration
    def test_end_to_end_component_flow(self) -> None:
        """Test complete component integration flow."""
        # Import all implementations
        import gmail_client_impl  # noqa: F401
        import gmail_message_impl  # noqa: F401

        # Mock Gmail service and message
        mock_gmail_data = {
            "id": "integration_test_123",
            "payload": {
                "headers": [
                    {"name": "From", "value": "integration@test.com"},
                    {"name": "To", "value": "recipient@test.com"},
                    {"name": "Subject", "value": "Integration Test Message"},
                    {"name": "Date", "value": "Mon, 1 Jan 2024 12:00:00 +0000"},
                ],
                "body": {"data": "VGhpcyBpcyBhIHRlc3QgbWVzc2FnZSBmb3IgaW50ZWdyYXRpb24gdGVzdGluZy4="},  # Base64 encoded
            },
            "internalDate": "1704110400000",
            "labelIds": ["INBOX"],
            "snippet": "This is a test message for integration testing.",
        }

        with patch("gmail_client_impl._service.GmailEmailService") as mock_service_class:
            # Set up mock service
            mock_service = Mock()
            mock_service_class.return_value = mock_service

            # Create mock message
            test_message = email_message.create_message("integration_test_123", json.dumps(mock_gmail_data))
            mock_service.fetch_message_by_id.return_value = test_message
            mock_service.fetch_messages.return_value = iter([test_message])

            # Get service through factory
            service = email_client_api.create_client(interactive=False)

            # Test message retrieval
            retrieved_message = service.fetch_message_by_id("integration_test_123")
            assert retrieved_message.message_id == "integration_test_123"

            # Test AI analysis integration
            analyzer = email_analytics.EmailAnalyzer()
            analysis = analyzer.analyze_message(retrieved_message)

            # Verify analysis results
            assert isinstance(analysis.priority_score, float)
            assert 0.0 <= analysis.priority_score <= 1.0
            assert analysis.sentiment in ["positive", "negative", "neutral"]
            assert isinstance(analysis.category, str)
            assert isinstance(analysis.estimated_reading_time, int)


class TestComponentInteraction:
    """Test interactions between different components."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        # Import implementations
        import gmail_client_impl  # noqa: F401
        import gmail_message_impl  # noqa: F401

    @pytest.mark.integration
    def test_analytics_with_real_message_structure(self) -> None:
        """Test analytics component with realistic message data."""
        # Create realistic Gmail message data
        realistic_gmail_data = {
            "id": "realistic_test_456",
            "payload": {
                "headers": [
                    {"name": "From", "value": "boss@company.com"},
                    {"name": "To", "value": "employee@company.com"},
                    {"name": "Subject", "value": "URGENT: Project deadline moved up - action required"},
                    {"name": "Date", "value": "Wed, 15 Jan 2024 14:30:00 +0000"},
                ],
                "parts": [
                    {
                        "mimeType": "text/plain",
                        "body": {
                            "data": "SGkgdGVhbSwgSSBuZWVkIHlvdXIgaW1tZWRpYXRlIGF0dGVudGlvbi4gVGhlIGNsaWVudCBoYXMgbW92ZWQgdXAgdGhlIHByb2plY3QgZGVhZGxpbmUgdG8gdGhpcyBGcmlkYXkuIFBsZWFzZSByZXNwb25kIEFTQVAgd2l0aCB5b3VyIHN0YXR1cyB1cGRhdGUuIFRoaXMgaXMgY3JpdGljYWwgZm9yIG91ciBzdWNjZXNzLg=="  # "Hi team, I need your immediate attention..."
                        },
                    }
                ],
            },
            "internalDate": "1705329000000",
            "labelIds": ["INBOX", "IMPORTANT"],
            "snippet": "Hi team, I need your immediate attention. The client has moved up the project deadline...",
            "threadId": "thread_789",
        }

        # Create message through factory
        message = email_message.create_message("realistic_test_456", json.dumps(realistic_gmail_data))

        # Analyze with AI
        analyzer = email_analytics.EmailAnalyzer()
        analysis = analyzer.analyze_message(message)

        # Verify high-priority detection
        assert analysis.priority_score > 0.7, "Should detect high priority from urgent keywords"
        assert "urgent" in analysis.urgency_indicators or "time_pressure" in analysis.urgency_indicators
        assert analysis.response_suggested is True, "Should suggest response for urgent request"
        assert analysis.category in ["work", "general"], "Should categorize as work-related"

    @pytest.mark.integration
    def test_communication_patterns_analysis(self) -> None:
        """Test communication patterns analysis with multiple messages."""
        # Create multiple realistic messages
        messages = []

        for i in range(3):
            gmail_data = {
                "id": f"pattern_test_{i}",
                "payload": {
                    "headers": [
                        {"name": "From", "value": f"sender{i % 2}@company.com"},
                        {"name": "Subject", "value": f"Test message {i}"},
                        {"name": "Date", "value": "Mon, 1 Jan 2024 12:00:00 +0000"},
                    ]
                },
                "internalDate": str(1704110400000 + i * 3600000),  # 1 hour apart
                "labelIds": ["INBOX"],
                "snippet": f"This is test message {i} for pattern analysis.",
            }

            message = email_message.create_message(f"pattern_test_{i}", json.dumps(gmail_data))
            messages.append(message)

        # Analyze patterns
        analyzer = email_analytics.EmailAnalyzer()
        patterns = analyzer.analyze_communication_patterns(messages)

        # Verify pattern analysis
        assert patterns.total_messages_analyzed == 3
        assert isinstance(patterns.most_frequent_senders, list)
        assert len(patterns.most_frequent_senders) > 0
        assert isinstance(patterns.category_distribution, dict)

    @pytest.mark.integration
    @pytest.mark.circleci
    def test_error_handling_across_components(self) -> None:
        """Test error handling propagation between components."""
        # Import implementations
        import gmail_client_impl  # noqa: F401

        with patch("gmail_client_impl._service.GmailEmailService") as mock_service_class:
            # Configure service to raise an exception
            mock_service = Mock()
            mock_service.fetch_message_by_id.side_effect = Exception("Gmail API Error")
            mock_service_class.return_value = mock_service

            # Get service through factory
            service = email_client_api.create_client(interactive=False)

            # Test error propagation
            with pytest.raises(Exception, match="Gmail API Error"):
                service.fetch_message_by_id("nonexistent_id")

    @pytest.mark.integration
    @pytest.mark.circleci
    def test_mock_based_full_workflow(self) -> None:
        """Test full workflow using mocks for CI compatibility."""
        # Import all components
        import gmail_client_impl  # noqa: F401
        import gmail_message_impl  # noqa: F401

        # Mock data for complete workflow
        workflow_message_data = {
            "id": "workflow_test_789",
            "payload": {
                "headers": [
                    {"name": "From", "value": "client@important.com"},
                    {"name": "Subject", "value": "Please review attached proposal - feedback needed"},
                    {"name": "Date", "value": "Thu, 18 Jan 2024 09:15:00 +0000"},
                ]
            },
            "internalDate": "1705570500000",
            "labelIds": ["INBOX"],
            "snippet": "Please review the attached proposal and provide feedback by end of week.",
        }

        with patch("gmail_client_impl._service.GmailEmailService") as mock_service_class:
            # Setup mock service
            mock_service = Mock()
            test_message = email_message.create_message("workflow_test_789", json.dumps(workflow_message_data))

            mock_service.fetch_messages.return_value = iter([test_message])
            mock_service.fetch_message_by_id.return_value = test_message
            mock_service.mark_message_read.return_value = True
            mock_service_class.return_value = mock_service

            # Execute complete workflow
            service = email_client_api.create_client(interactive=False)
            analyzer = email_analytics.EmailAnalyzer()

            # 1. Fetch messages
            messages = list(service.fetch_messages(limit=1))
            assert len(messages) == 1

            # 2. Analyze message
            analysis = analyzer.analyze_message(messages[0])
            assert analysis.response_suggested is True  # Should suggest response for "feedback needed"

            # 3. Mark as read (if high priority)
            if analysis.priority_score > 0.5:
                success = service.mark_message_read(messages[0].message_id)
                assert success is True

            # 4. Generate productivity metrics
            metrics = analyzer.generate_productivity_metrics(messages)
            assert isinstance(metrics.recommendations, list)
            assert len(metrics.recommendations) > 0
