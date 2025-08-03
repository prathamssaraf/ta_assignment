"""Gmail client protocol definition."""

from collections.abc import Iterator
from typing import Protocol, runtime_checkable, Optional, Callable

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


# Type-safe dependency injection
_client_factory: Optional[Callable[..., Client]] = None


def register_client_factory(factory: Callable[..., Client]) -> None:
    """Register a client implementation factory.
    
    Args:
        factory: Function that creates Client instances.
    """
    global _client_factory
    _client_factory = factory


def get_client(*args, **kwargs) -> Client:
    """Factory function for creating Client instances.

    Args:
        *args: Arguments to pass to the client factory.
        **kwargs: Keyword arguments to pass to the client factory.

    Returns:
        Client: A client instance.

    Raises:
        NotImplementedError: When called without implementation registered.
    """
    if _client_factory is None:
        raise NotImplementedError("No client implementation registered")
    return _client_factory(*args, **kwargs)


__all__ = ["Client", "register_client_factory", "get_client"]