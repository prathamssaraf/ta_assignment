"""Gmail client demonstration script."""

from gmail_client import get_client

# Constants
MAX_DEMO_MESSAGES = 5


def main() -> None:
    """Demonstrate Gmail client functionality."""
    try:
        # Initialize client
        client = get_client()

        # Get messages
        for message_count, _message in enumerate(client.get_messages(), 1):
            # Limit output for demo
            if message_count >= MAX_DEMO_MESSAGES:
                break


    except (ImportError, FileNotFoundError):
        pass
    except (RuntimeError, OSError):
        pass


if __name__ == "__main__":
    main()
