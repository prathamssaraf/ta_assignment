"""Gmail Message Implementation - Concrete Gmail message parsing and data extraction.

This module provides the GmailEmailMessage class that implements the EmailMessage
protocol specifically for Gmail API responses. It handles Gmail's unique data
structures, label system, and threading model.

Key Features:
    - Gmail API response parsing
    - Rich metadata extraction from Gmail headers
    - Gmail-specific features (labels, threads, stars)
    - Robust error handling for malformed data
    - Automatic dependency injection registration

Example:
    ```python
    from gmail_message_impl import GmailEmailMessage

    # Parse Gmail API response
    gmail_msg = GmailEmailMessage(msg_id="123", gmail_data=api_response)

    # Access Gmail-specific features
    print(f"Labels: {gmail_msg.labels}")
    print(f"Thread: {gmail_msg.thread_id}")
    ```

"""

import email_message

from ._implementation import GmailEmailMessage

# Export main class for documentation
__all__ = ["GmailEmailMessage", "create_gmail_message"]


def create_gmail_message(msg_id: str, raw_message_data: str) -> email_message.EmailMessage:
    """Create a Gmail-specific message instance.

    Args:
        msg_id: Gmail message ID
        raw_message_data: Raw Gmail API response data

    Returns:
        Gmail message implementation

    Raises:
        ValueError: If message data is invalid or unparseable

    """
    return GmailEmailMessage(message_id=msg_id, gmail_response=raw_message_data)


# --- Dependency Injection ---
# Override the create_message function in the protocol package
# Now anyone calling email_message.create_message() gets our Gmail implementation
email_message.create_message = create_gmail_message
# --- Dependency Injection ---
