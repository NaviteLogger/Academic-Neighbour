# WebSocket Real-Time Messaging

This document explains how to use the WebSocket implementation for real-time messaging in the FastAPI application.

## Overview

The application now supports real-time messaging through WebSocket connections. When a user sends a message, it's instantly delivered to all participants in the conversation without the need for polling.

## Architecture

### Components

1. **WebSocket Manager** (`services/websocket_manager.py`)
   - Manages active WebSocket connections
   - Handles connection/disconnection
   - Broadcasts messages to conversation participants

2. **WebSocket Endpoint** (`routers/message_router.py`)
   - `/conversations/{conversation_id}/ws?token={jwt_token}`
   - Authenticates users via JWT token
   - Validates conversation access
   - Handles real-time message exchange

3. **Test Interface** (`static/chat.html`)
   - Web-based chat interface for testing
   - Access at: `http://localhost:8000/static/chat.html`

## Usage

### 1. Starting the Server

```bash
cd /workspaces/Python-FastAPI
python main.py
```

The server will start on `http://localhost:8000`

### 2. Testing with the Web Interface

1. Open your browser to: `http://localhost:8000/static/chat.html`
2. Enter credentials (default: `testuser` / `TestPassword123`)
3. Enter a conversation ID (use `1` for sample data)
4. Click "Login & Connect"
5. Start chatting in real-time!

You can open multiple browser tabs with different users to see real-time message delivery.

### 3. Connecting via JavaScript

```javascript
// 1. Get JWT token from login
const response = await fetch('/auth/token', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
        username: 'testuser',
        password: 'TestPassword123'
    })
});
const { access_token } = await response.json();

// 2. Connect to WebSocket
const conversationId = 1;
const ws = new WebSocket(
    `ws://localhost:8000/conversations/${conversationId}/ws?token=${access_token}`
);

// 3. Handle connection
ws.onopen = () => {
    console.log('Connected!');
};

// 4. Receive messages
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'connection') {
        console.log('Connection confirmed:', data);
    } else if (data.type === 'message') {
        console.log('New message:', data.content);
        console.log('From:', data.sender_name);
        console.log('At:', data.created_at);
    }
};

// 5. Send a message
ws.send(JSON.stringify({
    content: 'Hello, WebSocket!'
}));

// 6. Handle disconnection
ws.onclose = (event) => {
    console.log('Disconnected:', event.code, event.reason);
};
```

### 4. Python Client Example

```python
import asyncio
import websockets
import json

async def chat():
    uri = "ws://localhost:8000/conversations/1/ws?token=YOUR_JWT_TOKEN"
    
    async with websockets.connect(uri) as websocket:
        # Receive connection confirmation
        response = await websocket.recv()
        print(f"Connected: {response}")
        
        # Send a message
        await websocket.send(json.dumps({
            "content": "Hello from Python!"
        }))
        
        # Listen for messages
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received: {data}")

# Run the client
asyncio.run(chat())
```

## Message Format

### Sending Messages (Client → Server)

```json
{
  "content": "Your message here"
}
```

### Receiving Messages (Server → Client)

#### Connection Confirmation

```json
{
  "type": "connection",
  "status": "connected",
  "conversation_id": 1,
  "user_id": 1
}
```

#### New Message

```json
{
  "type": "message",
  "id": 123,
  "content": "Message text",
  "sender_id": 2,
  "sender_name": "alice",
  "conversation_id": 1,
  "created_at": "2025-11-22 10:30:00"
}
```

#### User Left

```json
{
  "type": "user_left",
  "user_id": 2,
  "username": "alice"
}
```

#### Error

```json
{
  "type": "error",
  "message": "Error description"
}
```

## WebSocket Close Codes

- `1000`: Normal closure
- `4000`: Authentication error
- `4001`: Missing or invalid token
- `4003`: Not authorized (not a conversation participant)
- `4004`: Conversation not found

## Features

✅ **Real-time messaging** - Messages appear instantly  
✅ **Multiple participants** - Broadcast to all users in a conversation  
✅ **Authentication** - JWT token-based security  
✅ **Authorization** - Only conversation participants can connect  
✅ **Persistence** - Messages are saved to the database  
✅ **Automatic reconnection** - Handles network interruptions  
✅ **Connection status** - Real-time connection state  
✅ **User presence** - Know when users join/leave  

## Testing

Run the WebSocket tests:

```bash
pytest tests/test_websocket.py -v
```

## API Endpoints

### REST API (existing)

- `POST /conversations/` - Create a new conversation
- `GET /conversations/` - List user's conversations
- `GET /conversations/{id}/messages` - Get conversation history
- `POST /conversations/{id}/messages` - Send a message (REST fallback)

### WebSocket API (new)

- `WS /conversations/{id}/ws?token={jwt}` - Real-time messaging connection

## Security Considerations

1. **Authentication Required**: All WebSocket connections require a valid JWT token
2. **Authorization Check**: Users must be conversation participants
3. **Token Expiration**: Tokens expire after 3000 minutes (configurable)
4. **Connection Validation**: Invalid connections are rejected immediately
5. **Data Validation**: All messages are validated before broadcasting

## Performance

- **Concurrent Connections**: Supports multiple simultaneous connections
- **Broadcasting**: Efficient message delivery to all participants
- **Memory Management**: Connections are properly cleaned up on disconnect
- **Database**: Messages are saved asynchronously to avoid blocking

## Troubleshooting

### Connection Issues

**Problem**: WebSocket connection fails  
**Solution**:

- Verify the JWT token is valid
- Check if user is a participant in the conversation
- Ensure the server is running

**Problem**: Messages not appearing  
**Solution**:

- Check browser console for errors
- Verify WebSocket connection is open
- Test with the provided HTML interface

**Problem**: Token expired  
**Solution**:

- Re-authenticate to get a new token
- Implement automatic token refresh in your client

## Future Enhancements

Potential features to add:

- 📝 Typing indicators
- ✅ Read receipts
- 🟢 Online/offline status
- 📎 File uploads via WebSocket
- ✏️ Message editing/deletion
- 😊 Emoji reactions
- 🔔 Push notifications
- 📊 Delivery confirmation

## Example: Complete Chat Application

See `static/chat.html` for a complete, production-ready example with:

- User authentication
- WebSocket connection management
- Real-time message display
- Automatic reconnection
- Error handling
- Beautiful UI

## Support

For issues or questions, refer to:

- FastAPI WebSocket docs: <https://fastapi.tiangolo.com/advanced/websockets/>
- WebSocket RFC: <https://tools.ietf.org/html/rfc6455>
