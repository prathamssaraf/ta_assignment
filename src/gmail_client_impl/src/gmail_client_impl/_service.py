"""Gmail service implementation with comprehensive API integration and error handling."""

import json
import os
from collections.abc import Iterator
from typing import Any

from google.auth.transport.requests import Request  # type: ignore
from google.oauth2.credentials import Credentials  # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import email_message


class GmailEmailService:
    """Gmail-specific implementation of the EmailService protocol.

    This class provides a complete Gmail API client with OAuth2 authentication,
    comprehensive error handling, and support for both interactive and headless
    authentication modes for different deployment scenarios.
    """

    # Gmail API scope for full mailbox access
    GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

    # Default credentials and token file paths
    DEFAULT_CREDENTIALS_FILE = "credentials.json"
    DEFAULT_TOKEN_FILE = "token.json"

    def __init__(
        self,
        enable_interactive_auth: bool = False,
        credentials_file: str | None = None,
        token_file: str | None = None,
    ) -> None:
        """Initialize Gmail service with authentication setup.

        Args:
            enable_interactive_auth: Allow interactive OAuth2 flow
            credentials_file: Path to OAuth2 credentials JSON file
            token_file: Path to stored access token file

        Raises:
            AuthenticationError: If authentication setup fails
            FileNotFoundError: If required credential files are missing

        """
        self._interactive_mode = enable_interactive_auth
        self._credentials_path = credentials_file or self.DEFAULT_CREDENTIALS_FILE
        self._token_path = token_file or self.DEFAULT_TOKEN_FILE

        # Initialize Gmail API service
        self._gmail_service = self._initialize_gmail_service()

    def fetch_message_by_id(self, message_id: str) -> email_message.EmailMessage:
        """Retrieve a specific Gmail message by ID."""
        try:
            # Fetch full message details from Gmail API
            message_response = (
                self._gmail_service.users()
                .messages()
                .get(
                    userId="me",
                    id=message_id,
                    format="full",  # Get complete message data including headers and body
                )
                .execute()
            )

            # Convert Gmail API response to our EmailMessage protocol
            return email_message.create_message(
                msg_id=message_id,
                raw_message_data=json.dumps(message_response),
            )

        except HttpError as e:
            if e.resp.status == 404:
                msg = f"Message {message_id} not found"
                raise MessageNotFoundError(msg) from e
            if e.resp.status == 401:
                msg = "Gmail authentication expired or invalid"
                raise AuthenticationError(msg) from e
            msg = f"Failed to fetch message {message_id}: {e}"
            raise GmailAPIError(msg) from e

    def remove_message(self, message_id: str) -> bool:
        """Permanently delete a Gmail message."""
        try:
            # Use Gmail API trash operation (moves to trash, not permanent delete)
            self._gmail_service.users().messages().trash(
                userId="me",
                id=message_id,
            ).execute()

            return True

        except HttpError as e:
            if e.resp.status == 404:
                msg = f"Message {message_id} not found"
                raise MessageNotFoundError(msg) from e
            if e.resp.status == 403:
                msg = f"Insufficient permissions to delete message {message_id}"
                raise PermissionError(msg) from e
            # Log error but don't raise - return False to indicate failure
            return False

    def mark_message_read(self, message_id: str) -> bool:
        """Mark Gmail message as read by removing UNREAD label."""
        return self._modify_message_labels(
            message_id=message_id,
            remove_labels=["UNREAD"],
            add_labels=[],
        )

    def mark_message_unread(self, message_id: str) -> bool:
        """Mark Gmail message as unread by adding UNREAD label."""
        return self._modify_message_labels(
            message_id=message_id,
            remove_labels=[],
            add_labels=["UNREAD"],
        )

    def fetch_messages(self, limit: int = 10, query: str | None = None) -> Iterator[email_message.EmailMessage]:
        """Fetch Gmail messages with optional search filtering."""
        try:
            # Build Gmail API query parameters
            list_params = {
                "userId": "me",
                "maxResults": min(limit, 500),  # Gmail API limit is 500
            }

            if query:
                list_params["q"] = query

            # Get list of message IDs from Gmail API
            messages_response = self._gmail_service.users().messages().list(**list_params).execute()
            message_list = messages_response.get("messages", [])

            # Fetch full message details for each ID
            fetched_count = 0
            for message_info in message_list:
                if fetched_count >= limit:
                    break

                message_id = message_info["id"]
                try:
                    yield self.fetch_message_by_id(message_id)
                    fetched_count += 1
                except Exception:
                    # Log error but continue with other messages
                    continue

        except HttpError as e:
            if e.resp.status == 401:
                msg = "Gmail authentication expired or invalid"
                raise AuthenticationError(msg) from e
            if e.resp.status == 429:
                msg = "Gmail API rate limit exceeded"
                raise QuotaExceededError(msg) from e
            msg = f"Failed to fetch messages: {e}"
            raise GmailAPIError(msg) from e

    def search_messages(self, search_criteria: str, max_results: int = 50) -> Iterator[email_message.EmailMessage]:
        """Search Gmail messages using Gmail's advanced query syntax."""
        try:
            # Validate search criteria
            if not search_criteria.strip():
                msg = "Search criteria cannot be empty"
                raise InvalidQueryError(msg)

            # Use the fetch_messages method with the search query
            yield from self.fetch_messages(limit=max_results, query=search_criteria)

        except HttpError as e:
            if e.resp.status == 400:
                msg = f"Invalid Gmail search syntax: {search_criteria}"
                raise InvalidQueryError(msg) from e
            raise

    # Private helper methods

    def _initialize_gmail_service(self) -> Any:
        """Initialize and authenticate Gmail API service."""
        credentials = self._get_valid_credentials()

        # Build Gmail API service
        return build("gmail", "v1", credentials=credentials)

    def _get_valid_credentials(self) -> Credentials:
        """Get valid OAuth2 credentials, refreshing or re-authenticating as needed."""
        credentials = None

        # Try to load existing token
        if os.path.exists(self._token_path):
            credentials = Credentials.from_authorized_user_file(self._token_path, self.GMAIL_SCOPES)  # type: ignore

        # Check if credentials are valid and refresh if needed
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                # Refresh expired credentials
                try:
                    credentials.refresh(Request())  # type: ignore
                except Exception:
                    credentials = None

            # If refresh failed or no credentials, perform full auth flow
            if not credentials:
                credentials = self._perform_oauth_flow()

            # Save the credentials for next run
            self._save_credentials(credentials)

        return credentials

    def _perform_oauth_flow(self) -> Credentials:
        """Perform OAuth2 authentication flow."""
        # Check for environment variables first (for CI/CD)
        client_id = os.getenv("GMAIL_CLIENT_ID")
        client_secret = os.getenv("GMAIL_CLIENT_SECRET")
        refresh_token = os.getenv("GMAIL_REFRESH_TOKEN")

        if client_id and client_secret and refresh_token:
            # Use environment variables for headless authentication
            credentials = Credentials(  # type: ignore
                token=None,  # Will be refreshed automatically
                refresh_token=refresh_token,
                id_token=None,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=self.GMAIL_SCOPES,
            )
            # Refresh to get access token
            credentials.refresh(Request())  # type: ignore
            return credentials

        # Fall back to file-based authentication
        if not os.path.exists(self._credentials_path):
            msg = (
                f"Credentials file not found: {self._credentials_path}. "
                "Please download OAuth2 credentials from Google Cloud Console."
            )
            raise FileNotFoundError(
                msg,
            )

        if not self._interactive_mode:
            msg = (
                "Interactive authentication disabled, but credentials require user interaction. "
                "Set enable_interactive_auth=True or provide environment variables."
            )
            raise AuthenticationError(
                msg,
            )

        # Perform interactive OAuth2 flow
        flow = InstalledAppFlow.from_client_secrets_file(self._credentials_path, self.GMAIL_SCOPES)  # type: ignore
        return flow.run_local_server(port=0)  # type: ignore

    def _save_credentials(self, credentials: Credentials) -> None:
        """Save credentials to token file for future use."""
        try:
            with open(self._token_path, "w") as token_file:
                token_file.write(credentials.to_json())  # type: ignore
        except Exception:
            pass

    def _modify_message_labels(self, message_id: str, remove_labels: list[str], add_labels: list[str]) -> bool:
        """Modify Gmail message labels (used for read/unread status)."""
        try:
            modify_request = {}
            if remove_labels:
                modify_request["removeLabelIds"] = remove_labels
            if add_labels:
                modify_request["addLabelIds"] = add_labels

            if not modify_request:
                return True  # Nothing to do

            self._gmail_service.users().messages().modify(
                userId="me",
                id=message_id,
                body=modify_request,
            ).execute()

            return True

        except HttpError as e:
            if e.resp.status == 404:
                msg = f"Message {message_id} not found"
                raise MessageNotFoundError(msg) from e
            return False


# Custom exception classes
class GmailAPIError(Exception):
    """Base exception for Gmail API errors."""


class AuthenticationError(GmailAPIError):
    """Authentication-related errors."""


class MessageNotFoundError(GmailAPIError):
    """Message not found errors."""


class QuotaExceededError(GmailAPIError):
    """API quota exceeded errors."""


class InvalidQueryError(GmailAPIError):
    """Invalid search query errors."""
