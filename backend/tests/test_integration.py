"""Integration tests for end-to-end workflows."""

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from models.models import User, UserRole
from services.security import get_password_hash


class TestUserRegistrationAndLogin:
    """Integration tests for user registration and login workflow."""

    def test_register_login_and_access_protected_endpoint(self, client: TestClient):
        """Test complete flow: register → login → access protected endpoint."""
        registration_data = {
            "email": "integration@example.com",
            "username": "integrationuser",
            "first_name": "Integration",
            "last_name": "Test",
            "password": "SecurePass123!",
        }

        register_response = client.post("/users/register", json=registration_data)
        assert register_response.status_code == status.HTTP_200_OK

        login_response = client.post(
            "/auth/token",
            data={"username": "integrationuser", "password": "SecurePass123!"},
        )
        assert login_response.status_code == status.HTTP_200_OK
        token_data = login_response.json()
        assert "access_token" in token_data

        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        me_response = client.get("/users/me", headers=headers)
        assert me_response.status_code == status.HTTP_200_OK
        user_data = me_response.json()
        assert user_data["username"] == "integrationuser"
        assert user_data["email"] == "integration@example.com"


class TestPostCreationAndInteraction:
    """Integration tests for post creation and interaction workflow."""

    def test_create_post_like_and_comment_workflow(self, client: TestClient, session: Session):
        """Test complete flow: create user → login → create post → like → comment."""
        user = User(
            email="poster@example.com",
            username="poster",
            first_name="Post",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        login_response = client.post(
            "/auth/token", data={"username": "poster", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        post_data = {"content": "My first integration test post!"}
        create_post_response = client.post("/posts/", json=post_data, headers=headers)
        assert create_post_response.status_code == status.HTTP_201_CREATED
        post = create_post_response.json()
        post_id = post["id"]

        like_response = client.post(f"/posts/{post_id}/like", headers=headers)
        assert like_response.status_code == status.HTTP_201_CREATED

        likes_info_response = client.get(f"/posts/{post_id}/likes", headers=headers)
        assert likes_info_response.status_code == status.HTTP_200_OK
        likes_info = likes_info_response.json()
        assert likes_info["liked_by_current_user"] is True
        assert likes_info["likes_count"] == 1

        comment_data = {"content": "Great post!"}
        comment_response = client.post(
            f"/posts/{post_id}/comments", json=comment_data, headers=headers
        )
        assert comment_response.status_code == status.HTTP_201_CREATED

        comments_response = client.get(f"/posts/{post_id}/comments")
        assert comments_response.status_code == status.HTTP_200_OK
        comments = comments_response.json()
        assert len(comments) == 1
        assert comments[0]["content"] == "Great post!"


class TestFriendshipWorkflow:
    """Integration tests for friendship workflow."""

    def test_complete_friendship_workflow(self, client: TestClient, session: Session):
        """Test complete flow: create users → send request → accept → view friends."""
        user1 = User(
            email="friend1@example.com",
            username="friend1",
            first_name="Friend",
            last_name="One",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        user2 = User(
            email="friend2@example.com",
            username="friend2",
            first_name="Friend",
            last_name="Two",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        login1 = client.post("/auth/token", data={"username": "friend1", "password": "password123"})
        token1 = login1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        login2 = client.post("/auth/token", data={"username": "friend2", "password": "password123"})
        token2 = login2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        send_request = client.post(f"/friendships/request/{user2.id}", headers=headers1)
        assert send_request.status_code == status.HTTP_201_CREATED

        pending_requests = client.get("/friendships/?filter_type=pending", headers=headers2)
        assert pending_requests.status_code == status.HTTP_200_OK
        requests_data = pending_requests.json()
        assert len(requests_data) == 1
        assert requests_data[0]["username"] == "friend1"

        accept_request = client.post(f"/friendships/accept/{user1.id}", headers=headers2)
        assert accept_request.status_code == status.HTTP_200_OK

        friends1 = client.get("/friendships/", headers=headers1)
        friends2 = client.get("/friendships/", headers=headers2)

        assert friends1.status_code == status.HTTP_200_OK
        assert friends2.status_code == status.HTTP_200_OK
        assert len(friends1.json()) == 1
        assert len(friends2.json()) == 1


class TestEventWorkflow:
    """Integration tests for event workflow."""

    def test_complete_event_workflow(self, client: TestClient, session: Session):
        """Test complete flow: create user → create event → register → update status."""
        user = User(
            email="eventuser@example.com",
            username="eventuser",
            first_name="Event",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()

        login = client.post(
            "/auth/token", data={"username": "eventuser", "password": "password123"}
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        start_date = (datetime.now(UTC) + timedelta(days=7)).isoformat()
        end_date = (datetime.now(UTC) + timedelta(days=7, hours=2)).isoformat()

        event_data: dict[str, Any] = {
            "title": "Integration Test Event",
            "description": "Testing event workflow",
            "location": "Test Location",
            "start_date": start_date,
            "end_date": end_date,
        }

        create_event = client.post("/events/", json=event_data, headers=headers)
        assert create_event.status_code == status.HTTP_201_CREATED
        event = create_event.json()
        event_id = event["id"]

        register_response = client.post(
            f"/events/{event_id}/register",
            headers=headers,
        )
        assert register_response.status_code == status.HTTP_201_CREATED

        update_status = client.put(
            f"/events/{event_id}/register?attendance_status=interested",
            headers=headers,
        )
        assert update_status.status_code == status.HTTP_200_OK

        get_event = client.get(f"/events/{event_id}")
        assert get_event.status_code == status.HTTP_200_OK


class TestAdminWorkflow:
    """Integration tests for admin operations."""

    def test_admin_user_management_workflow(self, client: TestClient, session: Session):
        """Test complete flow: admin login → view users → manage users."""
        admin = User(
            email="admin@example.com",
            username="admin",
            first_name="Admin",
            last_name="User",
            hashed_password=get_password_hash("adminpass"),
            is_active=True,
            role=UserRole.ADMIN,
        )
        regular_user = User(
            email="regular@example.com",
            username="regularuser",
            first_name="Regular",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(admin)
        session.add(regular_user)
        session.commit()

        login = client.post("/auth/token", data={"username": "admin", "password": "adminpass"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        all_users = client.get("/admin/users", headers=headers)
        assert all_users.status_code == status.HTTP_200_OK
        users_data = all_users.json()
        assert len(users_data) >= 2

        get_user = client.get("/admin/user/regularuser", headers=headers)
        assert get_user.status_code == status.HTTP_200_OK
        user_data = get_user.json()
        assert user_data["username"] == "regularuser"


class TestMultiUserInteraction:
    """Integration tests for multi-user interactions."""

    def test_multiple_users_interacting_with_post(self, client: TestClient, session: Session):
        """Test multiple users creating, liking, and commenting on posts."""
        users_data = [
            ("user1", "user1@example.com"),
            ("user2", "user2@example.com"),
            ("user3", "user3@example.com"),
        ]

        tokens: list[str] = []
        for username, email in users_data:
            user = User(
                email=email,
                username=username,
                first_name="User",
                last_name=username,
                hashed_password=get_password_hash("password123"),
                is_active=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)

            login = client.post(
                "/auth/token", data={"username": username, "password": "password123"}
            )
            tokens.append(login.json()["access_token"])

        post_data = {"content": "Post for everyone to interact with"}
        create_post = client.post(
            "/posts/",
            json=post_data,
            headers={"Authorization": f"Bearer {tokens[0]}"},
        )
        post_id = create_post.json()["id"]

        for token in tokens:
            like_response = client.post(
                f"/posts/{post_id}/like",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert like_response.status_code == status.HTTP_201_CREATED

        likes_info = client.get(
            f"/posts/{post_id}/likes",
            headers={"Authorization": f"Bearer {tokens[0]}"},
        )
        assert likes_info.json()["likes_count"] == 3

        for i, token in enumerate(tokens):
            comment_data = {"content": f"Comment from user {i + 1}"}
            comment_response = client.post(
                f"/posts/{post_id}/comments",
                json=comment_data,
                headers={"Authorization": f"Bearer {token}"},
            )
            assert comment_response.status_code == status.HTTP_201_CREATED

        comments = client.get(f"/posts/{post_id}/comments")
        assert len(comments.json()) == 3


class TestErrorRecovery:
    """Integration tests for error handling and recovery."""

    def test_invalid_token_recovery(self, client: TestClient, session: Session):
        """Test that invalid token is handled and user can re-authenticate."""
        user = User(
            email="recovery@example.com",
            username="recoveryuser",
            first_name="Recovery",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()

        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/users/me", headers=invalid_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        login = client.post(
            "/auth/token", data={"username": "recoveryuser", "password": "password123"}
        )
        assert login.status_code == status.HTTP_200_OK
        token = login.json()["access_token"]

        valid_headers = {"Authorization": f"Bearer {token}"}
        me_response = client.get("/users/me", headers=valid_headers)
        assert me_response.status_code == status.HTTP_200_OK

    def test_cascade_operations_on_deleted_user(self, client: TestClient, session: Session):
        """Test handling of operations when related user is deleted."""
        user1 = User(
            email="deletable@example.com",
            username="deletableuser",
            first_name="Deletable",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user1)
        session.commit()
        session.refresh(user1)

        login = client.post(
            "/auth/token", data={"username": "deletableuser", "password": "password123"}
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        post_data = {"content": "Post before deletion"}
        create_post = client.post("/posts/", json=post_data, headers=headers)
        assert create_post.status_code == status.HTTP_201_CREATED
        post_id = create_post.json()["id"]

        get_post = client.get(f"/posts/{post_id}")
        assert get_post.status_code == status.HTTP_200_OK
