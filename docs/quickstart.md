# Quick Start

Get up and running with Gmail Client in minutes.

## Prerequisites

- Python 3.11 or higher
- UV package manager
- Gmail account with API access

## Installation

### 1. Install UV

=== "Windows"

    ```powershell
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

=== "macOS"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "Linux"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

### 2. Set Up Project

```bash
git clone https://github.com/prathamssaraf/ta_assignment.git
cd ta_assignment
uv sync --all-extras
```

### 3. Configure Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json` to the project root

!!! tip "Credential Setup"
    The `credentials.json` file should contain your OAuth 2.0 client configuration. Keep this file secure and never commit it to version control.

## First Usage

### Basic Message Reading

```python
from gmail_client import get_client

# Initialize the client (will prompt for OAuth on first run)
client = get_client()

# Read your latest messages
for i, message in enumerate(client.get_messages()):
    print(f"Message {i+1}:")
    print(f"  From: {message.from_}")
    print(f"  Subject: {message.subject}")
    print(f"  Date: {message.date}")
    print(f"  Body: {message.body[:100]}...")
    print()
    
    if i >= 4:  # Limit to first 5 messages
        break
```

### Sending Your First Message

```python
from gmail_client import get_client

client = get_client()

# Send a test message
success = client.send_message(
    to="your-email@example.com",  # Send to yourself for testing
    subject="Test from Gmail Client",
    body="This message was sent using the Gmail Client library!"
)

if success:
    print("Message sent successfully!")
else:
    print("Failed to send message")
```

### Complete CRUD Example

```python
from gmail_client import get_client

client = get_client()

# 1. Read messages
print("Reading messages...")
messages = list(client.get_messages())
print(f"Found {len(messages)} messages")

if messages:
    first_message = messages[0]
    print(f"Latest message from: {first_message.from_}")
    
    # 2. Mark as read
    print("Marking message as read...")
    client.mark_as_read(first_message.id)
    
    # 3. Send a reply (example)
    print("Sending reply...")
    client.send_message(
        to=first_message.from_,
        subject=f"Re: {first_message.subject}",
        body="Thank you for your message!"
    )
    
    # 4. Delete message (be careful!)
    # client.delete_message(first_message.id)
```

## Running Tests

Verify your setup by running the test suite:

```bash
# Run unit tests only
uv run pytest tests/ -m "unit"

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

## Development Setup

For development work:

```bash
# Install development dependencies
uv sync --all-extras

# Run code formatting
uv run ruff format

# Run linting
uv run ruff check

# Run type checking
uv run mypy src/

# Serve documentation locally
uv run mkdocs serve
```

## Next Steps

- 📖 Read the [User Guide](guide/installation.md) for detailed usage instructions
- 🔧 Check the [API Reference](api/client.md) for complete method documentation
- 🧪 Learn about [Testing](development/testing.md) your code with Gmail Client
- 🏗️ Understand the [Architecture](development/architecture.md) and design patterns

## Troubleshooting

### Common Issues

**"Credentials file not found"**
: Make sure `credentials.json` is in your project root directory

**"Permission denied" during OAuth**
: Ensure your Google Cloud project has the Gmail API enabled

**Import errors**
: Run `uv sync --all-extras` to install all dependencies

**Test failures**
: Integration tests require valid Gmail credentials

For more help, see our [Error Handling Guide](guide/error-handling.md).