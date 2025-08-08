# smart-email-client/main.py

"""Smart Email Client - AI-Enhanced Email Management Demo.

This application demonstrates the component-based architecture with dependency
injection by showcasing core email operations enhanced with AI-powered analytics.
"""

# Import implementation packages to trigger dependency injection
import email_analytics
import email_client_api


def main() -> None:
    """Demonstrate smart email client with AI-enhanced features."""
    print("🚀 Starting Smart Email Client with AI Analytics...")

    try:
        # Initialize email service (dependency injection provides Gmail implementation)
        print("\n📧 Initializing email service...")
        email_service = email_client_api.create_client(interactive=True)
        print("✅ Successfully connected to Gmail API")

        # Initialize AI analytics engine
        print("\n🧠 Initializing AI analytics engine...")
        analyzer = email_analytics.EmailAnalyzer()
        print("✅ AI analytics engine ready")

        # Demo 1: Fetch and analyze messages
        print("\n" + "=" * 60)
        print("📨 DEMO 1: Smart Message Retrieval & Analysis")
        print("=" * 60)

        messages = list(email_service.fetch_messages(limit=5))
        if not messages:
            print("❌ No messages found in inbox")
            return

        print(f"📥 Retrieved {len(messages)} messages")

        # Analyze each message with AI
        analyzed_messages = []
        for i, message in enumerate(messages, 1):
            print(f"\n📧 Message {i}:")
            print(f"   📤 From: {message.sender}")
            print(f"   📄 Subject: {message.subject}")
            print(f"   📅 Date: {message.timestamp}")

            # AI Analysis
            analysis = analyzer.analyze_message(message)
            analyzed_messages.append((message, analysis))

            print("   🤖 AI Analysis:")
            print(
                f"      Priority: {'🔴 HIGH' if analysis.priority_score > 0.7 else '🟡 MEDIUM' if analysis.priority_score > 0.4 else '🟢 LOW'} ({analysis.priority_score:.2f})"
            )
            print(f"      Sentiment: {analysis.sentiment.upper()} ({analysis.sentiment_confidence:.2f})")
            print(f"      Category: {analysis.category.upper()} ({analysis.category_confidence:.2f})")
            print(f"      Reading Time: {analysis.estimated_reading_time}s")
            print(f"      Response Needed: {'✅ YES' if analysis.response_suggested else '❌ NO'}")

            if analysis.urgency_indicators:
                print(f"      ⚠️  Urgency Indicators: {', '.join(analysis.urgency_indicators)}")

            if analysis.spam_probability > 0.5:
                print(f"      🚨 Spam Risk: {analysis.spam_probability:.2f}")

        # Demo 2: Priority-based message management
        print("\n" + "=" * 60)
        print("🎯 DEMO 2: Priority-Based Message Management")
        print("=" * 60)

        # Sort by priority score
        priority_sorted = sorted(analyzed_messages, key=lambda x: x[1].priority_score, reverse=True)

        print("📊 Messages sorted by AI-calculated priority:")
        for i, (message, analysis) in enumerate(priority_sorted, 1):
            priority_emoji = "🔴" if analysis.priority_score > 0.7 else "🟡" if analysis.priority_score > 0.4 else "🟢"
            print(f"{i}. {priority_emoji} {analysis.priority_score:.2f} - {message.subject[:50]}...")

        # Demonstrate message operations on highest priority
        if priority_sorted:
            top_message, top_analysis = priority_sorted[0]
            print("\n🎯 Operating on highest priority message:")
            print(f"   Subject: {top_message.subject}")

            if not top_message.is_read:
                print("   📖 Marking as read...")
                success = email_service.mark_message_read(top_message.message_id)
                print(f"   {'✅ Success' if success else '❌ Failed'}")

        # Demo 3: Communication pattern analysis
        print("\n" + "=" * 60)
        print("📈 DEMO 3: Communication Pattern Analysis")
        print("=" * 60)

        patterns = analyzer.analyze_communication_patterns(messages)
        print("📊 Communication Insights:")
        print(f"   Total Messages Analyzed: {patterns.total_messages_analyzed}")
        print(f"   Peak Activity Hours: {patterns.peak_activity_hours}")
        print(f"   Top Senders: {patterns.most_frequent_senders[:3]}")
        print(f"   Category Distribution: {patterns.category_distribution}")
        print(f"   Sentiment by Category: {patterns.sentiment_trend}")

        if patterns.avg_response_time:
            print(f"   Average Response Time: {patterns.avg_response_time}")

        # Demo 4: Productivity metrics and recommendations
        print("\n" + "=" * 60)
        print("📊 DEMO 4: Productivity Metrics & AI Recommendations")
        print("=" * 60)

        productivity = analyzer.generate_productivity_metrics(messages)
        print("🏆 Productivity Analysis:")
        print(f"   Priority Unread Messages: {productivity.unread_priority_messages}")
        print(f"   Daily Email Processing Time: {productivity.estimated_daily_email_time}")
        print(f"   Response Efficiency: {productivity.response_efficiency_score:.2f}")
        print(f"   Email Overload Risk: {productivity.email_overload_risk.upper()}")

        print("\n💡 AI Recommendations:")
        for i, recommendation in enumerate(productivity.recommendations, 1):
            print(f"   {i}. {recommendation}")

        # Demo 5: Advanced search with AI categorization
        print("\n" + "=" * 60)
        print("🔍 DEMO 5: Smart Search & Categorization")
        print("=" * 60)

        print("🔎 Searching for work-related emails...")
        try:
            work_messages = list(email_service.search_messages("category:work OR meeting OR project", max_results=3))
            print(f"📁 Found {len(work_messages)} work-related messages")

            for message in work_messages:
                analysis = analyzer.analyze_message(message)
                print(f"   📧 {message.subject[:40]}... (Category: {analysis.category})")
        except Exception as e:
            print(f"⚠️  Search not supported or failed: {e}")

        # Demo 6: Message cleanup suggestions
        print("\n" + "=" * 60)
        print("🧹 DEMO 6: Smart Cleanup Suggestions")
        print("=" * 60)

        print("🤖 Analyzing messages for cleanup opportunities...")

        # Find potential spam or low-priority messages
        cleanup_candidates = []
        for message, analysis in analyzed_messages:
            if analysis.spam_probability > 0.6 or (analysis.priority_score < 0.2 and analysis.category == "promotional"):
                cleanup_candidates.append((message, analysis))

        if cleanup_candidates:
            print(f"🗑️  Found {len(cleanup_candidates)} messages suggested for cleanup:")
            for message, analysis in cleanup_candidates:
                print(
                    f"   📧 {message.subject[:40]}... (Spam: {analysis.spam_probability:.2f}, Priority: {analysis.priority_score:.2f})"
                )

            print("\n💡 These messages could be safely archived or deleted")
        else:
            print("✨ No cleanup suggestions - your inbox looks clean!")

        print("\n" + "=" * 60)
        print("🎉 Smart Email Client Demo Complete!")
        print("=" * 60)
        print("✅ Successfully demonstrated:")
        print("   • Component-based architecture with dependency injection")
        print("   • Gmail API integration with comprehensive error handling")
        print("   • AI-powered email analysis and insights")
        print("   • Priority-based message management")
        print("   • Communication pattern analysis")
        print("   • Productivity metrics and recommendations")
        print("   • Smart search and categorization")
        print("   • Intelligent cleanup suggestions")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("🔧 Troubleshooting tips:")
        print("   • Ensure credentials.json is in the project root")
        print("   • Check internet connection")
        print("   • Verify Gmail API is enabled in Google Cloud Console")
        raise


if __name__ == "__main__":
    main()
