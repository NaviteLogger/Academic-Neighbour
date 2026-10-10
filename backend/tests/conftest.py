"""Pytest configuration and fixtures for testing."""

import enum
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from database.database import get_session
from main import app
from models.models import (
    AuthenticatedUser,
    Comment,
    Event,
    Friendship,
    FriendshipScenario,
    FriendshipStatusEnum,
    Post,
    User,
    UserRole,
)
from services.security import get_password_hash


class FixtureEnum(str, enum.Enum):
    """Enumeration of all available test fixtures."""

    SESSION = "session"
    CLIENT = "client"
    LOGGED_IN_USER = "logged_in_user"
    LOGGED_IN_ADMIN = "logged_in_admin"
    SECOND_USER = "second_user"
    SETUP_FRIENDSHIP_SCENARIO = "setup_friendship_scenario"
    TEST_POST = "test_post"
    TEST_COMMENT = "test_comment"
    TEST_EVENT = "test_event"


@pytest.fixture(name=FixtureEnum.SESSION)
def session_fixture():
    """Create a test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name=FixtureEnum.CLIENT)
def client_fixture(session: Session):
    """Create a test client with overridden database session."""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name=FixtureEnum.LOGGED_IN_USER)
def logged_in_user_fixture(client: TestClient, session: Session) -> AuthenticatedUser:
    """Create a logged-in regular user and return user data with access token."""
    # Create a test user
    user = User(
        email="testuser@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
        hashed_password=get_password_hash("testpassword"),
        role=UserRole.USER,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Login to get access token
    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "testpassword"},
    )
    assert response.status_code == 200
    token_data = response.json()

    return AuthenticatedUser(
        user=user,
        token=token_data["access_token"],
        headers={"Authorization": f"Bearer {token_data['access_token']}"},
    )


@pytest.fixture(name=FixtureEnum.LOGGED_IN_ADMIN)
def logged_in_admin_fixture(client: TestClient, session: Session) -> AuthenticatedUser:
    """Create a logged-in admin user and return user data with access token."""
    # Create a test admin user
    admin = User(
        email="admin@example.com",
        username="admin",
        first_name="Admin",
        last_name="User",
        hashed_password=get_password_hash("adminpassword"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)

    # Login to get access token
    response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "adminpassword"},
    )
    assert response.status_code == 200
    token_data = response.json()

    return AuthenticatedUser(
        user=admin,
        token=token_data["access_token"],
        headers={"Authorization": f"Bearer {token_data['access_token']}"},
    )


@pytest.fixture(name=FixtureEnum.SETUP_FRIENDSHIP_SCENARIO)
def setup_friendship_scenario_fixture(session: Session) -> FriendshipScenario:
    """Fixture to set up users and friendships for testing."""
    hashed_password = get_password_hash("testpassword")

    user_a = User(
        email="user_a@test.com",
        username="UserA",
        first_name="User",
        last_name="A",
        hashed_password=hashed_password,
        is_active=True,
    )
    user_b = User(
        email="user_b@test.com",
        username="UserB",
        first_name="User",
        last_name="B",
        hashed_password=hashed_password,
        is_active=True,
    )
    user_c = User(
        email="user_c@test.com",
        username="UserC",
        first_name="User",
        last_name="C",
        hashed_password=hashed_password,
        is_active=True,
    )
    user_d = User(
        email="user_d@test.com",
        username="UserD",
        first_name="User",
        last_name="D",
        hashed_password=hashed_password,
        is_active=True,
    )

    session.add_all([user_a, user_b, user_c, user_d])
    session.commit()

    session.refresh(user_a)
    session.refresh(user_b)
    session.refresh(user_c)
    session.refresh(user_d)

    assert user_a.id is not None
    assert user_b.id is not None
    assert user_c.id is not None
    assert user_d.id is not None

    friendship_ab = Friendship(
        requester_id=user_a.id,
        addressee_id=user_b.id,
        status=FriendshipStatusEnum.ACCEPTED,
    )

    friendship_ca = Friendship(
        requester_id=user_c.id,
        addressee_id=user_a.id,
        status=FriendshipStatusEnum.PENDING,
    )

    friendship_ad = Friendship(
        requester_id=user_a.id,
        addressee_id=user_d.id,
        status=FriendshipStatusEnum.PENDING,
    )

    session.add_all([friendship_ab, friendship_ca, friendship_ad])
    session.commit()

    return FriendshipScenario(
        user_a_id=user_a.id,
        user_b_id=user_b.id,
        user_c_id=user_c.id,
        user_d_id=user_d.id,
    )


@pytest.fixture(name=FixtureEnum.SECOND_USER)
def second_user_fixture(client: TestClient, session: Session) -> AuthenticatedUser:
    """Create a second logged-in user and return user data with access token."""
    # Create a second test user
    user = User(
        email="seconduser@example.com",
        username="seconduser",
        first_name="Second",
        last_name="User",
        hashed_password=get_password_hash("secondpassword"),
        role=UserRole.USER,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Login to get access token
    response = client.post(
        "/auth/token",
        data={"username": "seconduser", "password": "secondpassword"},
    )
    assert response.status_code == 200
    token_data = response.json()

    return AuthenticatedUser(
        user=user,
        token=token_data["access_token"],
        headers={"Authorization": f"Bearer {token_data['access_token']}"},
    )


@pytest.fixture(name=FixtureEnum.TEST_POST)
def test_post_fixture(session: Session, logged_in_user: AuthenticatedUser) -> Post:
    """Create a test post."""
    if not logged_in_user.user.id:
        raise ValueError("Logged in user must have an ID")
    post = Post(
        content="This is a test post about dorm life!",
        author_id=logged_in_user.user.id,
    )
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


@pytest.fixture(name=FixtureEnum.TEST_COMMENT)
def test_comment_fixture(
    session: Session, logged_in_user: AuthenticatedUser, test_post: Post
) -> Comment:
    """Create a test comment on the test post."""
    if not logged_in_user.user.id:
        raise ValueError("Logged in user must have an ID")

    if not test_post.id:
        raise ValueError("Test post must have an ID")
    comment = Comment(
        content="This is a test comment!",
        author_id=logged_in_user.user.id,
        post_id=test_post.id,
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


@pytest.fixture(name=FixtureEnum.TEST_EVENT)
def test_event_fixture(session: Session, logged_in_user: AuthenticatedUser) -> Event:
    """Create a test event."""
    if not logged_in_user.user.id:
        raise ValueError("Logged in user must have an ID")
    event = Event(
        title="Dorm Party",
        description="Let's have some fun!",
        location="Common Room",
        start_date=datetime(2024, 12, 31, 20, 0, 0, tzinfo=UTC),
        end_date=datetime(2024, 12, 31, 23, 59, 0, tzinfo=UTC),
        creator_id=logged_in_user.user.id,
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event
