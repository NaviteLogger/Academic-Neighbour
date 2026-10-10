from typing import Any

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from models.models import User, UserRole
from services.security import get_password_hash


class TestAuthToken:
    """Tests for authentication token endpoint."""

    def test_login_success(self, client: TestClient, session: Session):
        """Test successful login with valid credentials."""
        user = User(
            email="logintest@example.com",
            username="logintest",
            first_name="Login",
            last_name="Test",
            hashed_password=get_password_hash("SecurePass123!"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        response = client.post(
            "/auth/token",
            data={"username": "logintest", "password": "SecurePass123!"},
        )

        assert response.status_code == status.HTTP_200_OK
        data: dict[str, Any] = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == "logintest"
        assert data["user"]["email"] == "logintest@example.com"
        assert "hashed_password" not in data["user"]

    def test_login_wrong_password(self, client: TestClient, session: Session):
        """Test login with incorrect password."""
        user = User(
            email="wrongpass@example.com",
            username="wrongpass",
            first_name="Wrong",
            last_name="Pass",
            hashed_password=get_password_hash("CorrectPass123!"),
            is_active=True,
        )
        session.add(user)
        session.commit()

        response = client.post(
            "/auth/token",
            data={"username": "wrongpass", "password": "WrongPassword123!"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data: dict[str, Any] = response.json()
        assert data["detail"] == "Incorrect username or password"
        assert "WWW-Authenticate" in response.headers
        assert response.headers["WWW-Authenticate"] == "Bearer"

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with username that doesn't exist."""
        response = client.post(
            "/auth/token",
            data={"username": "nonexistent", "password": "SomePass123!"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data: dict[str, Any] = response.json()
        assert data["detail"] == "Incorrect username or password"

    def test_login_inactive_user(self, client: TestClient, session: Session):
        """Test that inactive users cannot login."""
        user = User(
            email="inactive@example.com",
            username="inactive",
            first_name="Inactive",
            last_name="User",
            hashed_password=get_password_hash("SecurePass123!"),
            is_active=False,
        )
        session.add(user)
        session.commit()

        response = client.post(
            "/auth/token",
            data={"username": "inactive", "password": "SecurePass123!"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_username(self, client: TestClient):
        """Test login without providing username."""
        response = client.post(
            "/auth/token",
            data={"password": "SomePass123!"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_login_missing_password(self, client: TestClient):
        """Test login without providing password."""
        response = client.post(
            "/auth/token",
            data={"username": "someuser"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_login_empty_credentials(self, client: TestClient):
        """Test login with empty username and password."""
        response = client.post(
            "/auth/token",
            data={"username": "", "password": ""},
        )

        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        ]

    def test_login_token_contains_username(self, client: TestClient, session: Session):
        """Test that the returned token is valid and contains user info."""
        user = User(
            email="tokentest@example.com",
            username="tokentest",
            first_name="Token",
            last_name="Test",
            hashed_password=get_password_hash("SecurePass123!"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        response = client.post(
            "/auth/token",
            data={"username": "tokentest", "password": "SecurePass123!"},
        )

        assert response.status_code == status.HTTP_200_OK
        data: dict[str, Any] = response.json()
        token = data["access_token"]

        me_response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert me_response.status_code == status.HTTP_200_OK
        me_data: dict[str, Any] = me_response.json()
        assert me_data["username"] == "tokentest"
        assert me_data["email"] == "tokentest@example.com"

    def test_login_case_sensitive_username(self, client: TestClient, session: Session):
        """Test that usernames are case-sensitive."""
        user = User(
            email="casetest@example.com",
            username="casetest",
            first_name="Case",
            last_name="Test",
            hashed_password=get_password_hash("SecurePass123!"),
            is_active=True,
        )
        session.add(user)
        session.commit()

        response = client.post(
            "/auth/token",
            data={"username": "CASETEST", "password": "SecurePass123!"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_special_characters_in_password(self, client: TestClient, session: Session):
        """Test login with special characters in password."""
        special_password = "P@ssw0rd!#$%^&*()"
        user = User(
            email="special@example.com",
            username="specialchars",
            first_name="Special",
            last_name="Chars",
            hashed_password=get_password_hash(special_password),
            is_active=True,
        )
        session.add(user)
        session.commit()

        response = client.post(
            "/auth/token",
            data={"username": "specialchars", "password": special_password},
        )

        assert response.status_code == status.HTTP_200_OK
        data: dict[str, Any] = response.json()
        assert "access_token" in data

    def test_login_returns_user_role(self, client: TestClient, session: Session):
        """Test that login response includes user role."""
        user = User(
            email="roletest@example.com",
            username="roletest",
            first_name="Role",
            last_name="Test",
            hashed_password=get_password_hash("SecurePass123!"),
            is_active=True,
            role=UserRole.USER,
        )
        session.add(user)
        session.commit()

        response = client.post(
            "/auth/token",
            data={"username": "roletest", "password": "SecurePass123!"},
        )

        assert response.status_code == status.HTTP_200_OK
        data: dict[str, Any] = response.json()
        assert "user" in data
        assert "role" in data["user"]
        assert data["user"]["role"] == "user"
