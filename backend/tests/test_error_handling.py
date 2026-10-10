"""Tests for error handling and edge cases."""

from datetime import UTC, datetime, timedelta

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from models.models import Post, User
from services.security import get_password_hash


class TestAuthenticationErrors:
    """Tests for authentication error handling."""

    def test_missing_authorization_header(self, client: TestClient):
        """Test accessing protected endpoint without authorization header."""
        response = client.get("/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_malformed_authorization_header(self, client: TestClient):
        """Test with malformed authorization header."""
        headers = {"Authorization": "InvalidFormat token123"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_missing_bearer_prefix(self, client: TestClient):
        """Test authorization header without Bearer prefix."""
        headers = {"Authorization": "token123"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_empty_token(self, client: TestClient):
        """Test with empty token."""
        headers = {"Authorization": "Bearer "}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestInputValidationErrors:
    """Tests for input validation error handling."""

    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email format."""
        user_data = {
            "email": "invalid-email",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "ValidPass123!",
        }
        response = client.post("/users/register", json=user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_required_fields(self, client: TestClient):
        """Test registration with missing required fields."""
        user_data = {"email": "test@example.com"}
        response = client.post("/users/register", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_post_empty_content(self, client: TestClient, session: Session):
        """Test creating post with empty content."""
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

        login = client.post("/auth/token", data={"username": "poster", "password": "password123"})
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        response = client.post("/posts/", json={"content": ""}, headers=headers)
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        ]

    def test_create_event_invalid_dates(self, client: TestClient, session: Session):
        """Test creating event with end date before start date."""
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
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        start_date = (datetime.now(UTC) + timedelta(days=7)).isoformat()
        end_date = (datetime.now(UTC) + timedelta(days=5)).isoformat()

        event_data = {
            "title": "Invalid Event",
            "description": "End before start",
            "location": "Test",
            "start_date": start_date,
            "end_date": end_date,
        }

        response = client.post("/events/", json=event_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestResourceNotFoundErrors:
    """Tests for resource not found error handling."""

    def test_get_nonexistent_post(self, client: TestClient):
        """Test getting post that doesn't exist."""
        response = client.get("/posts/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_nonexistent_event(self, client: TestClient):
        """Test getting event that doesn't exist."""
        response = client.get("/events/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_like_nonexistent_post(self, client: TestClient, session: Session):
        """Test liking post that doesn't exist."""
        user = User(
            email="liker@example.com",
            username="liker",
            first_name="Liker",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()

        login = client.post("/auth/token", data={"username": "liker", "password": "password123"})
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        response = client.post("/posts/99999/like", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_comment_on_nonexistent_post(self, client: TestClient, session: Session):
        """Test commenting on post that doesn't exist."""
        user = User(
            email="commenter@example.com",
            username="commenter",
            first_name="Commenter",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()

        login = client.post(
            "/auth/token", data={"username": "commenter", "password": "password123"}
        )
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        response = client.post(
            "/posts/99999/comments",
            json={"content": "Comment on nothing"},
            headers=headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPermissionErrors:
    """Tests for permission and authorization errors."""

    def test_update_other_users_comment(self, client: TestClient, session: Session):
        """Test updating another user's comment."""
        user1 = User(
            email="user1@example.com",
            username="user1",
            first_name="User",
            last_name="One",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        user2 = User(
            email="user2@example.com",
            username="user2",
            first_name="User",
            last_name="Two",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)

        if not user1.id:
            raise ValueError("User1 must have ID")

        post = Post(content="Test post", author_id=user1.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        login1 = client.post("/auth/token", data={"username": "user1", "password": "password123"})
        headers1 = {"Authorization": f"Bearer {login1.json()['access_token']}"}

        comment_response = client.post(
            f"/posts/{post.id}/comments",
            json={"content": "Original comment"},
            headers=headers1,
        )
        comment_id = comment_response.json()["id"]

        login2 = client.post("/auth/token", data={"username": "user2", "password": "password123"})
        headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}

        update_response = client.put(
            f"/posts/comments/{comment_id}",
            json={"content": "Trying to update"},
            headers=headers2,
        )
        assert update_response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_other_users_event(self, client: TestClient, session: Session):
        """Test deleting another user's event."""
        user1 = User(
            email="creator@example.com",
            username="creator",
            first_name="Creator",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        user2 = User(
            email="deleter@example.com",
            username="deleter",
            first_name="Deleter",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.commit()

        login1 = client.post("/auth/token", data={"username": "creator", "password": "password123"})
        headers1 = {"Authorization": f"Bearer {login1.json()['access_token']}"}

        start_date = (datetime.now(UTC) + timedelta(days=7)).isoformat()
        end_date = (datetime.now(UTC) + timedelta(days=7, hours=2)).isoformat()

        event_data = {
            "title": "Event to protect",
            "description": "Should not be deletable by others",
            "location": "Test",
            "start_date": start_date,
            "end_date": end_date,
        }

        create_response = client.post("/events/", json=event_data, headers=headers1)
        event_id = create_response.json()["id"]

        login2 = client.post("/auth/token", data={"username": "deleter", "password": "password123"})
        headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}

        delete_response = client.delete(f"/events/{event_id}", headers=headers2)
        assert delete_response.status_code == status.HTTP_403_FORBIDDEN

    def test_non_admin_access_admin_endpoint(self, client: TestClient, session: Session):
        """Test regular user accessing admin endpoint."""
        user = User(
            email="regular@example.com",
            username="regularuser",
            first_name="Regular",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()

        login = client.post(
            "/auth/token", data={"username": "regularuser", "password": "password123"}
        )
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        response = client.get("/admin/users", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDuplicateResourceErrors:
    """Tests for duplicate resource error handling."""

    def test_duplicate_username_registration(self, client: TestClient, session: Session):
        """Test registering with existing username."""
        user = User(
            email="existing@example.com",
            username="existinguser",
            first_name="Existing",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()

        new_user_data = {
            "email": "new@example.com",
            "username": "existinguser",
            "first_name": "New",
            "last_name": "User",
            "password": "ValidPass123!",
        }

        response = client.post("/users/register", json=new_user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicate_email_registration(self, client: TestClient, session: Session):
        """Test registering with existing email."""
        user = User(
            email="existing@example.com",
            username="existinguser",
            first_name="Existing",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()

        new_user_data = {
            "email": "existing@example.com",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "password": "ValidPass123!",
        }

        response = client.post("/users/register", json=new_user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicate_friend_request(self, client: TestClient, session: Session):
        """Test sending duplicate friend request."""
        user1 = User(
            email="requester@example.com",
            username="requester",
            first_name="Requester",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        user2 = User(
            email="addressee@example.com",
            username="addressee",
            first_name="Addressee",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        login = client.post(
            "/auth/token", data={"username": "requester", "password": "password123"}
        )
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        first_request = client.post(
            f"/friendships/request/{user2.id}",
            headers=headers,
        )
        assert first_request.status_code == status.HTTP_201_CREATED

        second_request = client.post(
            f"/friendships/request/{user2.id}",
            headers=headers,
        )
        assert second_request.status_code == status.HTTP_409_CONFLICT


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_self_friend_request(self, client: TestClient, session: Session):
        """Test sending friend request to oneself."""
        user = User(
            email="self@example.com",
            username="selfuser",
            first_name="Self",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        login = client.post("/auth/token", data={"username": "selfuser", "password": "password123"})
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        response = client.post(
            f"/friendships/request/{user.id}",
            headers=headers,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_like_same_post_multiple_times(self, client: TestClient, session: Session):
        """Test liking the same post multiple times (should be idempotent)."""
        user = User(
            email="multiliker@example.com",
            username="multiliker",
            first_name="Multi",
            last_name="Liker",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have ID")

        post = Post(content="Post to like multiple times", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        login = client.post(
            "/auth/token", data={"username": "multiliker", "password": "password123"}
        )
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        first_like = client.post(f"/posts/{post.id}/like", headers=headers)
        assert first_like.status_code == status.HTTP_201_CREATED

        for _ in range(2):
            response = client.post(f"/posts/{post.id}/like", headers=headers)
            assert response.status_code == status.HTTP_201_CREATED

        likes_info = client.get(f"/posts/{post.id}/likes", headers=headers)
        assert likes_info.json()["likes_count"] == 1

    def test_register_event_twice(self, client: TestClient, session: Session):
        """Test registering for the same event twice (should update status)."""
        user = User(
            email="doubleregister@example.com",
            username="doubleregister",
            first_name="Double",
            last_name="Register",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()

        login = client.post(
            "/auth/token", data={"username": "doubleregister", "password": "password123"}
        )
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        start_date = (datetime.now(UTC) + timedelta(days=7)).isoformat()
        end_date = (datetime.now(UTC) + timedelta(days=7, hours=2)).isoformat()

        event_data = {
            "title": "Double Registration Event",
            "description": "Test event",
            "location": "Test",
            "start_date": start_date,
            "end_date": end_date,
        }

        create_event = client.post("/events/", json=event_data, headers=headers)
        event_id = create_event.json()["id"]

        first_register = client.post(
            f"/events/{event_id}/register",
            json={"status": "attending"},
            headers=headers,
        )
        assert first_register.status_code == status.HTTP_201_CREATED

        second_register = client.post(
            f"/events/{event_id}/register",
            json={"status": "interested"},
            headers=headers,
        )
        assert second_register.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
        ]
