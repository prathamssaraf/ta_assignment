"""Gmail client demonstration script."""

from gmail_client import get_client


def main() -> None:
    """Demonstrate Gmail client functionality."""
    try:
        # Initialize client
        client = get_client()

        # Get messages
        message_count = 0
        for _message in client.get_messages():
            message_count += 1

            # Limit output for demo
            if message_count >= 5:
                break


    except Exception:
        pass


if __name__ == "__main__":
    main()
