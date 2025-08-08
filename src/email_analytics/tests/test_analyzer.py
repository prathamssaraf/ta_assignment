"""Unit tests for EmailAnalyzer and AI analysis components."""

from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

import pytest

import email_message
from email_analytics import AnalysisReport, EmailAnalyzer


class TestEmailAnalyzer:
    """Test suite for EmailAnalyzer AI analysis functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.analyzer = EmailAnalyzer()

        # Create a comprehensive mock message
        self.mock_message = Mock(spec=email_message.EmailMessage)
        self.mock_message.message_id = "test_123"
        self.mock_message.sender = "important@work.com"
        self.mock_message.recipients = ["me@example.com"]
        self.mock_message.cc_recipients = []
        self.mock_message.bcc_recipients = []
        self.mock_message.timestamp = datetime.now(tz=UTC)
        self.mock_message.subject = "Urgent: Please review the quarterly budget proposal"
        self.mock_message.body_text = "Hi team, we need your urgent feedback on the attached budget proposal. The deadline is approaching fast. Please respond ASAP with your comments. Thanks for your excellent work!"
        self.mock_message.body_html = "<p>Hi team, we need your urgent feedback...</p>"
        self.mock_message.is_read = False
        self.mock_message.is_starred = True
        self.mock_message.thread_id = "thread_456"
        self.mock_message.labels = ["INBOX", "WORK"]
        self.mock_message.attachment_count = 1
        self.mock_message.get_snippet.return_value = "Hi team, we need your urgent feedback on the attached budget proposal..."

    @pytest.mark.unit
    def test_analyzer_initialization(self) -> None:
        """Test EmailAnalyzer initializes correctly."""
        analyzer = EmailAnalyzer()

        # Verify analyzer has required attributes
        assert hasattr(analyzer, "HIGH_PRIORITY_KEYWORDS")
        assert hasattr(analyzer, "POSITIVE_WORDS")
        assert hasattr(analyzer, "NEGATIVE_WORDS")
        assert hasattr(analyzer, "CATEGORY_PATTERNS")
        assert hasattr(analyzer, "SPAM_INDICATORS")

    @pytest.mark.unit
    def test_analyze_message_returns_analysis_report(self) -> None:
        """Test analyze_message returns properly structured AnalysisReport."""
        result = self.analyzer.analyze_message(self.mock_message)

        # Verify return type
        assert isinstance(result, AnalysisReport)

        # Verify all required fields exist
        assert hasattr(result, "priority_score")
        assert hasattr(result, "sentiment")
        assert hasattr(result, "sentiment_confidence")
        assert hasattr(result, "category")
        assert hasattr(result, "category_confidence")
        assert hasattr(result, "urgency_indicators")
        assert hasattr(result, "spam_probability")
        assert hasattr(result, "estimated_reading_time")
        assert hasattr(result, "key_topics")
        assert hasattr(result, "response_suggested")

    @pytest.mark.unit
    def test_priority_scoring_high_priority_keywords(self) -> None:
        """Test priority scoring detects high-priority keywords."""
        # Test message with high priority keywords
        self.mock_message.subject = "URGENT: Critical system failure - action required"
        self.mock_message.body_text = "Emergency situation requires immediate attention. Please respond ASAP."

        result = self.analyzer.analyze_message(self.mock_message)

        # Should detect high priority
        assert result.priority_score > 0.7
        assert "urgent" in " ".join(result.urgency_indicators).lower() or len(result.urgency_indicators) > 0

    @pytest.mark.unit
    def test_priority_scoring_low_priority_message(self) -> None:
        """Test priority scoring for low-priority messages."""
        # Test message with promotional content
        self.mock_message.subject = "Weekly newsletter - Latest deals and promotions"
        self.mock_message.body_text = (
            "Check out our latest offers and discounts. Subscribe for more updates. Do not reply to this automated message."
        )
        self.mock_message.sender = "noreply@marketing.com"

        result = self.analyzer.analyze_message(self.mock_message)

        # Should have lower priority
        assert result.priority_score < 0.6

    @pytest.mark.unit
    def test_sentiment_analysis_positive(self) -> None:
        """Test sentiment analysis detects positive sentiment."""
        self.mock_message.subject = "Congratulations on your excellent work!"
        self.mock_message.body_text = (
            "Thank you for the wonderful presentation. Your work is awesome and we really appreciate your efforts. Great job!"
        )

        result = self.analyzer.analyze_message(self.mock_message)

        assert result.sentiment == "positive"
        assert result.sentiment_confidence > 0.0

    @pytest.mark.unit
    def test_sentiment_analysis_negative(self) -> None:
        """Test sentiment analysis detects negative sentiment."""
        self.mock_message.subject = "Problem with system - urgent issue"
        self.mock_message.body_text = (
            "We have a serious problem with the system. This is a bad situation and we are very concerned about the failures."
        )

        result = self.analyzer.analyze_message(self.mock_message)

        assert result.sentiment == "negative"
        assert result.sentiment_confidence > 0.0

    @pytest.mark.unit
    def test_sentiment_analysis_neutral(self) -> None:
        """Test sentiment analysis handles neutral content."""
        self.mock_message.subject = "Meeting scheduled for tomorrow"
        self.mock_message.body_text = (
            "The meeting is scheduled for 2 PM in conference room A. Please bring the required documents."
        )

        result = self.analyzer.analyze_message(self.mock_message)

        assert result.sentiment == "neutral"

    @pytest.mark.unit
    def test_category_classification_work(self) -> None:
        """Test category classification identifies work emails."""
        self.mock_message.subject = "Project deadline and team meeting"
        self.mock_message.body_text = "We need to discuss the project deadline with the team. The client expects the proposal by Friday. Please coordinate with your manager."

        result = self.analyzer.analyze_message(self.mock_message)

        assert result.category == "work"
        assert result.category_confidence > 0.0

    @pytest.mark.unit
    def test_category_classification_promotional(self) -> None:
        """Test category classification identifies promotional emails."""
        self.mock_message.subject = "Special sale - 50% discount on all items!"
        self.mock_message.body_text = (
            "Limited time offer! Buy now and save big. Free shipping on all orders. Don't miss this amazing deal!"
        )

        result = self.analyzer.analyze_message(self.mock_message)

        assert result.category == "promotional"

    @pytest.mark.unit
    def test_spam_detection_high_spam_probability(self) -> None:
        """Test spam detection identifies likely spam."""
        self.mock_message.subject = "CONGRATULATIONS!!! YOU WON $1 MILLION DOLLARS!!!"
        self.mock_message.body_text = (
            "You are the lottery winner! Click here now to claim your prize! Act now! Limited time! Free money!"
        )
        self.mock_message.sender = "noreply@suspicious-domain.com"

        result = self.analyzer.analyze_message(self.mock_message)

        assert result.spam_probability > 0.5

    @pytest.mark.unit
    def test_spam_detection_low_spam_probability(self) -> None:
        """Test spam detection identifies legitimate messages."""
        self.mock_message.subject = "Team meeting agenda for Thursday"
        self.mock_message.body_text = "Hi everyone, please find the agenda for our Thursday team meeting. Let me know if you have any additional items to discuss."
        self.mock_message.sender = "manager@company.com"

        result = self.analyzer.analyze_message(self.mock_message)

        assert result.spam_probability < 0.3

    @pytest.mark.unit
    def test_reading_time_estimation(self) -> None:
        """Test reading time estimation is reasonable."""
        # Short message
        self.mock_message.body_text = "Quick update: Meeting moved to 3 PM."
        result = self.analyzer.analyze_message(self.mock_message)
        assert result.estimated_reading_time >= 30  # Minimum 30 seconds

        # Longer message
        long_text = " ".join(["This is a longer message with many words."] * 50)
        self.mock_message.body_text = long_text
        result = self.analyzer.analyze_message(self.mock_message)
        assert result.estimated_reading_time > 60  # Should be more than 1 minute

    @pytest.mark.unit
    def test_response_suggestion_with_questions(self) -> None:
        """Test response suggestion detects questions."""
        self.mock_message.body_text = (
            "Can you please review the document? What do you think about the proposal? Let me know your thoughts."
        )

        result = self.analyzer.analyze_message(self.mock_message)

        assert result.response_suggested is True

    @pytest.mark.unit
    def test_response_suggestion_automated_emails(self) -> None:
        """Test response suggestion ignores automated emails."""
        self.mock_message.body_text = (
            "This is an automated notification. Do not reply to this message. Your account has been updated."
        )
        self.mock_message.sender = "noreply@system.com"

        result = self.analyzer.analyze_message(self.mock_message)

        assert result.response_suggested is False

    @pytest.mark.unit
    def test_key_topics_extraction(self) -> None:
        """Test key topics extraction from message content."""
        self.mock_message.subject = "Quarterly budget review meeting"
        self.mock_message.body_text = "We need to review the quarterly budget and discuss financial projections for the next quarter. Please prepare your departmental budget reports."

        result = self.analyzer.analyze_message(self.mock_message)

        assert isinstance(result.key_topics, list)
        assert len(result.key_topics) > 0
        # Should extract relevant keywords
        topic_text = " ".join(result.key_topics).lower()
        assert any(keyword in topic_text for keyword in ["budget", "quarterly", "review", "meeting"])

    @pytest.mark.unit
    def test_urgency_indicators_detection(self) -> None:
        """Test urgency indicators detection."""
        self.mock_message.subject = "URGENT: Action required ASAP!!!"
        self.mock_message.body_text = (
            "This is URGENT and requires immediate action. Deadline is approaching. Please respond ASAP!"
        )

        result = self.analyzer.analyze_message(self.mock_message)

        assert isinstance(result.urgency_indicators, list)
        assert len(result.urgency_indicators) > 0
        # Should detect multiple urgency indicators
        indicators_str = " ".join(result.urgency_indicators).lower()
        assert "caps" in indicators_str or "time" in indicators_str or "action" in indicators_str


class TestCommunicationPatternsAnalysis:
    """Test communication patterns analysis functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.analyzer = EmailAnalyzer()

        # Create multiple mock messages with different characteristics
        self.messages = []
        for i in range(5):
            mock_msg = Mock(spec=email_message.EmailMessage)
            mock_msg.message_id = f"msg_{i}"
            mock_msg.sender = f"user{i % 3}@example.com"  # 3 different senders
            mock_msg.timestamp = datetime.now(tz=UTC) - timedelta(days=i, hours=i * 2)
            mock_msg.subject = f"Test message {i}"
            mock_msg.body_text = f"This is test message number {i} with some content."
            mock_msg.is_read = i % 2 == 0  # Alternate read/unread
            mock_msg.labels = ["INBOX"]
            self.messages.append(mock_msg)

    @pytest.mark.unit
    def test_analyze_communication_patterns_empty_list(self) -> None:
        """Test communication patterns analysis with empty message list."""
        result = self.analyzer.analyze_communication_patterns([])

        assert result.total_messages_analyzed == 0
        assert result.avg_response_time is None
        assert result.peak_activity_hours == []
        assert result.most_frequent_senders == []
        assert result.category_distribution == {}
        assert result.sentiment_trend == {}

    @pytest.mark.unit
    def test_analyze_communication_patterns_with_messages(self) -> None:
        """Test communication patterns analysis with sample messages."""
        result = self.analyzer.analyze_communication_patterns(self.messages)

        assert result.total_messages_analyzed == 5
        assert isinstance(result.peak_activity_hours, list)
        assert isinstance(result.most_frequent_senders, list)
        assert isinstance(result.category_distribution, dict)
        assert isinstance(result.sentiment_trend, dict)

        # Verify sender frequency analysis
        assert len(result.most_frequent_senders) > 0
        sender_email, count = result.most_frequent_senders[0]
        assert "@example.com" in sender_email
        assert count > 0


class TestProductivityMetrics:
    """Test productivity metrics generation."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.analyzer = EmailAnalyzer()

    @pytest.mark.unit
    def test_generate_productivity_metrics_empty_list(self) -> None:
        """Test productivity metrics with empty message list."""
        result = self.analyzer.generate_productivity_metrics([])

        assert result.unread_priority_messages == 0
        assert result.estimated_daily_email_time == timedelta(0)
        assert result.response_efficiency_score == 1.0
        assert result.email_overload_risk == "low"
        assert isinstance(result.recommendations, list)
        assert len(result.recommendations) > 0

    @pytest.mark.unit
    def test_generate_productivity_metrics_with_high_priority_unread(self) -> None:
        """Test productivity metrics identifies high-priority unread messages."""
        # Create high-priority unread message
        mock_msg = Mock(spec=email_message.EmailMessage)
        mock_msg.message_id = "priority_msg"
        mock_msg.sender = "boss@company.com"
        mock_msg.subject = "URGENT: Critical decision needed"
        mock_msg.body_text = "This is urgent and requires immediate action from you."
        mock_msg.timestamp = datetime.now(tz=UTC)
        mock_msg.is_read = False  # Unread
        mock_msg.labels = ["INBOX", "IMPORTANT"]

        result = self.analyzer.generate_productivity_metrics([mock_msg])

        # Should detect high-priority unread message
        assert result.unread_priority_messages > 0

    @pytest.mark.unit
    def test_productivity_recommendations_generation(self) -> None:
        """Test that productivity recommendations are generated."""
        # Create a mix of messages
        messages = []
        for i in range(3):
            mock_msg = Mock(spec=email_message.EmailMessage)
            mock_msg.message_id = f"msg_{i}"
            mock_msg.sender = "sender@example.com"
            mock_msg.subject = "Regular email"
            mock_msg.body_text = "Regular content"
            mock_msg.timestamp = datetime.now(tz=UTC) - timedelta(days=i)
            mock_msg.is_read = i == 0  # First message read, others unread
            mock_msg.labels = ["INBOX"]
            messages.append(mock_msg)

        result = self.analyzer.generate_productivity_metrics(messages)

        assert isinstance(result.recommendations, list)
        assert len(result.recommendations) > 0
        # Should have meaningful recommendations
        recommendations_text = " ".join(result.recommendations).lower()
        assert any(keyword in recommendations_text for keyword in ["email", "unread", "priority", "good"])
