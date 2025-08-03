"""Message protocol definition for email clients."""

from collections.abc import Callable
from typing import Any, Optional, Protocol, runtime_checkable


@runtime_checkable
class Message(Protocol):
    """Protocol defining the interface for email messages."""

    @property
    def id(self) -> str:
        """Unique identifier for the message."""
        ...

    @property
    def from_(self) -> str:
        """Sender email address."""
        ...

    @property
    def to(self) -> str:
        """Recipient email address."""
        ...

    @property
    def subject(self) -> str:
        """Message subject line."""
        ...

    @property
    def body(self) -> str:
        """Message body content."""
        ...

    @property
    def date(self) -> str:
        """Message timestamp."""
        ...


# Type-safe dependency injection
_message_factory: Callable[..., Message] | None = None


def register_message_factory(factory: Callable[..., Message]) -> None:
    """Register a message implementation factory.

    Args:
        factory: Function that creates Message instances.
    """
    global _message_factory
    _message_factory = factory


def get_message(*args: Any, **kwargs: Any) -> Message:
    """Factory function for creating Message instances.

    Args:
        *args: Arguments to pass to the message factory.
        **kwargs: Keyword arguments to pass to the message factory.

    Returns:
        Message: A message instance.

    Raises:
        NotImplementedError: When called without implementation registered.
    """
    if _message_factory is None:
        raise NotImplementedError("No message implementation registered")
    return _message_factory(*args, **kwargs)


__all__ = ["Message", "get_message", "register_message_factory"]
