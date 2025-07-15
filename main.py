"""Gmail client demonstration script."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from gmail_client import get_client


def main() -> None:
    """Demonstrate Gmail client functionality."""
    try:
        # Initialize client
        print("Initializing Gmail client...")
        client = get_client()

        # Get messages
        print("Fetching messages...")
        message_count = 0
        for message in client.get_messages():
            message_count += 1
            print(f"\n--- Message {message_count} ---")
            print(f"ID: {message.id}")
            print(f"From: {message.from_}")
            print(f"To: {message.to}")
            print(f"Subject: {message.subject}")
            print(f"Date: {message.date}")
            print(f"Body: {message.body[:100]}...")

            # Limit output for demo
            if message_count >= 5:
                break

        print(f"\nTotal messages processed: {message_count}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Created a Google Cloud project")
        print("2. Enabled Gmail API")
        print("3. Downloaded credentials.json to project root")


if __name__ == "__main__":
    main()
