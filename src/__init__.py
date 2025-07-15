"""Gmail client package main entry point."""

# Import implementation to register factory functions
import gmail_client_impl  # noqa: F401
import message_impl  # noqa: F401

# Export main interface
from gmail_client_protocol import get_client


__all__ = ["get_client"]