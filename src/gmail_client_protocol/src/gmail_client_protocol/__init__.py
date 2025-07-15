"""Gmail client protocol definition."""

from collections.abc import Iterator
from typing import Protocol, runtime_checkable

from message import Message


@runtime_checkable
class Client(Protocol):
    """Protocol defining the interface for email clients."""

    def get_messages(self) -> Iterator[Message]:
        """Retrieve all messages from the inbox.

        Returns:
            Iterator[Message]: Iterator over all messages in the inbox.
        """
        ...

    def send_message(self, to: str, subject: str, body: str) -> bool:
        """Send a new email message.

        Args:
            to: Recipient email address.
            subject: Message subject line.
            body: Message body content.

        Returns:
            bool: True if message was sent successfully, False otherwise.
        """
        ...

    def delete_message(self, message_id: str) -> bool:
        """Delete a message by its ID.

        Args:
            message_id: Unique identifier of the message to delete.

        Returns:
            bool: True if message was deleted successfully, False otherwise.
        """
        ...

    def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read.

        Args:
            message_id: Unique identifier of the message to mark as read.

        Returns:
            bool: True if message was marked as read successfully, False otherwise.
        """
        ...


def get_client() -> Client:
    """Factory function for creating Client instances.

    This function is intended to be overridden by implementations
    through dependency injection.

    Raises:
        NotImplementedError: When called without implementation override.
    """
    raise NotImplementedError("No client implementation available")


__all__ = ["Client", "get_client"]
