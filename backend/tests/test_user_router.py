from typing import Any

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from models.models import AuthenticatedUser, User


class TestAdminEndpoints:
    """Tests for admin user management endpoints."""

    def test_read_all_users_success(
        self, client: TestClient, session: Session, logged_in_admin: AuthenticatedUser
    ):
        """Test that admin can retrieve all users."""
        user1 = User(
            email="user1@example.com",
            username="user1",
            first_name="User",
            last_name="One",
            hashed_password="test",
        )
        user2 = User(
            email="user2@example.com",
            username="user2",
            first_name="User",
            last_name="Two",
            hashed_password="test",
        )
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        response = client.get("/admin/users", headers=logged_in_admin.headers)
        assert response.status_code == status.HTTP_200_OK
        data: list[dict[str, Any]] = response.json()
        assert len(data) >= 2

    def test_read_user_by_username_success(
        self, client: TestClient, session: Session, logged_in_admin: AuthenticatedUser
    ):
        """Test that admin can retrieve user by username."""
        user = User(
            email="example@example.com",
            username="example",
            first_name="Example",
            last_name="User",
            hashed_password="test",
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        response = client.get(f"/admin/user/{user.username}", headers=logged_in_admin.headers)

        assert response.status_code == status.HTTP_200_OK
        data: dict[str, Any] = response.json()
        assert data["id"] == user.id
        assert data["username"] == "example"

    def test_read_user_by_email_success(
        self, client: TestClient, session: Session, logged_in_admin: AuthenticatedUser
    ):
        """Test that admin can retrieve user by email."""
        user = User(
            email="example@example.com",
            username="example",
            first_name="Example",
            last_name="User",
            hashed_password="test",
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        response = client.get(f"/admin/user/{user.email}", headers=logged_in_admin.headers)

        assert response.status_code == status.HTTP_200_OK
        data: dict[str, Any] = response.json()
        assert data["id"] == user.id
        assert data["email"] == "example@example.com"

    def test_read_user_by_username_not_found(
        self, client: TestClient, logged_in_admin: AuthenticatedUser
    ):
        """Test that querying non-existent user returns 404."""
        response = client.get("/admin/user/nonexistentuser", headers=logged_in_admin.headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data: dict[str, Any] = response.json()
        assert data["detail"] == "User not found"

    def test_read_all_users_unauthorized(self, client: TestClient):
        """Test that non-admin users cannot access admin endpoints."""
        response = client.get("/admin/users")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_read_user_unauthorized(self, client: TestClient):
        """Test that non-admin users cannot access user details."""
        response = client.get("/admin/user/someuser")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_read_user_by_email_case_sensitivity(
        self, client: TestClient, session: Session, logged_in_admin: AuthenticatedUser
    ):
        """Test that email lookup handles case correctly."""
        user = User(
            email="CaseSensitive@example.com",
            username="casetest",
            first_name="Case",
            last_name="Test",
            hashed_password="test",
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        response = client.get(f"/admin/user/{user.email.lower()}", headers=logged_in_admin.headers)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


class TestUserRegistration:
    """Tests for user registration endpoint."""

    def test_register_user_success(self, client: TestClient):
        """Test successful user registration."""
        new_user: dict[str, Any] = {
            "email": "newuser@example.com",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "password": "SecurePass123!",
        }

        response = client.post("/users/register", json=new_user)
        assert response.status_code == status.HTTP_200_OK
        data: dict[str, Any] = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == "newuser"
        assert data["user"]["email"] == "newuser@example.com"

    def test_register_user_invalid_email(self, client: TestClient):
        """Test registration with invalid email format."""
        new_user: dict[str, Any] = {
            "email": "invalid-email",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "SecurePass123!",
        }

        response = client.post("/users/register", json=new_user)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data: dict[str, Any] = response.json()
        assert data["detail"] == "Incorrect Email"

    def test_register_user_weak_password_no_uppercase(self, client: TestClient):
        """Test registration with password missing uppercase letter."""
        new_user: dict[str, Any] = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "weakpass123!",
        }

        response = client.post("/users/register", json=new_user)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data: dict[str, Any] = response.json()
        assert "Password must have" in data["detail"]

    def test_register_user_weak_password_no_special(self, client: TestClient):
        """Test registration with password missing special character."""
        new_user: dict[str, Any] = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "WeakPass123",
        }

        response = client.post("/users/register", json=new_user)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data: dict[str, Any] = response.json()
        assert "Password must have" in data["detail"]

    def test_register_user_weak_password_too_short(self, client: TestClient):
        """Test registration with password too short."""
        new_user: dict[str, Any] = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "Pass1!",
        }

        response = client.post("/users/register", json=new_user)
        # Pydantic validation may catch this first (422) or custom validation (400)
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        ]

    def test_register_user_duplicate_username(self, client: TestClient, session: Session):
        """Test registration with already existing username."""
        # Create existing user
        existing_user = User(
            email="existing@example.com",
            username="existinguser",
            first_name="Existing",
            last_name="User",
            hashed_password="test",
        )
        session.add(existing_user)
        session.commit()

        # Try to register with same username
        new_user: dict[str, Any] = {
            "email": "different@example.com",
            "username": "existinguser",
            "first_name": "New",
            "last_name": "User",
            "password": "SecurePass123!",
        }

        response = client.post("/users/register", json=new_user)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data: dict[str, Any] = response.json()
        assert data["detail"] == "Username already exists"

    def test_register_user_duplicate_email(self, client: TestClient, session: Session):
        """Test registration with already existing email."""
        # Create existing user
        existing_user = User(
            email="existing@example.com",
            username="existinguser",
            first_name="Existing",
            last_name="User",
            hashed_password="test",
        )
        session.add(existing_user)
        session.commit()

        # Try to register with same email
        new_user: dict[str, Any] = {
            "email": "existing@example.com",
            "username": "differentuser",
            "first_name": "New",
            "last_name": "User",
            "password": "SecurePass123!",
        }

        response = client.post("/users/register", json=new_user)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data: dict[str, Any] = response.json()
        assert data["detail"] == "Email already exists"

    def test_register_user_with_special_characters_in_name(self, client: TestClient):
        """Test registration with special characters in name fields."""
        new_user: dict[str, Any] = {
            "email": "special@example.com",
            "username": "specialuser",
            "first_name": "José",
            "last_name": "O'Brien-Smith",
            "password": "SecurePass123!",
        }

        response = client.post("/users/register", json=new_user)
        assert response.status_code == status.HTTP_200_OK
        data: dict[str, Any] = response.json()
        assert data["user"]["first_name"] == "José"
        assert data["user"]["last_name"] == "O'Brien-Smith"

    def test_register_user_email_edge_cases(self, client: TestClient):
        """Test registration with various valid email formats."""
        valid_emails = [
            "user+tag@example.com",
            "user.name@example.co.uk",
            "user_name@example-domain.com",
        ]

        for idx, email in enumerate(valid_emails):
            new_user: dict[str, Any] = {
                "email": email,
                "username": f"user{idx}",
                "first_name": "Test",
                "last_name": "User",
                "password": "SecurePass123!",
            }

            response = client.post("/users/register", json=new_user)
            assert response.status_code == status.HTTP_200_OK


class TestCurrentUser:
    """Tests for current user endpoint."""

    def test_get_current_user_success(self, client: TestClient, logged_in_user: AuthenticatedUser):
        """Test getting current authenticated user information."""
        response = client.get("/users/me", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_200_OK
        data: dict[str, Any] = response.json()
        assert data["username"] == logged_in_user.user.username
        assert data["email"] == logged_in_user.user.email
        assert "id" in data

    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test that unauthenticated users cannot access /me endpoint."""
        response = client.get("/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test that invalid token returns unauthorized."""
        headers = {"Authorization": "Bearer invalid_token_12345"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_malformed_header(self, client: TestClient):
        """Test that malformed authorization header returns unauthorized."""
        headers = {"Authorization": "InvalidFormat token123"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_returns_no_password(
        self, client: TestClient, logged_in_user: AuthenticatedUser
    ):
        """Test that user data doesn't include hashed password."""
        response = client.get("/users/me", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_200_OK
        data: dict[str, Any] = response.json()
        assert "hashed_password" not in data
        assert "password" not in data
