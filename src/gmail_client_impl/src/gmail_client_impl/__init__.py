"""Gmail Client Implementation - Concrete Gmail API service implementation.

This module provides the GmailEmailService class that implements the EmailService
protocol using Google's Gmail API. It handles OAuth2 authentication, API calls,
error handling, and rate limiting for production use.

Key Features:
    - OAuth2 authentication with multiple modes (interactive/headless)
    - Comprehensive Gmail API integration
    - Robust error handling and retry logic
    - Rate limiting and quota management
    - Batch operations for performance
    - Automatic dependency injection registration

Example:
    ```python
    from gmail_client_impl import GmailEmailService

    # Create service with interactive auth
    service = GmailEmailService(interactive=True)

    # Use standard EmailService interface
    messages = list(service.fetch_messages(limit=10))
    for msg in messages:
        print(f"Subject: {msg.subject}")
    ```

"""

import email_client_api

from ._service import GmailEmailService

# Export main class for documentation
__all__ = ["GmailEmailService", "create_gmail_service"]


def create_gmail_service(interactive: bool = False, provider: str = "gmail") -> email_client_api.EmailService:
    """Factory function to create a Gmail email service instance.

    Args:
        interactive: Enable interactive OAuth2 flow if True
        provider: Email provider identifier (only "gmail" supported)

    Returns:
        email_client_api.EmailService: Gmail service implementation

    Raises:
        ValueError: If unsupported provider is specified
        AuthenticationError: If authentication setup fails

    """
    if provider != "gmail":
        msg = f"Unsupported provider: {provider}. Only 'gmail' is supported."
        raise ValueError(msg)

    return GmailEmailService(enable_interactive_auth=interactive)


# --- Dependency Injection ---
# Override the create_client function in the protocol package
# Now anyone calling email_client_api.create_client() gets our Gmail implementation
email_client_api.create_client = create_gmail_service
# --- Dependency Injection ---
