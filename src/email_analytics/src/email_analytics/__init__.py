"""Email Analytics - AI-Enhanced Email Analysis and Intelligence.

This module provides intelligent analysis capabilities for email messages,
including sentiment analysis, priority scoring, content categorization,
and productivity insights. It demonstrates AI integration without external
dependencies by using rule-based algorithms and heuristics.

Key Features:
    - Email sentiment analysis and mood detection
    - Priority scoring based on sender, content, and metadata
    - Content categorization (work, personal, promotional, etc.)
    - Communication pattern analysis
    - Productivity metrics and recommendations
    - Spam detection using content analysis

Example:
    ```python
    from email_analytics import EmailAnalyzer, AnalysisReport

    analyzer = EmailAnalyzer()

    # Analyze a single message
    report = analyzer.analyze_message(email_message)
    print(f"Priority: {report.priority_score}")
    print(f"Sentiment: {report.sentiment}")
    print(f"Category: {report.category}")

    # Analyze email patterns
    patterns = analyzer.analyze_communication_patterns(message_list)
    print(f"Response time avg: {patterns.avg_response_time}")
    ```

"""

from ._analyzer import AnalysisReport, CommunicationPatterns, EmailAnalyzer, ProductivityMetrics

# Export main classes for public API
__all__ = [
    "AnalysisReport",
    "CommunicationPatterns",
    "EmailAnalyzer",
    "ProductivityMetrics",
]
