# Gmail Client

A professional, reusable Gmail client library with comprehensive CRUD operations built following modern Python best practices.

## Features

- **Protocol-based design** for easy testing and extensibility
- **Complete CRUD operations** for Gmail messages
- **OAuth 2.0 authentication** with secure credential management
- **Comprehensive testing** with unit, integration, and e2e tests
- **Type-safe implementation** with strict MyPy checking
- **Modern tooling** with UV, Ruff, and automated CI/CD

## Quick Start

### Prerequisites

- Python 3.11+
- UV package manager

### Installation

1. Install UV (if not already installed):
```bash
# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone and set up the project:
```bash
git clone <repository-url>
cd ta_assignment
uv sync --all-extras
```

3. Set up Gmail API credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download `credentials.json` to project root

### Basic Usage

```python
from gmail_client import get_client

# Initialize client
client = get_client()

# Read messages
for message in client.get_messages():
    print(f"From: {message.from_}")
    print(f"Subject: {message.subject}")
    print(f"Body: {message.body[:100]}...")

# Send a message
success = client.send_message(
    to="recipient@example.com",
    subject="Hello from Gmail Client",
    body="This is a test message."
)

# Mark message as read
client.mark_as_read(message_id="123456")

# Delete a message
client.delete_message(message_id="123456")
```

## Development

### Running Tests

```bash
# Unit tests only
uv run pytest tests/ -m "unit"

# Integration tests (requires Gmail API setup)
uv run pytest tests/ -m "integration"

# All tests
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
uv run ruff format

# Lint code
uv run ruff check

# Type checking
uv run mypy src/
```

### Documentation

```bash
# Serve documentation locally
uv run mkdocs serve

# Build documentation
uv run mkdocs build
```

## Architecture

The project follows a protocol-based architecture with clear separation between interfaces and implementations:

- `src/message/` - Message protocol definition
- `src/message_impl/` - Gmail message implementation
- `src/gmail_client_protocol/` - Client protocol definition  
- `src/gmail_client_impl/` - Gmail client implementation

This design enables easy testing with mocks and allows for future implementations (e.g., Outlook, Yahoo Mail).

## API Reference

### Client Protocol

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `get_messages()` | Retrieve all messages | None | `Iterator[Message]` |
| `send_message()` | Send a new message | `to`, `subject`, `body` | `bool` |
| `delete_message()` | Delete a message | `message_id` | `bool` |
| `mark_as_read()` | Mark message as read | `message_id` | `bool` |

### Message Protocol

| Property | Description | Type |
|----------|-------------|------|
| `id` | Unique message identifier | `str` |
| `from_` | Sender email address | `str` |
| `to` | Recipient email address | `str` |
| `subject` | Message subject | `str` |
| `body` | Message body content | `str` |
| `date` | Message timestamp | `str` |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and quality checks
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.