"""Email Client API - Core protocols and service contracts.

This module provides the foundational protocols for email client operations,
defining abstract interfaces that concrete implementations must satisfy to
enable email retrieval, management, and advanced operations.

Key Features:
    - Protocol-based design for loose coupling
    - Type-safe interfaces with runtime checking
    - Extensible architecture for multiple email providers
    - Factory pattern for implementation injection

Example:
    ```python
    from email_client_api import create_client, EmailService

    # Factory returns concrete implementation
    service = create_client(interactive=True)

    # Use standardized interface
    emails = service.fetch_messages(limit=5)
    for email in emails:
        print(f"Subject: {email.subject}")
    ```

"""

from collections.abc import Iterator
from typing import Protocol, runtime_checkable

from email_message import EmailMessage


@runtime_checkable
class EmailService(Protocol):
    """Protocol defining the contract for email service implementations.

    This protocol establishes the interface that all email service providers
    must implement to ensure consistent behavior across different backends
    (Gmail, Outlook, IMAP, etc.).
    """

    def fetch_message_by_id(self, message_id: str) -> EmailMessage:
        """Retrieve a specific email message by its unique identifier.

        Args:
            message_id: Unique identifier for the target message

        Returns:
            EmailMessage: The requested email message object

        Raises:
            MessageNotFoundError: If message with given ID doesn't exist
            AuthenticationError: If authentication is invalid or expired

        """
        raise NotImplementedError

    def remove_message(self, message_id: str) -> bool:
        """Permanently delete an email message from the mailbox.

        Args:
            message_id: Unique identifier for the message to delete

        Returns:
            bool: True if deletion was successful, False otherwise

        Raises:
            MessageNotFoundError: If message with given ID doesn't exist
            PermissionError: If user lacks deletion permissions

        """
        raise NotImplementedError

    def mark_message_read(self, message_id: str) -> bool:
        """Update message status to mark it as read.

        Args:
            message_id: Unique identifier for the message to mark

        Returns:
            bool: True if status update was successful, False otherwise

        Raises:
            MessageNotFoundError: If message with given ID doesn't exist

        """
        raise NotImplementedError

    def mark_message_unread(self, message_id: str) -> bool:
        """Update message status to mark it as unread.

        Args:
            message_id: Unique identifier for the message to mark

        Returns:
            bool: True if status update was successful, False otherwise

        Raises:
            MessageNotFoundError: If message with given ID doesn't exist

        """
        raise NotImplementedError

    def fetch_messages(self, limit: int = 10, query: str | None = None) -> Iterator[EmailMessage]:
        """Retrieve email messages from the inbox with optional filtering.

        Args:
            limit: Maximum number of messages to return (default: 10)
            query: Optional search query to filter messages

        Returns:
            Iterator[EmailMessage]: Iterator yielding email message objects

        Raises:
            AuthenticationError: If authentication is invalid or expired
            QuotaExceededError: If API rate limits are exceeded

        """
        raise NotImplementedError

    def search_messages(self, search_criteria: str, max_results: int = 50) -> Iterator[EmailMessage]:
        """Search for messages matching specific criteria.

        Args:
            search_criteria: Search query using provider-specific syntax
            max_results: Maximum number of results to return

        Returns:
            Iterator[EmailMessage]: Iterator of matching messages

        Raises:
            InvalidQueryError: If search criteria syntax is invalid

        """
        raise NotImplementedError


def create_client(interactive: bool = False, provider: str = "gmail") -> EmailService:
    """Factory function to create an email service client instance.

    This function acts as a service locator, returning the appropriate
    email service implementation based on the provider specified.
    Implementations register themselves by overriding this function.

    Args:
        interactive: Enable interactive authentication flow if True
        provider: Email service provider identifier (default: "gmail")

    Returns:
        EmailService: Concrete email service implementation

    Raises:
        NotImplementedError: If no implementation has been registered
        UnsupportedProviderError: If specified provider is not available

    """
    msg = "No email service implementation registered"
    raise NotImplementedError(msg)
