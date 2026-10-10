"""Unit tests for security service functions."""

from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException
from jose import jwt
from sqlmodel import Session

from models.models import User, UserRole
from services.security import (
    ALGORITHM,
    SECRET_KEY,
    authenticate_user,
    create_access_token,
    get_current_admin_user,
    get_password_hash,
    verify_password,
)


class TestPasswordHashing:
    """Tests for password hashing and verification."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "mySecurePassword123!"
        hashed = get_password_hash(password)

        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0

    def test_hash_password_different_each_time(self):
        """Test that hashing same password produces different hashes (due to salt)."""
        password = "samePassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "correctPassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "correctPassword123"
        wrong_password = "wrongPassword456"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty(self):
        """Test password verification with empty password."""
        password = "myPassword123"
        hashed = get_password_hash(password)

        assert verify_password("", hashed) is False

    def test_hash_special_characters(self):
        """Test hashing password with special characters."""
        password = "P@ssw0rd!#$%^&*()"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_hash_unicode_characters(self):
        """Test hashing password with unicode characters."""
        password = "пароль密码🔐"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True


class TestAuthenticateUser:
    """Tests for user authentication."""

    def test_authenticate_user_by_username_success(self, session: Session):
        """Test successful authentication by username."""
        user = User(
            email="auth@example.com",
            username="authuser",
            first_name="Auth",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()

        authenticated = authenticate_user(session, "authuser", "password123")

        assert authenticated is not None
        assert authenticated.username == "authuser"
        assert authenticated.email == "auth@example.com"

    def test_authenticate_user_by_email_success(self, session: Session):
        """Test successful authentication by email."""
        user = User(
            email="emailauth@example.com",
            username="emailauthuser",
            first_name="Email",
            last_name="Auth",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()

        authenticated = authenticate_user(session, "emailauth@example.com", "password123")

        assert authenticated is not None
        assert authenticated.username == "emailauthuser"

    def test_authenticate_user_wrong_password(self, session: Session):
        """Test authentication with wrong password."""
        user = User(
            email="wrongpass@example.com",
            username="wrongpassuser",
            first_name="Wrong",
            last_name="Pass",
            hashed_password=get_password_hash("correctpassword"),
            is_active=True,
        )
        session.add(user)
        session.commit()

        authenticated = authenticate_user(session, "wrongpassuser", "wrongpassword")

        assert authenticated is None

    def test_authenticate_user_nonexistent(self, session: Session):
        """Test authentication with nonexistent user."""
        authenticated = authenticate_user(session, "nonexistent", "password123")

        assert authenticated is None

    def test_authenticate_inactive_user(self, session: Session):
        """Test authentication with inactive user."""
        user = User(
            email="inactive@example.com",
            username="inactiveuser",
            first_name="Inactive",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=False,
        )
        session.add(user)
        session.commit()

        authenticated = authenticate_user(session, "inactiveuser", "password123")

        assert authenticated is None

    def test_authenticate_case_sensitive_username(self, session: Session):
        """Test that username authentication is case-sensitive."""
        user = User(
            email="case@example.com",
            username="CaseSensitive",
            first_name="Case",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()

        authenticated_exact = authenticate_user(session, "CaseSensitive", "password123")
        authenticated_lower = authenticate_user(session, "casesensitive", "password123")

        assert authenticated_exact is not None
        assert authenticated_lower is None


class TestCreateAccessToken:
    """Tests for JWT token creation."""

    def test_create_access_token_basic(self):
        """Test creating a basic access token."""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        assert token is not None
        assert len(token) > 0

        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "testuser"
        assert "exp" in decoded

    def test_create_access_token_with_expiration(self):
        """Test creating token with custom expiration."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)

        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = datetime.fromtimestamp(decoded["exp"], tz=UTC)
        now = datetime.now(UTC)

        time_diff = (exp - now).total_seconds()
        assert 1790 < time_diff < 1810

    def test_create_access_token_with_additional_data(self):
        """Test creating token with additional claims."""
        data = {"sub": "testuser", "role": "admin", "email": "test@example.com"}
        token = create_access_token(data)

        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "testuser"
        assert decoded["role"] == "admin"
        assert decoded["email"] == "test@example.com"

    def test_create_access_token_default_expiration(self):
        """Test that default expiration is 15 minutes."""
        data = {"sub": "testuser"}
        token = create_access_token(data, expires_delta=None)

        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = datetime.fromtimestamp(decoded["exp"], tz=UTC)
        now = datetime.now(UTC)

        time_diff = (exp - now).total_seconds()
        assert 890 < time_diff < 910


class TestGetCurrentAdminUser:
    """Tests for getting current admin user."""

    def test_get_current_admin_user_success(self):
        """Test getting admin user when user is admin."""
        admin_user = User(
            email="admin@example.com",
            username="adminuser",
            first_name="Admin",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            role=UserRole.ADMIN,
        )

        admin = get_current_admin_user(admin_user)

        assert admin is not None
        assert admin.username == "adminuser"
        assert admin.role == UserRole.ADMIN

    def test_get_current_admin_user_not_admin(self):
        """Test getting admin user when user is not admin."""
        regular_user = User(
            email="regular@example.com",
            username="regularuser",
            first_name="Regular",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            role=UserRole.USER,
        )

        with pytest.raises(HTTPException) as exc_info:
            get_current_admin_user(regular_user)

        assert exc_info.value.status_code == 403
        assert "do not have permission" in exc_info.value.detail

    def test_get_current_admin_user_no_role(self):
        """Test getting admin user when user has no role set."""
        user_no_role = User(
            email="norole@example.com",
            username="noroleuser",
            first_name="NoRole",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )

        with pytest.raises(HTTPException) as exc_info:
            get_current_admin_user(user_no_role)

        assert exc_info.value.status_code == 403
