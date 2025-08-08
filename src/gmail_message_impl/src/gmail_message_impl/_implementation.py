"""Gmail message implementation with comprehensive parsing and data extraction."""

import base64
import binascii
import json
import re
from datetime import UTC, datetime
from typing import Any


class GmailEmailMessage:
    """Gmail-specific implementation of the EmailMessage protocol.

    This class parses Gmail API responses and provides access to Gmail-specific
    features like labels, threads, and rich metadata extraction.
    """

    def __init__(self, message_id: str, gmail_response: str) -> None:
        """Initialize Gmail message from API response data.

        Args:
            message_id: Gmail message ID
            gmail_response: JSON string containing Gmail API response

        Raises:
            ValueError: If response data is invalid or unparseable

        """
        self._message_id = message_id
        try:
            self._gmail_data: dict[str, Any] = json.loads(gmail_response)
        except json.JSONDecodeError as e:
            msg = f"Invalid Gmail response JSON: {e}"
            raise ValueError(msg) from e

        # Extract and cache frequently accessed data
        self._headers = self._extract_headers()
        self._payload_parts = self._extract_payload_parts()

    @property
    def message_id(self) -> str:
        """Gmail message unique identifier."""
        return self._message_id

    @property
    def sender(self) -> str:
        """Extract sender from Gmail headers."""
        from_header = self._headers.get("From", "")
        # Extract email from "Name <email@domain.com>" format
        email_match = re.search(r"<([^>]+)>", from_header)
        if email_match:
            return email_match.group(1)
        # Return as-is if no angle brackets found
        return from_header.strip()

    @property
    def recipients(self) -> list[str]:
        """Extract primary recipients from To header."""
        to_header = self._headers.get("To", "")
        return self._parse_email_list(to_header)

    @property
    def cc_recipients(self) -> list[str]:
        """Extract CC recipients from Gmail headers."""
        cc_header = self._headers.get("Cc", "")
        return self._parse_email_list(cc_header)

    @property
    def bcc_recipients(self) -> list[str]:
        """Extract BCC recipients (usually empty in Gmail API)."""
        bcc_header = self._headers.get("Bcc", "")
        return self._parse_email_list(bcc_header)

    @property
    def timestamp(self) -> datetime:
        """Parse Gmail timestamp into datetime object."""
        if self._gmail_data is None:
            return datetime.now(tz=UTC)
            
        # Gmail provides internalDate as milliseconds since epoch
        internal_date = self._gmail_data.get("internalDate")
        if internal_date:
            # Convert milliseconds to seconds
            timestamp_seconds = int(internal_date) / 1000
            return datetime.fromtimestamp(timestamp_seconds, tz=UTC)

        # Fallback to Date header parsing
        date_header = self._headers.get("Date", "")
        if date_header:
            return self._parse_date_header(date_header)

        # Last resort: current time
        return datetime.now(tz=UTC)

    @property
    def subject(self) -> str:
        """Extract subject from Gmail headers."""
        return self._headers.get("Subject", "")

    @property
    def body_text(self) -> str:
        """Extract plain text body content."""
        # Look for text/plain parts in payload
        for part in self._payload_parts:
            if part.get("mimeType") == "text/plain":
                body_data = part.get("body", {}).get("data", "")
                if body_data:
                    return self._decode_base64_content(body_data)

        # If no plain text, try to extract from HTML
        html_body = self.body_html
        if html_body:
            return self._html_to_text(html_body)

        return ""

    @property
    def body_html(self) -> str:
        """Extract HTML body content."""
        # Look for text/html parts in payload
        for part in self._payload_parts:
            if part.get("mimeType") == "text/html":
                body_data = part.get("body", {}).get("data", "")
                if body_data:
                    return self._decode_base64_content(body_data)
        return ""

    @property
    def is_read(self) -> bool:
        """Check if message is marked as read (not in UNREAD label)."""
        if self._gmail_data is None:
            return True  # Assume read if no data
        labels = self._gmail_data.get("labelIds", [])
        return "UNREAD" not in labels

    @property
    def is_starred(self) -> bool:
        """Check if message is starred (has STARRED label)."""
        if self._gmail_data is None:
            return False
        labels = self._gmail_data.get("labelIds", [])
        return "STARRED" in labels

    @property
    def thread_id(self) -> str | None:
        """Gmail thread identifier for conversation grouping."""
        if self._gmail_data is None:
            return None
        return self._gmail_data.get("threadId")

    @property
    def labels(self) -> list[str]:
        """List of Gmail labels applied to this message."""
        if self._gmail_data is None:
            return []
        label_ids = self._gmail_data.get("labelIds", [])
        return [str(label) for label in label_ids] if label_ids else []

    @property
    def attachment_count(self) -> int:
        """Count file attachments in the message."""
        attachment_count = 0
        for part in self._payload_parts:
            if part.get("filename") and part.get("body", {}).get("attachmentId"):
                attachment_count += 1
        return attachment_count

    def get_snippet(self, max_length: int = 100) -> str:
        """Generate message content preview."""
        if self._gmail_data is None:
            return ""
            
        # Gmail provides a snippet field
        gmail_snippet = self._gmail_data.get("snippet", "")
        if gmail_snippet:
            return str(gmail_snippet)[:max_length] + ("..." if len(str(gmail_snippet)) > max_length else "")

        # Fallback to body text
        body = self.body_text
        if body:
            clean_body = str(body).replace("\n", " ").replace("\r", " ").strip()
            return clean_body[:max_length] + ("..." if len(clean_body) > max_length else "")

        return ""

    # Private helper methods

    def _extract_headers(self) -> dict[str, str]:
        """Extract headers from Gmail payload."""
        headers = {}
        if self._gmail_data is None:
            return headers
            
        payload = self._gmail_data.get("payload", {})
        header_list = payload.get("headers", [])

        for header in header_list:
            name = header.get("name", "")
            value = header.get("value", "")
            headers[name] = value

        return headers

    def _extract_payload_parts(self) -> list[dict[str, Any]]:
        """Extract all payload parts for content parsing."""
        if self._gmail_data is None:
            return []
            
        payload = self._gmail_data.get("payload", {})
        parts = payload.get("parts", [])

        # If no parts, the payload itself might contain the content
        if not parts and payload.get("body"):
            return [payload]

        # Recursively extract parts (for nested multipart messages)
        all_parts = []
        for part in parts:
            all_parts.append(part)
            if "parts" in part:
                all_parts.extend(part["parts"])

        return all_parts

    def _parse_email_list(self, email_header: str) -> list[str]:
        """Parse comma-separated email addresses from headers."""
        if not email_header:
            return []

        emails = []
        # Split by comma and extract email addresses
        for email_part_raw in email_header.split(","):
            email_part = email_part_raw.strip()
            # Extract email from "Name <email@domain.com>" format
            email_match = re.search(r"<([^>]+)>", email_part)
            if email_match:
                extracted_email = email_match.group(1)
                # Validate that extracted email has @ symbol
                if "@" in extracted_email:
                    emails.append(extracted_email)
            elif "@" in email_part and not email_part.startswith("<"):
                # Direct email address, but not incomplete angle bracket format
                emails.append(email_part)

        return emails

    def _decode_base64_content(self, base64_data: str) -> str:
        """Decode Gmail's URL-safe base64 encoded content."""
        try:
            # Gmail uses URL-safe base64 encoding
            # Ensure proper padding
            missing_padding = len(base64_data) % 4
            if missing_padding:
                base64_data += '=' * (4 - missing_padding)
            
            decoded_bytes = base64.urlsafe_b64decode(base64_data)
            return decoded_bytes.decode("utf-8", errors="replace")
        except (ValueError, TypeError, binascii.Error):
            # Return empty string for invalid base64 data
            return ""

    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML content to plain text (basic implementation)."""
        # Remove HTML tags (basic regex approach)
        clean_text = re.sub(r"<[^>]+>", "", html_content)
        # Clean up whitespace
        clean_text = re.sub(r"\s+", " ", clean_text)
        return clean_text.strip()

    def _parse_date_header(self, date_header: str) -> datetime:
        """Parse RFC 2822 date header into datetime object."""
        try:
            # Try common date formats
            formats = [
                "%a, %d %b %Y %H:%M:%S %z",
                "%d %b %Y %H:%M:%S %z",
                "%a, %d %b %Y %H:%M:%S",
                "%d %b %Y %H:%M:%S",
            ]

            for date_format in formats:
                try:
                    return datetime.strptime(date_header, date_format).replace(tzinfo=UTC)
                except ValueError:
                    continue

            # If all formats fail, return current time
            return datetime.now(tz=UTC)
        except (ValueError, TypeError):
            return datetime.now(tz=UTC)
