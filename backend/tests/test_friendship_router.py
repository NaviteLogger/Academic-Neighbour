from typing import Any

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from models.models import (
    AuthenticatedUser,
    Friendship,
    FriendshipScenario,
    FriendshipStatusEnum,
    User,
)
from services.security import get_password_hash


def get_auth_headers(client: TestClient, username: str, password: str = "testpassword"):
    """Helper to login and get authorization token."""
    response = client.post("/auth/token", data={"username": username, "password": password})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestFriendshipListing:
    """Tests for listing friends and friend requests."""

    def test_read_accepted_friends(
        self, client: TestClient, setup_friendship_scenario: FriendshipScenario
    ):
        """Tests GET /?filter_type=accepted - should return a list of accepted friends."""
        headers = get_auth_headers(client, "UserA")
        response = client.get("/friendships/", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        friends_data: list[dict[str, Any]] = response.json()

        assert isinstance(friends_data, list)
        assert len(friends_data) == 1

        friends_list: list[User] = [User.model_validate(user) for user in friends_data]
        assert friends_list[0].username == "UserB"

    def test_read_accepted_friends_explicit(
        self, client: TestClient, setup_friendship_scenario: FriendshipScenario
    ):
        """
        Tests GET /?filter_type=accepted (explicit).

        Should return a list of accepted friends.
        """
        headers = get_auth_headers(client, "UserA")
        response = client.get("/friendships/?filter_type=accepted", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        friends_data: list[dict[str, Any]] = response.json()

        assert isinstance(friends_data, list)
        assert len(friends_data) == 1

        friends_list: list[User] = [User.model_validate(user) for user in friends_data]
        assert friends_list[0].username == "UserB"

    def test_read_pending_requests(
        self, client: TestClient, setup_friendship_scenario: FriendshipScenario
    ):
        """Tests GET /?filter_type=pending - should return a list of received friend requests."""
        headers = get_auth_headers(client, "UserA")
        response = client.get("/friendships/?filter_type=pending", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        pending_data: list[dict[str, Any]] = response.json()

        assert isinstance(pending_data, list)
        assert len(pending_data) == 1

        pending_list: list[User] = [User.model_validate(user) for user in pending_data]
        assert pending_list[0].username == "UserC"

    def test_read_sent_requests(
        self, client: TestClient, setup_friendship_scenario: FriendshipScenario
    ):
        """Tests GET /?filter_type=sent - should return a list of sent friend requests."""
        headers = get_auth_headers(client, "UserA")
        response = client.get("/friendships/?filter_type=sent", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        sent_data: list[dict[str, Any]] = response.json()

        assert isinstance(sent_data, list)
        assert len(sent_data) == 1

        sent_list: list[User] = [User.model_validate(user) for user in sent_data]
        assert sent_list[0].username == "UserD"

    def test_read_friends_unauthenticated(self, client: TestClient):
        """Test that unauthenticated users cannot list friends."""
        response = client.get("/friendships/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_read_friends_no_friends(self, client: TestClient, logged_in_user: AuthenticatedUser):
        """Test listing friends when user has no friends."""
        response = client.get("/friendships/", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_200_OK
        friends_data: list[dict[str, Any]] = response.json()
        assert isinstance(friends_data, list)
        assert len(friends_data) == 0

    def test_read_friends_invalid_filter(
        self, client: TestClient, setup_friendship_scenario: FriendshipScenario
    ):
        """Test that invalid filter type defaults to accepted friends."""
        headers = get_auth_headers(client, "UserA")
        # Invalid filter should be caught by Pydantic validation
        response = client.get("/friendships/?filter_type=invalid", headers=headers)
        # Should return 422 Unprocessable Entity for invalid enum value
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestSendFriendRequest:
    """Tests for sending friend requests."""

    def test_send_friend_request_success(self, client: TestClient, session: Session):
        """Test successfully sending a friend request."""
        # Create two users
        hashed_password = get_password_hash("testpassword")
        user1 = User(
            email="sender@example.com",
            username="sender",
            first_name="Sender",
            last_name="User",
            hashed_password=hashed_password,
            is_active=True,
        )
        user2 = User(
            email="receiver@example.com",
            username="receiver",
            first_name="Receiver",
            last_name="User",
            hashed_password=hashed_password,
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        headers = get_auth_headers(client, "sender")
        response = client.post(f"/friendships/request/{user2.id}", headers=headers)

        assert response.status_code == status.HTTP_201_CREATED
        friendship_data: dict[str, Any] = response.json()
        friendship: Friendship = Friendship.model_validate(friendship_data)
        assert friendship.requester_id == user1.id
        assert friendship.addressee_id == user2.id
        assert friendship.status == FriendshipStatusEnum.PENDING

    def test_send_friend_request_to_self(
        self, client: TestClient, logged_in_user: AuthenticatedUser
    ):
        """Test that users cannot send friend requests to themselves."""
        response = client.post(
            f"/friendships/request/{logged_in_user.user.id}", headers=logged_in_user.headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data: dict[str, Any] = response.json()
        assert "yourself" in data["detail"].lower()

    def test_send_friend_request_to_nonexistent_user(
        self, client: TestClient, logged_in_user: AuthenticatedUser
    ):
        """Test sending friend request to non-existent user."""
        response = client.post("/friendships/request/99999", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data: dict[str, Any] = response.json()
        assert "does not exist" in data["detail"]

    def test_send_duplicate_friend_request(self, client: TestClient, session: Session):
        """Test that duplicate friend requests are rejected."""
        # Create two users
        hashed_password = get_password_hash("testpassword")
        user1 = User(
            email="user1@example.com",
            username="user1",
            first_name="User",
            last_name="One",
            hashed_password=hashed_password,
            is_active=True,
        )
        user2 = User(
            email="user2@example.com",
            username="user2",
            first_name="User",
            last_name="Two",
            hashed_password=hashed_password,
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        headers = get_auth_headers(client, "user1")

        # Send first request
        response = client.post(f"/friendships/request/{user2.id}", headers=headers)
        assert response.status_code == status.HTTP_201_CREATED

        # Try to send again
        response = client.post(f"/friendships/request/{user2.id}", headers=headers)
        assert response.status_code == status.HTTP_409_CONFLICT
        data: dict[str, Any] = response.json()
        assert "already been sent" in data["detail"]

    def test_send_friend_request_to_existing_friend(
        self, client: TestClient, setup_friendship_scenario: FriendshipScenario
    ):
        """Test that friend requests cannot be sent to existing friends."""
        # UserA and UserB are already friends
        headers = get_auth_headers(client, "UserA")
        userb_id = setup_friendship_scenario.user_b_id

        response = client.post(f"/friendships/request/{userb_id}", headers=headers)
        assert response.status_code == status.HTTP_409_CONFLICT
        data: dict[str, Any] = response.json()
        assert "already friends" in data["detail"].lower()

    def test_send_friend_request_unauthenticated(self, client: TestClient, session: Session):
        """Test that unauthenticated users cannot send friend requests."""
        user = User(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            hashed_password=get_password_hash("testpassword"),
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        response = client.post(f"/friendships/request/{user.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAcceptFriendRequest:
    """Tests for accepting friend requests."""

    def test_accept_friend_request_success(self, client: TestClient, session: Session):
        """Test successfully accepting a friend request."""
        # Create two users
        hashed_password = get_password_hash("testpassword")
        requester = User(
            email="requester@example.com",
            username="requester",
            first_name="Requester",
            last_name="User",
            hashed_password=hashed_password,
            is_active=True,
        )
        addressee = User(
            email="addressee@example.com",
            username="addressee",
            first_name="Addressee",
            last_name="User",
            hashed_password=hashed_password,
            is_active=True,
        )
        session.add(requester)
        session.add(addressee)
        session.commit()
        session.refresh(requester)
        session.refresh(addressee)

        # Requester sends request
        requester_headers = get_auth_headers(client, "requester")
        client.post(f"/friendships/request/{addressee.id}", headers=requester_headers)

        # Addressee accepts
        addressee_headers = get_auth_headers(client, "addressee")
        response = client.post(f"/friendships/accept/{requester.id}", headers=addressee_headers)

        assert response.status_code == status.HTTP_200_OK
        friendship_data: dict[str, Any] = response.json()
        friendship: Friendship = Friendship.model_validate(friendship_data)
        assert friendship.status == FriendshipStatusEnum.ACCEPTED

    def test_accept_nonexistent_request(
        self, client: TestClient, logged_in_user: AuthenticatedUser
    ):
        """Test accepting a non-existent friend request."""
        response = client.post("/friendships/accept/99999", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data: dict[str, Any] = response.json()
        assert "No pending friend request" in data["detail"]

    def test_accept_friend_request_unauthenticated(self, client: TestClient):
        """Test that unauthenticated users cannot accept friend requests."""
        response = client.post("/friendships/accept/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_accept_already_accepted_request(self, client: TestClient, session: Session):
        """Test that already accepted requests cannot be accepted again."""
        # Create two users with accepted friendship
        hashed_password = get_password_hash("testpassword")
        user1 = User(
            email="user1@example.com",
            username="user1acc",
            first_name="User",
            last_name="One",
            hashed_password=hashed_password,
            is_active=True,
        )
        user2 = User(
            email="user2@example.com",
            username="user2acc",
            first_name="User",
            last_name="Two",
            hashed_password=hashed_password,
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        assert user1.id is not None
        assert user2.id is not None

        # Create accepted friendship
        friendship = Friendship(
            requester_id=user1.id,
            addressee_id=user2.id,
            status=FriendshipStatusEnum.ACCEPTED,
        )
        session.add(friendship)
        session.commit()

        # Try to accept again
        headers = get_auth_headers(client, "user2acc")
        response = client.post(f"/friendships/accept/{user1.id}", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeclineFriendRequest:
    """Tests for declining friend requests."""

    def test_decline_friend_request_success(self, client: TestClient, session: Session):
        """Test successfully declining a friend request."""
        # Create two users
        hashed_password = get_password_hash("testpassword")
        requester = User(
            email="requester@example.com",
            username="requester_dec",
            first_name="Requester",
            last_name="User",
            hashed_password=hashed_password,
            is_active=True,
        )
        addressee = User(
            email="addressee@example.com",
            username="addressee_dec",
            first_name="Addressee",
            last_name="User",
            hashed_password=hashed_password,
            is_active=True,
        )
        session.add(requester)
        session.add(addressee)
        session.commit()
        session.refresh(requester)
        session.refresh(addressee)

        # Requester sends request
        requester_headers = get_auth_headers(client, "requester_dec")
        client.post(f"/friendships/request/{addressee.id}", headers=requester_headers)

        # Addressee declines
        addressee_headers = get_auth_headers(client, "addressee_dec")
        response = client.post(f"/friendships/decline/{requester.id}", headers=addressee_headers)

        assert response.status_code == status.HTTP_200_OK
        friendship_data: dict[str, Any] = response.json()
        friendship: Friendship = Friendship.model_validate(friendship_data)
        assert friendship.status == FriendshipStatusEnum.DECLINED

    def test_decline_nonexistent_request(
        self, client: TestClient, logged_in_user: AuthenticatedUser
    ):
        """Test declining a non-existent friend request."""
        response = client.post("/friendships/decline/99999", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data: dict[str, Any] = response.json()
        assert "No pending friend request" in data["detail"]

    def test_decline_friend_request_unauthenticated(self, client: TestClient):
        """Test that unauthenticated users cannot decline friend requests."""
        response = client.post("/friendships/decline/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRemoveFriend:
    """Tests for removing friends."""

    def test_remove_friend_success(
        self, client: TestClient, setup_friendship_scenario: FriendshipScenario
    ):
        """Test successfully removing a friend."""
        # UserA and UserB are friends
        headers = get_auth_headers(client, "UserA")
        userb_id = setup_friendship_scenario.user_b_id

        response = client.delete(f"/friendships/remove/{userb_id}", headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify they're no longer friends
        response = client.get("/friendships/", headers=headers)
        friends_data: list[dict[str, Any]] = response.json()
        assert len(friends_data) == 0

    def test_remove_friend_not_friends(
        self, client: TestClient, logged_in_user: AuthenticatedUser, session: Session
    ):
        """Test removing a user who is not a friend."""
        # Create another user
        other_user = User(
            email="other@example.com",
            username="otheruser",
            first_name="Other",
            last_name="User",
            hashed_password=get_password_hash("testpassword"),
        )
        session.add(other_user)
        session.commit()
        session.refresh(other_user)

        response = client.delete(
            f"/friendships/remove/{other_user.id}", headers=logged_in_user.headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data: dict[str, Any] = response.json()
        assert "not friends" in data["detail"].lower()

    def test_remove_friend_nonexistent_user(
        self, client: TestClient, logged_in_user: AuthenticatedUser
    ):
        """Test removing a non-existent user."""
        response = client.delete("/friendships/remove/99999", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_remove_friend_unauthenticated(self, client: TestClient):
        """Test that unauthenticated users cannot remove friends."""
        response = client.delete("/friendships/remove/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_remove_friend_pending_request(self, client: TestClient, session: Session):
        """Test that pending friend requests cannot be removed via remove endpoint."""
        # Create two users with pending friendship
        hashed_password = get_password_hash("testpassword")
        user1 = User(
            email="user1rem@example.com",
            username="user1rem",
            first_name="User",
            last_name="One",
            hashed_password=hashed_password,
            is_active=True,
        )
        user2 = User(
            email="user2rem@example.com",
            username="user2rem",
            first_name="User",
            last_name="Two",
            hashed_password=hashed_password,
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        # Send friend request
        headers = get_auth_headers(client, "user1rem")
        client.post(f"/friendships/request/{user2.id}", headers=headers)

        # Try to remove pending request
        response = client.delete(f"/friendships/remove/{user2.id}", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
