"""Email Message Protocol - Core message representation and data models.

This module defines the EmailMessage protocol that represents email messages
with comprehensive metadata, content parsing, and extensible properties for
different email service providers.

Key Features:
    - Rich email metadata (sender, recipients, timestamps)
    - Content parsing (plain text, HTML, attachments)
    - Thread and conversation tracking
    - Extensible attributes for provider-specific data
    - Factory pattern for implementation injection

Example:
    ```python
    from email_message import EmailMessage, create_message

    # Factory returns concrete implementation
    msg = create_message(msg_id="abc123", raw_data=gmail_response)

    # Access rich metadata
    print(f"From: {msg.sender}")
    print(f"Subject: {msg.subject}")
    print(f"Thread: {msg.thread_id}")
    ```

"""

from datetime import datetime
from typing import Protocol, runtime_checkable


@runtime_checkable
class EmailMessage(Protocol):
    """Protocol defining the structure and interface for email message objects.

    This protocol ensures consistent access to email message properties
    across different email service implementations while providing rich
    metadata and content parsing capabilities.
    """

    @property
    def message_id(self) -> str:
        """Unique identifier for this email message.

        Returns:
            str: Globally unique message identifier

        """
        raise NotImplementedError

    @property
    def sender(self) -> str:
        """Email address of the message sender.

        Returns:
            str: Sender's email address in standard format

        """
        raise NotImplementedError

    @property
    def recipients(self) -> list[str]:
        """List of recipient email addresses (To field).

        Returns:
            list[str]: List of primary recipient email addresses

        """
        raise NotImplementedError

    @property
    def cc_recipients(self) -> list[str]:
        """List of carbon copy recipient email addresses.

        Returns:
            list[str]: List of CC recipient email addresses

        """
        raise NotImplementedError

    @property
    def bcc_recipients(self) -> list[str]:
        """List of blind carbon copy recipient email addresses.

        Returns:
            list[str]: List of BCC recipient email addresses (if available)

        """
        raise NotImplementedError

    @property
    def timestamp(self) -> datetime:
        """Timestamp when the message was sent.

        Returns:
            datetime: Message send timestamp in UTC

        """
        raise NotImplementedError

    @property
    def subject(self) -> str:
        """Email subject line.

        Returns:
            str: Message subject, empty string if no subject

        """
        raise NotImplementedError

    @property
    def body_text(self) -> str:
        """Plain text content of the email body.

        Returns:
            str: Plain text body content, extracted from HTML if necessary

        """
        raise NotImplementedError

    @property
    def body_html(self) -> str:
        """HTML content of the email body.

        Returns:
            str: HTML body content, empty string if only plain text available

        """
        raise NotImplementedError

    @property
    def is_read(self) -> bool:
        """Read status of the message.

        Returns:
            bool: True if message has been marked as read

        """
        raise NotImplementedError

    @property
    def is_starred(self) -> bool:
        """Star/favorite status of the message.

        Returns:
            bool: True if message is starred/favorited

        """
        raise NotImplementedError

    @property
    def thread_id(self) -> str | None:
        """Thread/conversation identifier for grouped messages.

        Returns:
            str | None: Thread ID if message is part of a conversation

        """
        raise NotImplementedError

    @property
    def labels(self) -> list[str]:
        """List of labels/tags associated with the message.

        Returns:
            list[str]: List of label names applied to this message

        """
        raise NotImplementedError

    @property
    def attachment_count(self) -> int:
        """Number of attachments in the message.

        Returns:
            int: Count of file attachments

        """
        raise NotImplementedError

    def get_snippet(self, max_length: int = 100) -> str:
        """Generate a preview snippet of the message content.

        Args:
            max_length: Maximum length of the snippet

        Returns:
            str: Truncated preview of message content

        """
        raise NotImplementedError


def create_message(msg_id: str, raw_message_data: str) -> EmailMessage:
    """Factory function to create an EmailMessage instance from raw data.

    This function acts as a factory, delegating to the appropriate
    message implementation based on the registered provider.
    Implementations override this function to provide their concrete types.

    Args:
        msg_id: Unique identifier for the message
        raw_message_data: Raw message data from the email service

    Returns:
        EmailMessage: Concrete email message implementation

    Raises:
        NotImplementedError: If no implementation has been registered
        MessageParsingError: If raw data cannot be parsed

    """
    msg = "No email message implementation registered"
    raise NotImplementedError(msg)
