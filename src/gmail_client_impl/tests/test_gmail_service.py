"""Unit tests for GmailEmailService authentication and API operations."""

import json
import os
from unittest.mock import Mock, mock_open, patch

import pytest
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

from gmail_client_impl import GmailEmailService
from gmail_client_impl._service import (
    AuthenticationError,
    GmailAPIError,
    MessageNotFoundError,
    QuotaExceededError,
    InvalidQueryError,
)


class TestGmailEmailService:
    """Test suite for GmailEmailService core functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        # Mock credentials to avoid real authentication
        self.mock_credentials = Mock(spec=Credentials)
        self.mock_credentials.valid = True
        self.mock_credentials.expired = False
        self.mock_credentials.refresh_token = "mock_refresh_token"

        # Mock Gmail service
        self.mock_gmail_service = Mock()

    @pytest.mark.unit
    def test_initialization_with_default_parameters(self) -> None:
        """Test GmailEmailService initialization with default parameters."""
        with patch.object(GmailEmailService, '_initialize_gmail_service', return_value=self.mock_gmail_service):
            service = GmailEmailService()
            
            assert service._interactive_mode is False
            assert service._credentials_path == GmailEmailService.DEFAULT_CREDENTIALS_FILE
            assert service._token_path == GmailEmailService.DEFAULT_TOKEN_FILE

    @pytest.mark.unit
    def test_initialization_with_custom_parameters(self) -> None:
        """Test GmailEmailService initialization with custom parameters."""
        with patch.object(GmailEmailService, '_initialize_gmail_service', return_value=self.mock_gmail_service):
            service = GmailEmailService(
                enable_interactive_auth=True,
                credentials_file="custom_creds.json",
                token_file="custom_token.json"
            )
            
            assert service._interactive_mode is True
            assert service._credentials_path == "custom_creds.json"
            assert service._token_path == "custom_token.json"

    @pytest.mark.unit
    def test_authentication_with_environment_variables(self) -> None:
        """Test authentication using environment variables (headless mode)."""
        # Mock environment variables
        env_vars = {
            'GMAIL_CLIENT_ID': 'mock_client_id',
            'GMAIL_CLIENT_SECRET': 'mock_client_secret',
            'GMAIL_REFRESH_TOKEN': 'mock_refresh_token'
        }
        
        # Create a proper mock credentials instance
        mock_creds_instance = Mock()
        mock_creds_instance.valid = True
        mock_creds_instance.refresh = Mock()
        
        with patch.dict(os.environ, env_vars), \
             patch('gmail_client_impl._service.Credentials', return_value=mock_creds_instance) as mock_creds_class, \
             patch('gmail_client_impl._service.Request') as mock_request, \
             patch('googleapiclient.discovery.build', return_value=self.mock_gmail_service):
            
            service = GmailEmailService()
            
            # Verify credentials were created with environment variables
            mock_creds_class.assert_called_once_with(
                token=None,
                refresh_token='mock_refresh_token',
                id_token=None,
                token_uri="https://oauth2.googleapis.com/token",
                client_id='mock_client_id',
                client_secret='mock_client_secret',
                scopes=GmailEmailService.GMAIL_SCOPES,
            )
            
            # Verify credentials were refreshed
            mock_creds_instance.refresh.assert_called_once()

    @pytest.mark.unit
    def test_authentication_with_existing_valid_token(self) -> None:
        """Test authentication using existing valid token file."""
        # Mock valid credentials from file
        mock_token_data = {
            'token': 'mock_access_token',
            'refresh_token': 'mock_refresh_token',
            'client_id': 'mock_client_id',
            'client_secret': 'mock_client_secret'
        }
        
        with patch('os.path.exists', return_value=True), \
             patch('google.oauth2.credentials.Credentials.from_authorized_user_file') as mock_from_file, \
             patch('googleapiclient.discovery.build', return_value=self.mock_gmail_service):
            
            mock_from_file.return_value = self.mock_credentials
            
            service = GmailEmailService()
            
            # Verify credentials were loaded from file
            mock_from_file.assert_called_once_with(
                GmailEmailService.DEFAULT_TOKEN_FILE,
                GmailEmailService.GMAIL_SCOPES
            )

    @pytest.mark.unit
    def test_authentication_with_expired_credentials_refresh_success(self) -> None:
        """Test authentication with expired credentials that refresh successfully."""
        expired_credentials = Mock(spec=Credentials)
        expired_credentials.valid = False
        expired_credentials.expired = True
        expired_credentials.refresh_token = "mock_refresh_token"
        
        # After refresh, credentials become valid
        refreshed_credentials = Mock(spec=Credentials)
        refreshed_credentials.valid = True
        
        with patch('os.path.exists', return_value=True), \
             patch('google.oauth2.credentials.Credentials.from_authorized_user_file', return_value=expired_credentials), \
             patch('google.auth.transport.requests.Request') as mock_request, \
             patch('googleapiclient.discovery.build', return_value=self.mock_gmail_service):
            
            # Mock successful refresh
            def refresh_side_effect(request):
                expired_credentials.valid = True
            expired_credentials.refresh.side_effect = refresh_side_effect
            
            service = GmailEmailService()
            
            # Verify refresh was attempted
            expired_credentials.refresh.assert_called_once()

    @pytest.mark.unit
    def test_authentication_missing_credentials_file_no_env_vars(self) -> None:
        """Test authentication failure when credentials file is missing and no environment variables."""
        with patch('os.path.exists', return_value=False), \
             patch.dict(os.environ, {}, clear=True):
            
            with pytest.raises(FileNotFoundError) as exc_info:
                GmailEmailService()
            
            assert "Credentials file not found" in str(exc_info.value)
            assert "credentials.json" in str(exc_info.value)

    @pytest.mark.unit
    def test_authentication_interactive_mode_disabled_error(self) -> None:
        """Test authentication error when interactive mode is disabled but required."""
        with patch('os.path.exists', return_value=True), \
             patch('google.oauth2.credentials.Credentials.from_authorized_user_file', return_value=None), \
             patch.dict(os.environ, {}, clear=True):
            
            with pytest.raises(AuthenticationError) as exc_info:
                GmailEmailService(enable_interactive_auth=False)
            
            assert "Interactive authentication disabled" in str(exc_info.value)

    @pytest.mark.unit
    def test_fetch_message_by_id_success(self) -> None:
        """Test successful message fetch by ID."""
        message_id = "test_message_123"
        mock_gmail_response = {
            'id': message_id,
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Subject'},
                    {'name': 'From', 'value': 'test@example.com'}
                ]
            },
            'internalDate': '1640995200000'
        }
        
        # Create a fresh mock for each test to avoid call conflicts
        mock_get = Mock()
        mock_get.return_value.execute.return_value = mock_gmail_response
        self.mock_gmail_service.users.return_value.messages.return_value.get = mock_get
        
        with patch.object(GmailEmailService, '_initialize_gmail_service', return_value=self.mock_gmail_service), \
             patch('email_message.create_message') as mock_create_message:
            
            service = GmailEmailService()
            mock_create_message.return_value = Mock()
            
            result = service.fetch_message_by_id(message_id)
            
            # Verify Gmail API was called correctly
            mock_get.assert_called_once_with(
                userId="me",
                id=message_id,
                format="full"
            )
            
            # Verify message creation was called
            mock_create_message.assert_called_once_with(
                msg_id=message_id,
                raw_message_data=json.dumps(mock_gmail_response)
            )

    @pytest.mark.unit
    def test_fetch_message_by_id_not_found(self) -> None:
        """Test message fetch when message is not found."""
        message_id = "nonexistent_message"
        
        # Mock 404 error
        mock_response = Mock()
        mock_response.status = 404
        http_error = HttpError(resp=mock_response, content=b"Not found")
        
        self.mock_gmail_service.users().messages().get().execute.side_effect = http_error
        
        with patch.object(GmailEmailService, '_initialize_gmail_service', return_value=self.mock_gmail_service):
            service = GmailEmailService()
            
            with pytest.raises(MessageNotFoundError) as exc_info:
                service.fetch_message_by_id(message_id)
            
            assert message_id in str(exc_info.value)

    @pytest.mark.unit
    def test_fetch_message_by_id_authentication_error(self) -> None:
        """Test message fetch with authentication error."""
        message_id = "test_message"
        
        # Mock 401 error
        mock_response = Mock()
        mock_response.status = 401
        http_error = HttpError(resp=mock_response, content=b"Unauthorized")
        
        self.mock_gmail_service.users().messages().get().execute.side_effect = http_error
        
        with patch.object(GmailEmailService, '_initialize_gmail_service', return_value=self.mock_gmail_service):
            service = GmailEmailService()
            
            with pytest.raises(AuthenticationError) as exc_info:
                service.fetch_message_by_id(message_id)
            
            assert "authentication expired or invalid" in str(exc_info.value).lower()

    @pytest.mark.unit
    def test_search_messages_invalid_query(self) -> None:
        """Test search with invalid query string."""
        # Mock 400 error for bad query
        mock_response = Mock()
        mock_response.status = 400
        http_error = HttpError(resp=mock_response, content=b"Bad Request")
        
        # Mock the list method to raise the error
        mock_list = Mock()
        mock_list.return_value.execute.side_effect = http_error
        self.mock_gmail_service.users.return_value.messages.return_value.list = mock_list
        
        with patch.object(GmailEmailService, '_initialize_gmail_service', return_value=self.mock_gmail_service):
            service = GmailEmailService()
            
            with pytest.raises(InvalidQueryError) as exc_info:
                list(service.search_messages("invalid:query:syntax"))
            
            assert "Invalid Gmail search syntax" in str(exc_info.value)

    @pytest.mark.unit
    def test_search_messages_empty_criteria_error(self) -> None:
        """Test search with empty criteria."""
        with patch.object(GmailEmailService, '_initialize_gmail_service', return_value=self.mock_gmail_service):
            service = GmailEmailService()
            
            with pytest.raises(InvalidQueryError) as exc_info:
                list(service.search_messages("   "))  # Empty/whitespace only
            
            assert "Search criteria cannot be empty" in str(exc_info.value)

    @pytest.mark.unit
    def test_fetch_messages_quota_exceeded(self) -> None:
        """Test fetch messages with quota exceeded error."""
        # Mock 429 error (rate limit)
        mock_response = Mock()
        mock_response.status = 429
        http_error = HttpError(resp=mock_response, content=b"Quota exceeded")
        
        self.mock_gmail_service.users().messages().list.side_effect = http_error
        
        with patch.object(GmailEmailService, '_initialize_gmail_service', return_value=self.mock_gmail_service):
            service = GmailEmailService()
            
            with pytest.raises(QuotaExceededError) as exc_info:
                list(service.fetch_messages(limit=10))
            
            assert "rate limit exceeded" in str(exc_info.value).lower()

    @pytest.mark.unit
    def test_remove_message_success(self) -> None:
        """Test successful message removal."""
        message_id = "message_to_delete"
        
        # Mock successful API call
        mock_trash = Mock()
        mock_trash.return_value.execute.return_value = {}
        self.mock_gmail_service.users.return_value.messages.return_value.trash = mock_trash
        
        with patch.object(GmailEmailService, '_initialize_gmail_service', return_value=self.mock_gmail_service):
            service = GmailEmailService()
            
            result = service.remove_message(message_id)
            
            assert result is True
            mock_trash.assert_called_once_with(
                userId="me",
                id=message_id
            )

    @pytest.mark.unit
    def test_remove_message_permission_error(self) -> None:
        """Test message removal with insufficient permissions."""
        message_id = "protected_message"
        
        # Mock 403 error
        mock_response = Mock()
        mock_response.status = 403
        http_error = HttpError(resp=mock_response, content=b"Forbidden")
        
        self.mock_gmail_service.users().messages().trash.side_effect = http_error
        
        with patch.object(GmailEmailService, '_initialize_gmail_service', return_value=self.mock_gmail_service):
            service = GmailEmailService()
            
            with pytest.raises(PermissionError) as exc_info:
                service.remove_message(message_id)
            
            assert "Insufficient permissions" in str(exc_info.value)

    @pytest.mark.unit
    def test_mark_message_read_success(self) -> None:
        """Test marking message as read."""
        message_id = "message_to_mark_read"
        
        # Mock successful label modification
        mock_modify = Mock()
        mock_modify.return_value.execute.return_value = {}
        self.mock_gmail_service.users.return_value.messages.return_value.modify = mock_modify
        
        with patch.object(GmailEmailService, '_initialize_gmail_service', return_value=self.mock_gmail_service):
            service = GmailEmailService()
            
            result = service.mark_message_read(message_id)
            
            assert result is True
            mock_modify.assert_called_once_with(
                userId="me",
                id=message_id,
                body={"removeLabelIds": ["UNREAD"]}
            )

    @pytest.mark.unit
    def test_mark_message_unread_success(self) -> None:
        """Test marking message as unread."""
        message_id = "message_to_mark_unread"
        
        # Mock successful label modification
        mock_modify = Mock()
        mock_modify.return_value.execute.return_value = {}
        self.mock_gmail_service.users.return_value.messages.return_value.modify = mock_modify
        
        with patch.object(GmailEmailService, '_initialize_gmail_service', return_value=self.mock_gmail_service):
            service = GmailEmailService()
            
            result = service.mark_message_unread(message_id)
            
            assert result is True
            mock_modify.assert_called_once_with(
                userId="me",
                id=message_id,
                body={"addLabelIds": ["UNREAD"]}
            )

    @pytest.mark.unit
    def test_save_credentials_success(self) -> None:
        """Test successful credentials saving."""
        mock_creds = Mock()
        mock_creds.to_json.return_value = '{"token": "mock_token"}'
        
        with patch.object(GmailEmailService, '_initialize_gmail_service', return_value=self.mock_gmail_service), \
             patch('builtins.open', mock_open()) as mock_file:
            
            service = GmailEmailService()
            service._save_credentials(mock_creds)
            
            # Verify file was opened for writing
            mock_file.assert_called_once_with(service._token_path, 'w')
            # Verify credentials JSON was written
            mock_file().write.assert_called_once_with('{"token": "mock_token"}')

    @pytest.mark.unit
    def test_save_credentials_handles_exceptions(self) -> None:
        """Test that save_credentials handles exceptions gracefully."""
        mock_creds = Mock()
        mock_creds.to_json.return_value = '{"token": "mock_token"}'
        
        with patch.object(GmailEmailService, '_initialize_gmail_service', return_value=self.mock_gmail_service), \
             patch('builtins.open', side_effect=IOError("Permission denied")):
            
            service = GmailEmailService()
            # Should not raise exception
            service._save_credentials(mock_creds)