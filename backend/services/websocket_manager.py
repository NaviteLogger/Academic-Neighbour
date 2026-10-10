"""WebSocket connection manager for real-time messaging."""

import json
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections for real-time messaging."""

    def __init__(self):
        # Store active connections: {conversation_id: [websocket1, websocket2, ...]}
        self.active_connections: dict[int, list[WebSocket]] = {}
        # Track which user owns which connection: {websocket: user_id}
        self.connection_users: dict[WebSocket, int] = {}

    async def connect(self, websocket: WebSocket, conversation_id: int, user_id: int):
        """Accept and store a new WebSocket connection."""
        await websocket.accept()

        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []

        self.active_connections[conversation_id].append(websocket)
        self.connection_users[websocket] = user_id

    def disconnect(self, websocket: WebSocket, conversation_id: int):
        """Remove a WebSocket connection."""
        if conversation_id in self.active_connections:
            if websocket in self.active_connections[conversation_id]:
                self.active_connections[conversation_id].remove(websocket)

            # Clean up empty conversation rooms
            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]

        if websocket in self.connection_users:
            del self.connection_users[websocket]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific connection."""
        await websocket.send_text(message)

    async def broadcast_to_conversation(
        self, message: dict[str, Any], conversation_id: int, exclude_sender: WebSocket | None = None
    ):
        """Broadcast a message to all participants in a conversation."""
        if conversation_id not in self.active_connections:
            return

        message_json = json.dumps(message)

        for connection in self.active_connections[conversation_id]:
            # Optionally exclude the sender from receiving their own message
            if exclude_sender and connection == exclude_sender:
                continue
            try:
                await connection.send_text(message_json)
            except Exception as e:
                # Connection might be closed
                print(f"Failed to send message to connection: {e}")

    def get_conversation_connections_count(self, conversation_id: int) -> int:
        """Get the number of active connections for a conversation."""
        if conversation_id not in self.active_connections:
            return 0
        return len(self.active_connections[conversation_id])


# Global instance
manager = ConnectionManager()
