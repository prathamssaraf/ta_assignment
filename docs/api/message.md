# Message Protocol Reference

The `Message` protocol defines the interface for email message objects.

::: message.Message

## Factory Function

::: message.get_message

## Usage Examples

### Accessing Message Properties

```python
from gmail_client import get_client

client = get_client()

for message in client.get_messages():
    # Access all message properties
    print(f"ID: {message.id}")
    print(f"From: {message.from_}")
    print(f"To: {message.to}")
    print(f"Subject: {message.subject}")
    print(f"Date: {message.date}")
    print(f"Body: {message.body}")
    print("-" * 50)
```

### Message Filtering

```python
# Filter messages by sender
def get_messages_from(client, sender_email):
    return [
        msg for msg in client.get_messages()
        if sender_email in msg.from_
    ]

# Filter by subject keywords
def get_messages_with_subject(client, keyword):
    return [
        msg for msg in client.get_messages()
        if keyword.lower() in msg.subject.lower()
    ]

# Usage
urgent_messages = get_messages_with_subject(client, "urgent")
boss_messages = get_messages_from(client, "boss@company.com")
```

### Message Processing

```python
import re
from datetime import datetime

def process_messages(client):
    for message in client.get_messages():
        # Extract email addresses from body
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', message.body)
        
        # Check for attachments (basic detection)
        has_attachments = "attachment" in message.body.lower()
        
        # Parse date (implementation specific)
        try:
            # This would depend on the date format
            parsed_date = datetime.strptime(message.date, "%a, %d %b %Y %H:%M:%S %z")
        except:
            parsed_date = None
        
        print(f"Message: {message.subject}")
        print(f"  Emails found: {len(emails)}")
        print(f"  Has attachments: {has_attachments}")
        print(f"  Parsed date: {parsed_date}")
```

## Property Details

### id

Unique identifier for the message within the email system.

**Type:** `str`

**Example:**
```python
message_id = message.id
print(f"Message ID: {message_id}")

# Use ID for operations
client.mark_as_read(message_id)
client.delete_message(message_id)
```

### from_

The sender's email address. Note the underscore suffix to avoid conflict with Python's `from` keyword.

**Type:** `str`

**Example:**
```python
sender = message.from_
print(f"Message from: {sender}")

# Extract domain
domain = sender.split('@')[1] if '@' in sender else ''
print(f"Sender domain: {domain}")
```

### to

The recipient's email address (your email when reading your inbox).

**Type:** `str`

**Example:**
```python
recipient = message.to
print(f"Message to: {recipient}")

# Check if message was sent to a specific address
if "work@company.com" in recipient:
    print("This is a work email")
```

### subject

The message subject line.

**Type:** `str`

**Example:**
```python
subject = message.subject
print(f"Subject: {subject}")

# Subject-based filtering
if any(keyword in subject.lower() for keyword in ["urgent", "asap", "emergency"]):
    print("This message needs immediate attention!")
```

### body

The main content of the message. For multipart messages, this contains the plain text portion.

**Type:** `str`

**Example:**
```python
body = message.body
print(f"Body length: {len(body)} characters")

# Preview body
preview = body[:100] + "..." if len(body) > 100 else body
print(f"Preview: {preview}")

# Search in body
if "meeting" in body.lower():
    print("This message mentions a meeting")
```

### date

The message timestamp as a string. Format may vary depending on the email system.

**Type:** `str`

**Example:**
```python
date_str = message.date
print(f"Date: {date_str}")

# Note: Date parsing would need to be implemented based on format
# Common formats include:
# "Mon, 15 Jan 2025 10:00:00 +0000"
# "2025-01-15T10:00:00Z"
```

## Message Content Handling

### Plain Text Extraction

For multipart messages (HTML + plain text), the Message protocol provides the plain text content:

```python
def extract_text_content(message):
    # The protocol implementation handles multipart extraction
    text = message.body
    
    # Additional processing if needed
    lines = text.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    
    return '\n'.join(non_empty_lines)
```

### Content Analysis

```python
def analyze_message_content(message):
    analysis = {
        'word_count': len(message.body.split()),
        'line_count': len(message.body.split('\n')),
        'has_urls': 'http' in message.body,
        'has_phone': any(char.isdigit() for char in message.body),
        'is_short': len(message.body) < 100
    }
    return analysis

# Usage
for message in client.get_messages():
    stats = analyze_message_content(message)
    if stats['is_short']:
        print(f"Short message: {message.subject}")
```

## Protocol Compliance

Any class implementing the `Message` protocol must provide all six properties as read-only attributes:

```python
from message import Message

class CustomMessage:
    def __init__(self, data):
        self._data = data
    
    @property
    def id(self) -> str:
        return self._data['id']
    
    @property
    def from_(self) -> str:
        return self._data['from']
    
    # ... implement all other properties

# Verify protocol compliance
custom_msg = CustomMessage({'id': '123', 'from': 'test@example.com', ...})
assert isinstance(custom_msg, Message)
```

## Testing with Messages

```python
from unittest.mock import Mock
from message import Message

def test_message_processing():
    # Create mock message for testing
    mock_message = Mock(spec=Message)
    mock_message.id = "test-123"
    mock_message.from_ = "sender@example.com"
    mock_message.to = "recipient@example.com"
    mock_message.subject = "Test Subject"
    mock_message.body = "Test message body"
    mock_message.date = "2025-01-15 10:00:00"
    
    # Test your processing logic
    assert mock_message.subject == "Test Subject"
    assert "sender@example.com" in mock_message.from_
```