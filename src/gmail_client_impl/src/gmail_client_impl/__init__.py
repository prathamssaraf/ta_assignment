"""Gmail client implementation."""

import base64
import os
from collections.abc import Iterator
from pathlib import Path
from typing import ClassVar

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError

import mail_client_api
from gmail_message_impl import get_message_impl
from mail_client_api import Client
from message import Message


class GmailClient:
    """Gmail implementation of the Client protocol."""

    SCOPES: ClassVar[list[str]] = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
    ]

    def __init__(self, credentials_path: str = "credentials.json") -> None:
        """Initialize Gmail client.

        Args:
            credentials_path: Path to Gmail API credentials file.
        """
        self._credentials_path = credentials_path
        self._service: Resource | None = None
        self._authenticate()

    def _authenticate(self) -> None:
        """Authenticate with Gmail API using OAuth 2.0."""
        creds = None
        token_path = "token.json"

        # Load existing token if available
        if Path(token_path).exists():
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)

        # If no valid credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not Path(self._credentials_path).exists():
                    raise FileNotFoundError(
                        f"Credentials file not found: {self._credentials_path}. "
                        "Please download from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self._credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            Path(token_path).write_text(creds.to_json())

        # Build Gmail service
        self._service = build("gmail", "v1", credentials=creds)

    @property
    def service(self) -> Resource:
        """Get authenticated Gmail service."""
        if self._service is None:
            raise RuntimeError("Gmail service not initialized")
        return self._service

    def get_messages(self) -> Iterator[Message]:
        """Retrieve all messages from Gmail inbox."""
        try:
            # Get list of message IDs
            results = self.service.users().messages().list(userId="me").execute()
            messages = results.get("messages", [])

            # Fetch full message data for each ID
            for msg_info in messages:
                msg_id = msg_info["id"]
                try:
                    # Get full message with raw format
                    message = (
                        self.service.users()
                        .messages()
                        .get(userId="me", id=msg_id, format="raw")
                        .execute()
                    )
                    yield get_message_impl(msg_id, message)
                except HttpError as e:
                    print(f"Error fetching message {msg_id}: {e}")
                    continue

        except HttpError as e:
            print(f"Error fetching messages: {e}")

    def send_message(self, to: str, subject: str, body: str) -> bool:
        """Send a new email message."""
        try:
            # Create message
            message_text = f"To: {to}\nSubject: {subject}\n\n{body}"
            raw_message = base64.urlsafe_b64encode(message_text.encode()).decode()

            message = {"raw": raw_message}

            # Send message
            self.service.users().messages().send(userId="me", body=message).execute()
            return True

        except HttpError as e:
            print(f"Error sending message: {e}")
            return False

    def delete_message(self, message_id: str) -> bool:
        """Delete a message by its ID."""
        try:
            self.service.users().messages().delete(userId="me", id=message_id).execute()
            return True

        except HttpError as e:
            print(f"Error deleting message {message_id}: {e}")
            return False

    def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read."""
        try:
            # Remove UNREAD label to mark as read
            modify_request = {"removeLabelIds": ["UNREAD"]}
            self.service.users().messages().modify(
                userId="me", id=message_id, body=modify_request
            ).execute()
            return True

        except HttpError as e:
            print(f"Error marking message {message_id} as read: {e}")
            return False


def get_client_impl(credentials_path: str = "credentials.json") -> Client:
    """Create a GmailClient instance.

    Args:
        credentials_path: Path to Gmail API credentials file.

    Returns:
        Client: GmailClient instance conforming to Client protocol.
    """
    return GmailClient(credentials_path)


# Override the protocol factory function
mail_client_api.get_client = get_client_impl


__all__ = ["GmailClient", "get_client_impl"]
