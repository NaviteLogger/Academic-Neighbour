"""Tests for message router endpoints."""

from typing import Any

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from models.models import AuthenticatedUser, Conversation, ConversationParticipant


class TestConversationEndpoints:
    """Test suite for conversation endpoints."""

    def test_create_conversation(
        self, client: TestClient, logged_in_user: AuthenticatedUser, second_user: AuthenticatedUser
    ):
        """Test creating a new one-to-one conversation."""
        if not second_user.user.id:
            raise ValueError("Second user must have an ID")

        response = client.post(
            "/conversations/",
            json={"participant_id": second_user.user.id},
            headers=logged_in_user.headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "title" in data
        assert "id" in data

    def test_get_conversations(
        self,
        client: TestClient,
        session: Session,
        logged_in_user: AuthenticatedUser,
        second_user: AuthenticatedUser,
    ):
        """Test listing user's conversations."""
        if not logged_in_user.user.id or not second_user.user.id:
            raise ValueError("Users must have IDs")

        # Create a conversation
        conversation = Conversation(title="Test Chat")
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        if conversation.id:
            participant1 = ConversationParticipant(
                conversation_id=conversation.id, user_id=logged_in_user.user.id
            )
            participant2 = ConversationParticipant(
                conversation_id=conversation.id, user_id=second_user.user.id
            )
            session.add(participant1)
            session.add(participant2)
            session.commit()

        response = client.get("/conversations/", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_200_OK
        data: list[dict[str, Any]] = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(c["title"] == "Test Chat" for c in data)

    def test_get_conversation_details(
        self,
        client: TestClient,
        session: Session,
        logged_in_user: AuthenticatedUser,
        second_user: AuthenticatedUser,
    ):
        """Test getting conversation details."""
        if not logged_in_user.user.id or not second_user.user.id:
            raise ValueError("Users must have IDs")

        conversation = Conversation(title="Test Details")
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        if conversation.id:
            participant = ConversationParticipant(
                conversation_id=conversation.id, user_id=logged_in_user.user.id
            )
            session.add(participant)
            session.commit()

            response = client.get(
                f"/conversations/{conversation.id}", headers=logged_in_user.headers
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["title"] == "Test Details"

    def test_get_conversation_unauthorized(
        self, client: TestClient, session: Session, logged_in_user: AuthenticatedUser
    ):
        """Test accessing a conversation without being a participant."""
        # Create conversation without the user
        conversation = Conversation(title="Private Chat")
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        response = client.get(f"/conversations/{conversation.id}", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_participants(
        self,
        client: TestClient,
        session: Session,
        logged_in_user: AuthenticatedUser,
        second_user: AuthenticatedUser,
    ):
        """Test getting conversation participants."""
        if not logged_in_user.user.id or not second_user.user.id:
            raise ValueError("Users must have IDs")

        conversation = Conversation(title="Test Participants")
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        if conversation.id:
            participant1 = ConversationParticipant(
                conversation_id=conversation.id, user_id=logged_in_user.user.id
            )
            participant2 = ConversationParticipant(
                conversation_id=conversation.id, user_id=second_user.user.id
            )
            session.add(participant1)
            session.add(participant2)
            session.commit()

            response = client.get(
                f"/conversations/{conversation.id}/participants", headers=logged_in_user.headers
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 2
            user_ids = [u["id"] for u in data]
            assert logged_in_user.user.id in user_ids
            assert second_user.user.id in user_ids


class TestMessageEndpoints:
    """Test suite for message endpoints."""

    def test_send_message(
        self,
        client: TestClient,
        session: Session,
        logged_in_user: AuthenticatedUser,
        second_user: AuthenticatedUser,
    ):
        """Test sending a message to a conversation."""
        if not logged_in_user.user.id or not second_user.user.id:
            raise ValueError("Users must have IDs")

        # Create conversation
        conversation = Conversation(title="Test Messages")
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        if conversation.id:
            participant = ConversationParticipant(
                conversation_id=conversation.id, user_id=logged_in_user.user.id
            )
            session.add(participant)
            session.commit()

            response = client.post(
                f"/conversations/{conversation.id}/messages",
                json={"content": "Hello, World!"},
                headers=logged_in_user.headers,
            )
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["content"] == "Hello, World!"
            assert data["sender_id"] == logged_in_user.user.id
            assert data["sender_name"] == logged_in_user.user.username

    def test_get_messages(
        self,
        client: TestClient,
        session: Session,
        logged_in_user: AuthenticatedUser,
        second_user: AuthenticatedUser,
    ):
        """Test getting messages from a conversation."""
        if not logged_in_user.user.id or not second_user.user.id:
            raise ValueError("Users must have IDs")

        # Create conversation
        conversation = Conversation(title="Test Get Messages")
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        if conversation.id:
            participant = ConversationParticipant(
                conversation_id=conversation.id, user_id=logged_in_user.user.id
            )
            session.add(participant)
            session.commit()

            # Send a message first
            client.post(
                f"/conversations/{conversation.id}/messages",
                json={"content": "Test message"},
                headers=logged_in_user.headers,
            )

            # Get messages
            response = client.get(
                f"/conversations/{conversation.id}/messages", headers=logged_in_user.headers
            )
            assert response.status_code == status.HTTP_200_OK
            data: list[dict[str, Any]] = response.json()
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["content"] == "Test message"

    def test_send_message_unauthorized(
        self, client: TestClient, session: Session, logged_in_user: AuthenticatedUser
    ):
        """Test sending a message to a conversation without being a participant."""
        # Create conversation without the user
        conversation = Conversation(title="Private Chat")
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        if conversation.id:
            response = client.post(
                f"/conversations/{conversation.id}/messages",
                json={"content": "Should fail"},
                headers=logged_in_user.headers,
            )
            assert response.status_code == status.HTTP_403_FORBIDDEN
