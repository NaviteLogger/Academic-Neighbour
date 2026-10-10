from sqlmodel import Session, desc, select

from models.models import Conversation, ConversationParticipant, Message, User


def create_conversation(session: Session, conversation: Conversation) -> Conversation:
    """Create a new conversation."""
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def add_participant(
    session: Session, conversation_id: int, user_id: int
) -> ConversationParticipant:
    """Add a user to a conversation."""
    participant = ConversationParticipant(conversation_id=conversation_id, user_id=user_id)
    session.add(participant)
    session.commit()
    session.refresh(participant)
    return participant


def get_user_conversations(session: Session, user_id: int) -> list[Conversation]:
    """Get all conversations a user is part of."""
    statement = (
        select(Conversation)
        .join(ConversationParticipant, Conversation.id == ConversationParticipant.conversation_id)
        .where(ConversationParticipant.user_id == user_id)
        .order_by(desc(Conversation.created_at))
    )
    return list(session.exec(statement).all())


def get_conversation_by_id(session: Session, conversation_id: int) -> Conversation | None:
    """Get a conversation by ID."""
    return session.get(Conversation, conversation_id)


def is_participant(session: Session, conversation_id: int, user_id: int) -> bool:
    """Check if a user is a participant in a conversation."""
    participant = session.exec(
        select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == user_id,
        )
    ).first()
    return participant is not None


def get_conversation_messages(session: Session, conversation_id: int) -> list[tuple[Message, User]]:
    """Get all messages in a conversation with sender information."""
    statement = (
        select(Message, User)
        .join(User, Message.sender_id == User.id)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    return list(session.exec(statement).all())


def create_message(session: Session, message: Message) -> Message:
    """Create a new message in a conversation."""
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


def get_conversation_participants(session: Session, conversation_id: int) -> list[User]:
    """Get all participants in a conversation."""
    statement = (
        select(User)
        .join(ConversationParticipant, User.id == ConversationParticipant.user_id)
        .where(ConversationParticipant.conversation_id == conversation_id)
    )
    return list(session.exec(statement).all())
