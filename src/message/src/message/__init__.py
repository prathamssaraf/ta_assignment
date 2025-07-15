"""Message protocol definition for email clients."""

from typing import Protocol, runtime_checkable


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


def get_message() -> Message:
    """Factory function for creating Message instances.
    
    This function is intended to be overridden by implementations
    through dependency injection.
    
    Raises:
        NotImplementedError: When called without implementation override.
    """
    raise NotImplementedError("No message implementation available")


__all__ = ["Message", "get_message"]