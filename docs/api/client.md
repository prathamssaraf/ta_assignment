# Client Protocol Reference

The `Client` protocol defines the core interface for email client operations.

::: mail_client_api.Client

## Factory Function

::: mail_client_api.get_client

## Usage Examples

### Basic Client Operations

```python
from gmail_client import get_client

# Get client instance
client = get_client()

# Iterate through messages
for message in client.get_messages():
    print(f"Subject: {message.subject}")
```

### Sending Messages

```python
# Send a simple message
success = client.send_message(
    to="recipient@example.com",
    subject="Hello from Gmail Client",
    body="This is a test message sent using the Gmail Client library."
)

if success:
    print("Message sent successfully!")
```

### Message Management

```python
# Get all messages
messages = list(client.get_messages())

for message in messages:
    # Mark as read
    if client.mark_as_read(message.id):
        print(f"Marked message '{message.subject}' as read")
    
    # Delete if needed (be careful!)
    # if client.delete_message(message.id):
    #     print(f"Deleted message '{message.subject}'")
```

## Method Details

### get_messages()

Returns an iterator over all messages in the inbox. Messages are yielded as they are fetched from the Gmail API.

**Returns:** `Iterator[Message]`

**Example:**
```python
# Process messages one by one (memory efficient)
for message in client.get_messages():
    if "urgent" in message.subject.lower():
        print(f"Urgent message: {message.subject}")

# Or collect all messages (use with caution for large inboxes)
all_messages = list(client.get_messages())
```

### send_message(to, subject, body)

Sends a new email message to the specified recipient.

**Parameters:**
- `to` (str): Recipient email address
- `subject` (str): Message subject line
- `body` (str): Message body content (plain text)

**Returns:** `bool` - `True` if successful, `False` otherwise

**Example:**
```python
# Send with error handling
try:
    success = client.send_message(
        to="colleague@company.com",
        subject="Project Update",
        body="The project is on track for completion next week."
    )
    if not success:
        print("Failed to send message")
except Exception as e:
    print(f"Error sending message: {e}")
```

### delete_message(message_id)

Permanently deletes a message from the Gmail account.

!!! warning "Permanent Action"
    This action cannot be undone. The message will be permanently deleted from Gmail.

**Parameters:**
- `message_id` (str): Unique identifier of the message to delete

**Returns:** `bool` - `True` if successful, `False` otherwise

**Example:**
```python
# Delete with confirmation
message_to_delete = messages[0]
if input(f"Delete message '{message_to_delete.subject}'? (y/n): ") == 'y':
    if client.delete_message(message_to_delete.id):
        print("Message deleted successfully")
    else:
        print("Failed to delete message")
```

### mark_as_read(message_id)

Marks a message as read by removing the UNREAD label.

**Parameters:**
- `message_id` (str): Unique identifier of the message to mark as read

**Returns:** `bool` - `True` if successful, `False` otherwise

**Example:**
```python
# Mark multiple messages as read
unread_messages = [msg for msg in client.get_messages() if "UNREAD" in msg.labels]

for message in unread_messages:
    if client.mark_as_read(message.id):
        print(f"Marked '{message.subject}' as read")
```

## Error Handling

All client methods handle Gmail API errors gracefully and return `False` for operations that fail. For more detailed error information, check the console output.

```python
# Robust error handling pattern
try:
    client = get_client()
    
    # Attempt operations with fallback
    if not client.send_message("test@example.com", "Test", "Body"):
        print("Send operation failed - check credentials and network")
        
except FileNotFoundError:
    print("Gmail credentials not found - run setup first")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Protocol Compliance

Any class implementing the `Client` protocol must provide all four methods with matching signatures. This enables easy testing and alternative implementations.

```python
from mail_client_api import Client
from unittest.mock import Mock

# Create a mock client for testing
mock_client = Mock(spec=Client)
mock_client.get_messages.return_value = iter([])
mock_client.send_message.return_value = True

# Verify protocol compliance
assert isinstance(mock_client, Client)
```