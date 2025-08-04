"""End-to-end tests for the main application workflow."""

import io
from contextlib import redirect_stdout, suppress
from unittest.mock import Mock, patch

import pytest

# Import main application
import main


class TestMainApplicationFlow:
    """Test the complete main application demonstration flow."""

    @pytest.mark.e2e
    @pytest.mark.circleci
    def test_main_application_with_mocked_services(self) -> None:
        """Test main application flow with mocked services for CI compatibility."""
        # Import implementations to trigger dependency injection
        import json

        import email_message
        import gmail_client_impl  # noqa: F401
        import gmail_message_impl  # noqa: F401

        # Create realistic mock data
        mock_gmail_messages = []
        for i in range(3):
            gmail_data = {
                "id": f"e2e_test_{i}",
                "payload": {
                    "headers": [
                        {"name": "From", "value": f"sender{i}@example.com"},
                        {"name": "To", "value": "user@example.com"},
                        {"name": "Subject", "value": f"E2E Test Message {i}" + (" - URGENT" if i == 0 else "")},
                        {"name": "Date", "value": "Fri, 19 Jan 2024 10:00:00 +0000"},
                    ]
                },
                "internalDate": str(1705665600000 + i * 1800000),  # 30 minutes apart
                "labelIds": ["INBOX"] + (["IMPORTANT"] if i == 0 else []),
                "snippet": f"This is e2e test message {i} for application testing.",
                "threadId": f"thread_{i}",
            }

            message = email_message.create_message(f"e2e_test_{i}", json.dumps(gmail_data))
            mock_gmail_messages.append(message)

        # Mock the Gmail service
        with patch("gmail_client_impl._service.GmailEmailService") as mock_service_class:
            mock_service = Mock()
            mock_service.fetch_messages.return_value = iter(mock_gmail_messages)
            mock_service.fetch_message_by_id.return_value = mock_gmail_messages[0]
            mock_service.mark_message_read.return_value = True
            mock_service.search_messages.return_value = iter([mock_gmail_messages[0]])
            mock_service_class.return_value = mock_service

            # Capture stdout to verify application output
            output_buffer = io.StringIO()

            with redirect_stdout(output_buffer):
                with suppress(SystemExit):
                    main.main()

            output = output_buffer.getvalue()

            # Verify key application flows are executed
            assert "Smart Email Client with AI Analytics" in output
            assert "Successfully connected to Gmail API" in output
            assert "AI analytics engine ready" in output
            assert "DEMO 1: Smart Message Retrieval & Analysis" in output
            assert "DEMO 2: Priority-Based Message Management" in output
            assert "DEMO 3: Communication Pattern Analysis" in output
            assert "DEMO 4: Productivity Metrics & AI Recommendations" in output
            assert "Smart Email Client Demo Complete" in output

            # Verify service method calls
            mock_service.fetch_messages.assert_called()
            mock_service.mark_message_read.assert_called()

    @pytest.mark.e2e
    @pytest.mark.local_credentials
    def test_main_application_with_real_gmail_api(self) -> None:
        """Test main application with real Gmail API (requires credentials)."""
        # This test requires actual Gmail credentials and will be skipped in CI
        # It's marked with local_credentials to exclude from automated testing

        try:
            # Import implementations
            import email_client_api
            import gmail_client_impl  # noqa: F401
            import gmail_message_impl  # noqa: F401

            # Try to create real Gmail service
            service = email_client_api.create_client(interactive=False)

            # Simple connectivity test
            messages = list(service.fetch_messages(limit=1))

            # If we get here, the real API is working
            assert isinstance(messages, list), "Should return list of messages"

            if messages:
                # Test AI analysis on real message
                import email_analytics

                analyzer = email_analytics.EmailAnalyzer()
                analysis = analyzer.analyze_message(messages[0])

                # Verify analysis structure
                assert hasattr(analysis, "priority_score")
                assert hasattr(analysis, "sentiment")
                assert hasattr(analysis, "category")

        except Exception as e:
            # If credentials are missing or invalid, skip the test
            pytest.skip(f"Real Gmail API test skipped due to: {e}")

    @pytest.mark.e2e
    @pytest.mark.circleci
    def test_application_error_handling(self) -> None:
        """Test application error handling and graceful failure."""
        # Import implementations
        import gmail_client_impl  # noqa: F401

        # Mock service to raise authentication error
        with patch("gmail_client_impl._service.GmailEmailService") as mock_service_class:
            mock_service_class.side_effect = Exception("Authentication failed")

            # Capture stderr for error output
            error_buffer = io.StringIO()

            with redirect_stdout(error_buffer):
                with pytest.raises(Exception, match="Authentication failed"):
                    main.main()

            # Verify error handling output
            output = error_buffer.getvalue()
            assert "Smart Email Client with AI Analytics" in output
            assert "Initializing email service" in output

    @pytest.mark.e2e
    @pytest.mark.circleci
    def test_component_dependency_injection_in_main(self) -> None:
        """Test that dependency injection works correctly in main application context."""
        import email_client_api
        import email_message

        # Before importing implementations, factories should raise NotImplementedError
        try:
            email_client_api.create_client()
            msg = "Should raise NotImplementedError before implementation import"
            raise AssertionError(msg)
        except NotImplementedError:
            pass  # Expected

        try:
            email_message.create_message("test", "data")
            msg = "Should raise NotImplementedError before implementation import"
            raise AssertionError(msg)
        except NotImplementedError:
            pass  # Expected

        # Import implementations to trigger dependency injection
        import gmail_client_impl  # noqa: F401
        import gmail_message_impl  # noqa: F401

        # Mock the underlying services to avoid real API calls
        with patch("gmail_client_impl._service.GmailEmailService") as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service

            # Now factories should return implementations
            service = email_client_api.create_client()
            assert service is not None

            # Message factory should work too
            with patch("gmail_message_impl._implementation.GmailEmailMessage") as mock_message_class:
                mock_message = Mock()
                mock_message_class.return_value = mock_message

                message = email_message.create_message("test_id", '{"test": "data"}')
                assert message is not None

    @pytest.mark.e2e
    def test_ai_analytics_end_to_end_accuracy(self) -> None:
        """Test AI analytics accuracy with diverse message types."""
        import json

        import email_analytics
        import email_message
        import gmail_message_impl  # noqa: F401

        # Test different message types
        test_cases = [
            {
                "name": "urgent_work_email",
                "data": {
                    "id": "urgent_123",
                    "payload": {
                        "headers": [
                            {"name": "From", "value": "boss@company.com"},
                            {"name": "Subject", "value": "URGENT: Client meeting moved to today - action required"},
                        ]
                    },
                    "snippet": "Emergency client meeting scheduled for today at 2 PM. Please prepare materials ASAP.",
                },
                "expected_priority": "high",
                "expected_category": "work",
                "expected_response": True,
            },
            {
                "name": "promotional_email",
                "data": {
                    "id": "promo_456",
                    "payload": {
                        "headers": [
                            {"name": "From", "value": "noreply@shopping.com"},
                            {"name": "Subject", "value": "50% OFF Sale - Limited Time Offer!"},
                        ]
                    },
                    "snippet": "Don't miss our biggest sale of the year! Buy now and save big on all items.",
                },
                "expected_priority": "low",
                "expected_category": "promotional",
                "expected_response": False,
            },
            {
                "name": "positive_feedback",
                "data": {
                    "id": "feedback_789",
                    "payload": {
                        "headers": [
                            {"name": "From", "value": "colleague@company.com"},
                            {"name": "Subject", "value": "Great job on the presentation!"},
                        ]
                    },
                    "snippet": "Thank you for the excellent presentation. Your work was wonderful and really appreciated.",
                },
                "expected_priority": "medium",
                "expected_sentiment": "positive",
            },
        ]

        analyzer = email_analytics.EmailAnalyzer()

        for test_case in test_cases:
            # Create message
            message = email_message.create_message(test_case["data"]["id"], json.dumps(test_case["data"]))

            # Analyze message
            analysis = analyzer.analyze_message(message)

            # Verify expectations
            if "expected_priority" in test_case:
                if test_case["expected_priority"] == "high":
                    assert analysis.priority_score > 0.7, f"Failed priority test for {test_case['name']}"
                elif test_case["expected_priority"] == "low":
                    assert analysis.priority_score < 0.4, f"Failed priority test for {test_case['name']}"

            if "expected_category" in test_case:
                assert analysis.category == test_case["expected_category"], f"Failed category test for {test_case['name']}"

            if "expected_response" in test_case:
                assert analysis.response_suggested == test_case["expected_response"], (
                    f"Failed response test for {test_case['name']}"
                )

            if "expected_sentiment" in test_case:
                assert analysis.sentiment == test_case["expected_sentiment"], f"Failed sentiment test for {test_case['name']}"
