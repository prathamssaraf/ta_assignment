"""Gmail message implementation."""

import base64
import email
import email.policy
from email.message import EmailMessage
from typing import Any

import message
from message import Message


class GmailMessage:
    """Gmail implementation of the Message protocol."""

    def __init__(self, message_id: str, raw_data: dict[str, Any]) -> None:
        """Initialize Gmail message from API response.

        Args:
            message_id: Gmail message ID.
            raw_data: Raw message data from Gmail API.
        """
        self._id = message_id
        self._raw_data = raw_data
        self._parsed_message = self._parse_message()

    def _parse_message(self) -> EmailMessage:
        """Parse raw Gmail message data into EmailMessage object."""
        raw = self._raw_data.get("raw", "")
        if raw:
            # Decode base64 encoded raw message
            decoded_bytes = base64.urlsafe_b64decode(raw + "==")
            return email.message_from_bytes(decoded_bytes, policy=email.policy.default)  # type: ignore[return-value,arg-type]
        else:
            # Create empty message if no raw data
            return EmailMessage()

    @property
    def id(self) -> str:
        """Message ID."""
        return self._id

    @property
    def from_(self) -> str:
        """Sender email address."""
        return str(self._parsed_message.get("From", ""))

    @property
    def to(self) -> str:
        """Recipient email address."""
        return str(self._parsed_message.get("To", ""))

    @property
    def subject(self) -> str:
        """Message subject."""
        return str(self._parsed_message.get("Subject", ""))

    def _extract_multipart_content(self) -> str:
        """Extract plain text content from multipart message."""
        for part in self._parsed_message.walk():
            if part.get_content_type() == "text/plain":
                try:
                    content = part.get_content()
                    if content:
                        return str(content)
                except (AttributeError, UnicodeDecodeError):
                    # Fallback to raw payload
                    payload = part.get_payload(decode=True)
                    if payload and isinstance(payload, bytes):
                        return payload.decode("utf-8", errors="replace")
        return ""

    def _extract_single_part_content(self) -> str:
        """Extract content from single part message."""
        try:
            content = self._parsed_message.get_content()
            if content:
                return str(content)
        except (AttributeError, UnicodeDecodeError):
            # Fallback to raw payload
            payload = self._parsed_message.get_payload(decode=True)
            if payload and isinstance(payload, bytes):
                return payload.decode("utf-8", errors="replace")
        return ""

    @property
    def body(self) -> str:
        """Message body content."""
        try:
            if self._parsed_message.is_multipart():
                return self._extract_multipart_content()
            else:
                return self._extract_single_part_content()
        except Exception:
            return ""

    @property
    def date(self) -> str:
        """Message date."""
        return str(self._parsed_message.get("Date", ""))


def get_message_impl(message_id: str, raw_data: dict[str, Any]) -> Message:
    """Create a GmailMessage instance.

    Args:
        message_id: Gmail message ID.
        raw_data: Raw message data from Gmail API.

    Returns:
        Message: GmailMessage instance conforming to Message protocol.
    """
    return GmailMessage(message_id, raw_data)


# Override the protocol factory function
message.get_message = get_message_impl  # type: ignore[assignment]

__all__ = ["GmailMessage", "get_message_impl"]
