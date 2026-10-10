from sqlmodel import Session

from models.models import User
from repositories.user_repo import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
)
from services.security import get_password_hash


class TestUserRepository:
    """Tests for user repository functions."""

    def test_create_user(self, session: Session):
        """Test creating a new user."""
        user = User(
            email="newuser@example.com",
            username="newuser",
            first_name="New",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )

        created_user = create_user(session, user)

        assert created_user is not None
        assert created_user.id is not None
        assert created_user.email == "newuser@example.com"
        assert created_user.username == "newuser"
        assert created_user.first_name == "New"
        assert created_user.last_name == "User"
        assert created_user.is_active is True

    def test_get_user_by_email_exists(self, session: Session):
        """Test getting a user by email when user exists."""
        user = User(
            email="findme@example.com",
            username="findme",
            first_name="Find",
            last_name="Me",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()

        found_user = get_user_by_email(session, "findme@example.com")

        assert found_user is not None
        assert found_user.email == "findme@example.com"
        assert found_user.username == "findme"

    def test_get_user_by_email_not_exists(self, session: Session):
        """Test getting a user by email when user doesn't exist."""
        found_user = get_user_by_email(session, "nonexistent@example.com")

        assert found_user is None

    def test_get_user_by_email_case_sensitive(self, session: Session):
        """Test that email lookup is case-sensitive."""
        user = User(
            email="CaseSensitive@example.com",
            username="caseuser",
            first_name="Case",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()

        found_exact = get_user_by_email(session, "CaseSensitive@example.com")
        found_lower = get_user_by_email(session, "casesensitive@example.com")

        assert found_exact is not None
        assert found_lower is None

    def test_get_user_by_username_exists(self, session: Session):
        """Test getting a user by username when user exists."""
        user = User(
            email="username@example.com",
            username="uniqueuser",
            first_name="Unique",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()

        found_user = get_user_by_username(session, "uniqueuser")

        assert found_user is not None
        assert found_user.username == "uniqueuser"
        assert found_user.email == "username@example.com"

    def test_get_user_by_username_not_exists(self, session: Session):
        """Test getting a user by username when user doesn't exist."""
        found_user = get_user_by_username(session, "nonexistentuser")

        assert found_user is None

    def test_get_user_by_username_case_sensitive(self, session: Session):
        """Test that username lookup is case-sensitive."""
        user = User(
            email="caseuser@example.com",
            username="CamelCaseUser",
            first_name="Camel",
            last_name="Case",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()

        found_exact = get_user_by_username(session, "CamelCaseUser")
        found_lower = get_user_by_username(session, "camelcaseuser")

        assert found_exact is not None
        assert found_lower is None

    def test_get_user_by_id_exists(self, session: Session):
        """Test getting a user by ID when user exists."""
        user = User(
            email="idtest@example.com",
            username="idtestuser",
            first_name="ID",
            last_name="Test",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        found_user = get_user_by_id(session, user.id)

        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.username == "idtestuser"

    def test_get_user_by_id_not_exists(self, session: Session):
        """Test getting a user by ID when user doesn't exist."""
        found_user = get_user_by_id(session, 99999)

        assert found_user is None

    def test_create_user_with_inactive_status(self, session: Session):
        """Test creating a user with is_active=False."""
        user = User(
            email="inactive@example.com",
            username="inactiveuser",
            first_name="Inactive",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=False,
        )

        created_user = create_user(session, user)

        assert created_user is not None
        assert created_user.is_active is False

    def test_create_multiple_users(self, session: Session):
        """Test creating multiple users."""
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

        created_user1 = create_user(session, user1)
        created_user2 = create_user(session, user2)

        if not created_user1:
            raise ValueError("Created users must not be None")
        if not created_user2:
            raise ValueError("Created users must not be None")
        assert created_user1.id != created_user2.id
        assert created_user1.email != created_user2.email
        assert created_user1.username != created_user2.username

    def test_get_user_by_email_after_multiple_creates(self, session: Session):
        """Test getting user by email after creating multiple users."""
        users = [
            User(
                email=f"user{i}@example.com",
                username=f"user{i}",
                first_name=f"User{i}",
                last_name="Test",
                hashed_password=get_password_hash("password123"),
                is_active=True,
            )
            for i in range(5)
        ]

        for user in users:
            create_user(session, user)

        found_user = get_user_by_email(session, "user3@example.com")

        assert found_user is not None
        assert found_user.username == "user3"
