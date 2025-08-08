"""Email analysis engine with AI-inspired algorithms and heuristics."""

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import ClassVar, NamedTuple, Sequence

import email_message


class AnalysisReport(NamedTuple):
    """Comprehensive analysis report for a single email message."""

    priority_score: float  # 0.0 (low) to 1.0 (critical)
    sentiment: str  # positive, negative, neutral
    sentiment_confidence: float  # 0.0 to 1.0
    category: str  # work, personal, promotional, notification, etc.
    category_confidence: float  # 0.0 to 1.0
    urgency_indicators: list[str]  # List of detected urgency signals
    spam_probability: float  # 0.0 (not spam) to 1.0 (likely spam)
    estimated_reading_time: int  # Seconds
    key_topics: list[str]  # Extracted topics/keywords
    response_suggested: bool  # Whether email likely needs response


@dataclass
class CommunicationPatterns:
    """Analysis of communication patterns across multiple messages."""

    total_messages_analyzed: int
    avg_response_time: timedelta | None
    peak_activity_hours: list[int]  # Hours of day (0-23)
    most_frequent_senders: list[tuple[str, int]]  # (sender, count)
    category_distribution: dict[str, int]
    sentiment_trend: dict[str, float]  # category -> avg sentiment score


@dataclass
class ProductivityMetrics:
    """Productivity insights and recommendations."""

    unread_priority_messages: int
    estimated_daily_email_time: timedelta
    response_efficiency_score: float  # 0.0 to 1.0
    email_overload_risk: str  # low, medium, high
    recommendations: list[str]


class EmailAnalyzer:
    """AI-enhanced email analyzer using rule-based algorithms and heuristics."""

    # Class constants for email analysis
    HIGH_PRIORITY_THRESHOLD: ClassVar[float] = 0.7
    MEDIUM_OVERLOAD_THRESHOLD: ClassVar[int] = 20
    EMAIL_OVERLOAD_THRESHOLD: ClassVar[int] = 50
    POSITIVE_SENTIMENT_THRESHOLD: ClassVar[float] = 0.6
    NEGATIVE_SENTIMENT_THRESHOLD: ClassVar[float] = 0.4
    EXCESSIVE_LINKS_THRESHOLD: ClassVar[int] = 5
    MIN_MESSAGES_FOR_ANALYSIS: ClassVar[int] = 2
    SECONDS_PER_DAY: ClassVar[int] = 86400
    SECONDS_PER_HOUR: ClassVar[int] = 3600
    UNREAD_RATIO_THRESHOLD: ClassVar[float] = 0.3
    OLD_UNREAD_DAYS_THRESHOLD: ClassVar[int] = 7
    OLD_UNREAD_COUNT_THRESHOLD: ClassVar[int] = 5

    # Priority scoring keywords and weights
    HIGH_PRIORITY_KEYWORDS: ClassVar[dict[str, float]] = {
        "urgent": 0.9,
        "asap": 0.8,
        "emergency": 1.0,
        "critical": 0.9,
        "deadline": 0.7,
        "important": 0.6,
        "action required": 0.8,
        "please respond": 0.6,
        "time sensitive": 0.8,
        "priority": 0.7,
    }

    MEDIUM_PRIORITY_KEYWORDS: ClassVar[dict[str, float]] = {
        "meeting": 0.5,
        "schedule": 0.4,
        "reminder": 0.4,
        "follow up": 0.5,
        "please review": 0.5,
        "feedback": 0.4,
        "update": 0.3,
        "status": 0.3,
    }

    # Sentiment analysis keywords
    POSITIVE_WORDS: ClassVar[set[str]] = {
        "thanks",
        "thank you",
        "appreciate",
        "excellent",
        "great",
        "wonderful",
        "perfect",
        "awesome",
        "congratulations",
        "success",
        "pleased",
        "happy",
    }

    NEGATIVE_WORDS: ClassVar[set[str]] = {
        "problem",
        "issue",
        "error",
        "failed",
        "wrong",
        "bad",
        "terrible",
        "disappointed",
        "frustrated",
        "angry",
        "concerned",
        "worry",
        "urgent",
    }

    # Category classification patterns
    CATEGORY_PATTERNS: ClassVar[dict[str, list[str]]] = {
        "work": [
            r"\b(meeting|project|deadline|client|budget|proposal|contract)\b",
            r"\b(team|manager|department|office|business|corporate)\b",
        ],
        "personal": [
            r"\b(family|friend|birthday|vacation|personal|home)\b",
            r"\b(weekend|evening|dinner|party|celebration)\b",
        ],
        "promotional": [
            r"\b(sale|discount|offer|deal|promotion|marketing)\b",
            r"\b(buy now|limited time|free|save|purchase)\b",
        ],
        "notification": [
            r"\b(notification|alert|reminder|confirmation|receipt)\b",
            r"\b(account|security|password|login|verification)\b",
        ],
    }

    # Spam detection patterns
    SPAM_INDICATORS: ClassVar[list[str]] = [
        r"\b(lottery|winner|million dollars|inheritance|prince)\b",
        r"\b(click here|act now|limited time|urgent action)\b",
        r"\b(viagra|pharmacy|medication|pills)\b",
        r"[A-Z]{5,}",  # Excessive caps
        r"[!]{3,}",  # Multiple exclamation marks
    ]

    def analyze_message(self, message: email_message.EmailMessage) -> AnalysisReport:
        """Perform comprehensive analysis on a single email message."""
        content = f"{message.subject} {message.body_text}".lower()

        # Calculate priority score
        priority_score = self._calculate_priority_score(message, content)

        # Analyze sentiment
        sentiment, sentiment_confidence = self._analyze_sentiment(content)

        # Categorize message
        category, category_confidence = self._categorize_message(content)

        # Detect urgency indicators
        urgency_indicators = self._detect_urgency_indicators(content)

        # Calculate spam probability
        spam_probability = self._calculate_spam_probability(message, content)

        # Estimate reading time (average 200 words per minute)
        word_count = len(content.split())
        reading_time = max(30, (word_count / 200) * 60)  # Minimum 30 seconds

        # Extract key topics
        key_topics = self._extract_key_topics(content)

        # Determine if response is suggested
        response_suggested = self._should_suggest_response(message, content)

        return AnalysisReport(
            priority_score=priority_score,
            sentiment=sentiment,
            sentiment_confidence=sentiment_confidence,
            category=category,
            category_confidence=category_confidence,
            urgency_indicators=urgency_indicators,
            spam_probability=spam_probability,
            estimated_reading_time=int(reading_time),
            key_topics=key_topics,
            response_suggested=response_suggested,
        )

    def analyze_communication_patterns(
        self,
        messages: Sequence[email_message.EmailMessage],
    ) -> CommunicationPatterns:
        """Analyze communication patterns across multiple messages."""
        if not messages:
            return CommunicationPatterns(
                total_messages_analyzed=0,
                avg_response_time=None,
                peak_activity_hours=[],
                most_frequent_senders=[],
                category_distribution={},
                sentiment_trend={},
            )

        # Analyze timestamps for peak activity
        timestamps = [msg.timestamp for msg in messages if hasattr(msg, "timestamp")]
        hour_counts = Counter(ts.hour for ts in timestamps)
        peak_hours = [hour for hour, _ in hour_counts.most_common(3)]

        # Count senders
        sender_counts = Counter(msg.sender for msg in messages)
        top_senders = sender_counts.most_common(5)

        # Analyze categories and sentiment
        category_counts: dict[str, int] = defaultdict(int)
        sentiment_scores: dict[str, list[float]] = defaultdict(list)

        for message in messages:
            analysis = self.analyze_message(message)
            category_counts[analysis.category] += 1

            # Convert sentiment to numeric score
            sentiment_score = self._sentiment_to_score(analysis.sentiment)
            sentiment_scores[analysis.category].append(sentiment_score)

        # Calculate average sentiment by category
        sentiment_trend = {
            category: sum(scores) / len(scores) if scores else 0.0 for category, scores in sentiment_scores.items()
        }

        return CommunicationPatterns(
            total_messages_analyzed=len(messages),
            avg_response_time=self._calculate_avg_response_time(messages),
            peak_activity_hours=peak_hours,
            most_frequent_senders=top_senders,
            category_distribution=dict(category_counts),
            sentiment_trend=sentiment_trend,
        )

    def generate_productivity_metrics(
        self,
        messages: Sequence[email_message.EmailMessage],
    ) -> ProductivityMetrics:
        """Generate productivity insights and recommendations."""
        if not messages:
            return ProductivityMetrics(
                unread_priority_messages=0,
                estimated_daily_email_time=timedelta(0),
                response_efficiency_score=1.0,
                email_overload_risk="low",
                recommendations=["No messages to analyze"],
            )

        # Count high-priority unread messages
        priority_unread = sum(
            1 for msg in messages if not msg.is_read and self.analyze_message(msg).priority_score > self.HIGH_PRIORITY_THRESHOLD
        )

        # Estimate daily email processing time
        total_reading_time = sum(self.analyze_message(msg).estimated_reading_time for msg in messages)
        daily_time = timedelta(seconds=total_reading_time)

        # Calculate response efficiency (simplified heuristic)
        response_efficiency = self._calculate_response_efficiency(messages)

        # Assess email overload risk
        messages_per_day = len(messages) / max(1, (messages[-1].timestamp - messages[0].timestamp).days or 1)
        if messages_per_day > self.EMAIL_OVERLOAD_THRESHOLD:
            overload_risk = "high"
        elif messages_per_day > self.MEDIUM_OVERLOAD_THRESHOLD:
            overload_risk = "medium"
        else:
            overload_risk = "low"

        # Generate recommendations
        recommendations = self._generate_recommendations(messages, priority_unread, overload_risk)

        return ProductivityMetrics(
            unread_priority_messages=priority_unread,
            estimated_daily_email_time=daily_time,
            response_efficiency_score=response_efficiency,
            email_overload_risk=overload_risk,
            recommendations=recommendations,
        )

    # Private helper methods

    def _calculate_priority_score(self, message: email_message.EmailMessage, content: str) -> float:
        """Calculate priority score based on various factors."""
        score = 0.5  # Base score

        # Check for high priority keywords
        for keyword, weight in self.HIGH_PRIORITY_KEYWORDS.items():
            if keyword in content:
                score = min(1.0, score + weight * 0.3)

        # Check for medium priority keywords
        for keyword, weight in self.MEDIUM_PRIORITY_KEYWORDS.items():
            if keyword in content:
                score = min(1.0, score + weight * 0.2)

        # Boost score for personal emails from known contacts
        if not any(spam_word in message.sender.lower() for spam_word in ["noreply", "donotreply"]):
            score += 0.1

        # Boost for emails with questions
        if "?" in content:
            score += 0.15

        # Reduce score for automated/notification emails
        if any(auto_word in content for auto_word in ["automated", "do not reply", "noreply"]):
            score -= 0.2

        return max(0.0, min(1.0, score))

    def _analyze_sentiment(self, content: str) -> tuple[str, float]:
        """Analyze sentiment using keyword matching."""
        positive_count = sum(1 for word in self.POSITIVE_WORDS if word in content)
        negative_count = sum(1 for word in self.NEGATIVE_WORDS if word in content)

        total_sentiment_words = positive_count + negative_count

        if total_sentiment_words == 0:
            return "neutral", 0.7

        positive_ratio = positive_count / total_sentiment_words
        confidence = min(1.0, total_sentiment_words / 10)  # More words = higher confidence

        if positive_ratio > self.POSITIVE_SENTIMENT_THRESHOLD:
            return "positive", confidence
        if positive_ratio < self.NEGATIVE_SENTIMENT_THRESHOLD:
            return "negative", confidence
        return "neutral", confidence

    def _categorize_message(self, content: str) -> tuple[str, float]:
        """Categorize message based on content patterns."""
        category_scores = {}

        for category, patterns in self.CATEGORY_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                score += matches
            category_scores[category] = score

        if not category_scores or max(category_scores.values()) == 0:
            return "general", 0.5

        best_category = max(category_scores.keys(), key=lambda k: category_scores[k])
        max_score = category_scores[best_category]
        confidence = min(1.0, max_score / 5)  # Normalize confidence

        return best_category, confidence

    def _detect_urgency_indicators(self, content: str) -> list[str]:
        """Detect urgency indicators in message content."""
        indicators = []

        urgency_patterns = {
            "deadline_mention": r"\b(deadline|due date|expires|until)\b",
            "time_pressure": r"\b(asap|urgent|immediately|quickly)\b",
            "action_required": r"\b(action required|please respond|need response)\b",
            "caps_emphasis": r"\b[A-Z]{4,}\b",
            "multiple_exclamations": r"[!]{2,}",
        }

        for indicator_type, pattern in urgency_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                indicators.append(indicator_type)

        return indicators

    def _calculate_spam_probability(self, message: email_message.EmailMessage, content: str) -> float:
        """Calculate probability that message is spam."""
        spam_score = 0.0

        # Check spam indicator patterns
        for pattern in self.SPAM_INDICATORS:
            if re.search(pattern, content, re.IGNORECASE):
                spam_score += 0.2

        # Check sender reputation signals
        sender = message.sender.lower()
        if any(suspicious in sender for suspicious in ["noreply", "marketing", "promo"]):
            spam_score += 0.1

        # Check for excessive links (simplified)
        link_count = content.count("http")
        if link_count > self.EXCESSIVE_LINKS_THRESHOLD:
            spam_score += 0.2

        # Check subject line spam indicators
        subject = message.subject.lower()
        if any(spam_word in subject for spam_word in ["free", "win", "money", "deal"]):
            spam_score += 0.15

        return min(1.0, spam_score)

    def _extract_key_topics(self, content: str) -> list[str]:
        """Extract key topics/keywords from content."""
        # Simple keyword extraction (could be enhanced with NLP)
        words = re.findall(r"\b[a-zA-Z]{4,}\b", content)
        word_counts = Counter(word.lower() for word in words)

        # Filter out common words
        common_words = {"this", "that", "with", "from", "they", "have", "will", "your", "would", "could"}
        filtered_counts = {word: count for word, count in word_counts.items() if word not in common_words}

        # Return top 5 keywords
        return [word for word, _ in Counter(filtered_counts).most_common(5)]

    def _should_suggest_response(self, message: email_message.EmailMessage, content: str) -> bool:
        """Determine if a response is suggested for this message."""
        # Don't suggest response for automated emails (check first)
        if any(auto_word in content for auto_word in ["automated", "do not reply", "noreply"]):
            return False

        # Don't suggest response for automated senders
        if any(auto_sender in message.sender.lower() for auto_sender in ["noreply", "donotreply", "no-reply"]):
            return False

        # Look for question indicators
        if "?" in content:
            return True

        # Look for request patterns
        request_patterns = [
            r"\bplease\b.*\b(let me know|respond|reply|confirm)\b",
            r"\bcan you\b",
            r"\bwould you\b",
            r"\bcould you\b",
        ]

        return any(re.search(pattern, content, re.IGNORECASE) for pattern in request_patterns)

    def _sentiment_to_score(self, sentiment: str) -> float:
        """Convert sentiment string to numeric score."""
        sentiment_map = {"positive": 1.0, "neutral": 0.5, "negative": 0.0}
        return sentiment_map.get(sentiment, 0.5)

    def _calculate_avg_response_time(self, messages: Sequence[email_message.EmailMessage]) -> timedelta | None:
        """Calculate average response time (simplified heuristic)."""
        # This is a simplified implementation
        # In practice, you'd need to analyze email threads and reply patterns
        if len(messages) < self.MIN_MESSAGES_FOR_ANALYSIS:
            return None

        # Simple heuristic: average time between messages
        time_diffs = []
        sorted_messages = sorted(messages, key=lambda m: m.timestamp)

        for i in range(1, len(sorted_messages)):
            diff = sorted_messages[i].timestamp - sorted_messages[i - 1].timestamp
            if diff.total_seconds() < self.SECONDS_PER_DAY:  # Within 24 hours
                time_diffs.append(diff)

        if not time_diffs:
            return None

        avg_seconds = sum(diff.total_seconds() for diff in time_diffs) / len(time_diffs)
        return timedelta(seconds=avg_seconds)

    def _calculate_response_efficiency(self, messages: Sequence[email_message.EmailMessage]) -> float:
        """Calculate response efficiency score."""
        # Simplified metric based on read status and time since receipt
        if not messages:
            return 1.0

        now = datetime.now(tz=UTC)
        efficient_responses = 0
        total_actionable = 0

        for message in messages:
            # Skip if message is very recent (less than 1 hour)
            age = now - message.timestamp
            if age.total_seconds() < self.SECONDS_PER_HOUR:
                continue

            analysis = self.analyze_message(message)
            if analysis.response_suggested:
                total_actionable += 1
                # Consider efficient if read within reasonable time
                if message.is_read and age.total_seconds() < self.SECONDS_PER_DAY:  # Within 24 hours
                    efficient_responses += 1

        if total_actionable == 0:
            return 1.0

        return efficient_responses / total_actionable

    def _generate_recommendations(
        self,
        messages: Sequence[email_message.EmailMessage],
        priority_unread: int,
        overload_risk: str,
    ) -> list[str]:
        """Generate productivity recommendations."""
        recommendations = []

        if priority_unread > 0:
            recommendations.append(f"Focus on {priority_unread} high-priority unread messages first")

        if overload_risk == "high":
            recommendations.append("Consider using filters to reduce email volume")
            recommendations.append("Set specific times for email processing to improve focus")

        # Analyze unread ratio
        total_messages = len(messages)
        unread_messages = sum(1 for msg in messages if not msg.is_read)
        if total_messages > 0 and unread_messages / total_messages > self.UNREAD_RATIO_THRESHOLD:
            recommendations.append("Consider batch processing emails to reduce unread backlog")

        # Check for old unread messages
        now = datetime.now(tz=UTC)
        old_unread = sum(1 for msg in messages if not msg.is_read and (now - msg.timestamp).days > self.OLD_UNREAD_DAYS_THRESHOLD)
        if old_unread > self.OLD_UNREAD_COUNT_THRESHOLD:
            recommendations.append("Archive or delete old unread messages to reduce clutter")

        if not recommendations:
            recommendations.append("Your email management looks good!")

        return recommendations
