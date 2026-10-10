import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlmodel import Session, select

from database.database import get_session
from models.models import (
    Conversation,
    ConversationCreate,
    ConversationParticipant,
    ConversationRead,
    Message,
    MessageCreate,
    MessageRead,
    User,
)
from repositories.message_repo import (
    add_participant,
    create_conversation,
    create_message,
    get_conversation_by_id,
    get_conversation_messages,
    get_conversation_participants,
    get_user_conversations,
    is_participant,
)
from repositories.user_repo import get_user_by_id, get_user_by_username
from services.security import get_current_active_user, verify_token
from services.websocket_manager import manager
from utils.logging import logger

router = APIRouter(prefix="/conversations", tags=["conversations"])

session: Session = Depends(get_session)
current_user: User = Depends(get_current_active_user)


@router.post("/", response_model=ConversationRead, status_code=status.HTTP_201_CREATED)
def create_conversation_endpoint(
    conversation_data: ConversationCreate,
    current_user: User = current_user,
    session: Session = session,
) -> Conversation:
    """Create a new one-to-one conversation."""
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User ID is missing"
        )

    # Cannot create conversation with yourself
    if conversation_data.participant_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create a conversation with yourself",
        )

    # Validate participant exists
    participant = get_user_by_id(session, conversation_data.participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {conversation_data.participant_id} not found",
        )

    # Check if conversation already exists between these two users
    existing_conversation: Conversation | None = session.exec(
        select(Conversation)
        .join(ConversationParticipant, Conversation.id == ConversationParticipant.conversation_id)
        .where(ConversationParticipant.user_id == current_user.id)
        .where(
            Conversation.id.in_(  # type: ignore
                select(ConversationParticipant.conversation_id).where(
                    ConversationParticipant.user_id == conversation_data.participant_id
                )
            )
        )
    ).first()

    if existing_conversation:
        return existing_conversation

    # Create conversation with participant's username as title
    conversation = Conversation(title=f"Chat with {participant.username}")
    created_conversation = create_conversation(session, conversation)

    if not created_conversation.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Conversation creation failed",
        )

    # Add both participants
    add_participant(session, created_conversation.id, current_user.id)
    add_participant(session, created_conversation.id, conversation_data.participant_id)

    return created_conversation


@router.get("/", response_model=list[ConversationRead])
def get_conversations(
    current_user: User = current_user,
    session: Session = session,
) -> list[Conversation]:
    """Get all conversations the current user is part of."""
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User ID is missing"
        )

    return get_user_conversations(session, current_user.id)


@router.get("/{conversation_id}", response_model=ConversationRead)
def get_conversation(
    conversation_id: int,
    current_user: User = current_user,
    session: Session = session,
) -> Conversation:
    """Get conversation details."""
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User ID is missing"
        )

    conversation = get_conversation_by_id(session, conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    # Check if user is a participant
    if not is_participant(session, conversation_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this conversation",
        )

    return conversation


@router.get("/{conversation_id}/participants", response_model=list[User])
def get_participants(
    conversation_id: int,
    current_user: User = current_user,
    session: Session = session,
) -> list[User]:
    """Get all participants in a conversation."""
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User ID is missing"
        )

    conversation = get_conversation_by_id(session, conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    # Check if user is a participant
    if not is_participant(session, conversation_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this conversation",
        )

    return get_conversation_participants(session, conversation_id)


@router.get("/{conversation_id}/messages", response_model=list[MessageRead])
def get_messages(
    conversation_id: int,
    current_user: User = current_user,
    session: Session = session,
) -> list[MessageRead]:
    """Get all messages in a conversation."""
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User ID is missing"
        )

    conversation = get_conversation_by_id(session, conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    # Check if user is a participant
    if not is_participant(session, conversation_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this conversation",
        )

    messages_with_senders = get_conversation_messages(session, conversation_id)

    result: list[MessageRead] = []
    for message, sender in messages_with_senders:
        if not message.id:
            continue

        result.append(
            MessageRead(
                id=message.id,
                content=message.content,
                sender_id=message.sender_id,
                sender_name=sender.username,
                conversation_id=message.conversation_id,
                created_at=str(message.created_at),
            )
        )

    return result


@router.post(
    "/{conversation_id}/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED
)
def send_message(
    conversation_id: int,
    message_data: MessageCreate,
    current_user: User = current_user,
    session: Session = session,
) -> MessageRead:
    """Send a message to a conversation."""
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User ID is missing"
        )

    conversation = get_conversation_by_id(session, conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    # Check if user is a participant
    if not is_participant(session, conversation_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a participant to send messages",
        )

    message = Message(
        content=message_data.content,
        sender_id=current_user.id,
        conversation_id=conversation_id,
    )
    created_message = create_message(session, message)

    if not created_message.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Message creation failed"
        )

    return MessageRead(
        id=created_message.id,
        content=created_message.content,
        sender_id=created_message.sender_id,
        sender_name=current_user.username,
        conversation_id=created_message.conversation_id,
        created_at=str(created_message.created_at),
    )


@router.websocket("/{conversation_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: int,
    token: str | None = None,
):
    """
    WebSocket endpoint for real-time messaging in a conversation.

    Client should connect with: ws://localhost:8000/conversations/{id}/ws?token={jwt_token}

    Message format:
    - Send: {"content": "message text"}
    - Receive: {"type": "message", "id": 1, "content": "...", "sender_id": 1, ...}
    """
    from database.database import engine

    # Authenticate user from token
    if not token:
        await websocket.close(code=4001, reason="Missing authentication token")
        logger.warning("WebSocket connection attempt without token")
        return

    try:
        # Verify JWT token
        payload = verify_token(token)
        username = payload.get("sub")
        if not username:
            await websocket.close(code=4001, reason="Invalid token")
            logger.warning("WebSocket connection with invalid token")
            return

        # Get user from database
        with Session(engine) as session:
            user = get_user_by_username(session, username)
            if not user or not user.id:
                await websocket.close(code=4001, reason="User not found")
                logger.warning(f"WebSocket connection for non-existent user: {username}")
                return

            # Check if user is participant in conversation
            conversation = get_conversation_by_id(session, conversation_id)
            if not conversation:
                await websocket.close(code=4004, reason="Conversation not found")
                logger.warning(
                    f"WebSocket connection to non-existent conversation: {conversation_id}"
                )
                return

            if not is_participant(session, conversation_id, user.id):
                await websocket.close(code=4003, reason="Not authorized")
                logger.warning(
                    f"User {username} attempted to connect to "
                    f"conversation {conversation_id} without permission"
                )
                return

        # Connect the WebSocket
        await manager.connect(websocket, conversation_id, user.id)
        logger.info(f"User {username} connected to conversation {conversation_id} via WebSocket")

        # Send connection confirmation
        await manager.send_personal_message(
            json.dumps(
                {
                    "type": "connection",
                    "status": "connected",
                    "conversation_id": conversation_id,
                    "user_id": user.id,
                }
            ),
            websocket,
        )

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)

                # Save message to database
                with Session(engine) as session:
                    message = Message(
                        content=message_data.get("content", ""),
                        sender_id=user.id,
                        conversation_id=conversation_id,
                    )
                    created_message = create_message(session, message)

                    if not created_message.id:
                        await manager.send_personal_message(
                            json.dumps({"type": "error", "message": "Failed to save message"}),
                            websocket,
                        )
                        logger.error(f"Failed to save message from user {username}")
                        continue

                    # Broadcast message to all participants
                    broadcast_data: dict[str, Any] = {
                        "type": "message",
                        "id": created_message.id,
                        "content": created_message.content,
                        "sender_id": created_message.sender_id,
                        "sender_name": user.username,
                        "conversation_id": created_message.conversation_id,
                        "created_at": str(created_message.created_at),
                    }

                    await manager.broadcast_to_conversation(
                        broadcast_data,
                        conversation_id,
                        exclude_sender=None,  # Set to websocket to exclude sender
                    )
                    logger.info(
                        f"Message broadcast to conversation {conversation_id} from user {username}"
                    )

        except WebSocketDisconnect:
            manager.disconnect(websocket, conversation_id)
            logger.info(f"User {username} disconnected from conversation {conversation_id}")
            # Optionally broadcast that user left
            await manager.broadcast_to_conversation(
                {"type": "user_left", "user_id": user.id, "username": username}, conversation_id
            )
        except Exception as e:
            logger.error(f"WebSocket error for user {username}: {e}")
            manager.disconnect(websocket, conversation_id)

    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        await websocket.close(code=4000, reason=f"Authentication error: {str(e)}")
