from sqlmodel import Session

from models.models import Friendship, FriendshipStatusEnum, User
from repositories.friendship_repo import (
    create_friendship,
    get_accepted_friends,
    get_accepted_friendship,
    get_friendship_any_status,
    get_pending_friendship,
    get_received_pending_requests,
    get_sent_pending_requests,
    update_friendship,
)
from services.security import get_password_hash


class TestFriendshipRepository:
    """Tests for friendship repository functions."""

    def test_create_friendship(self, session: Session):
        """Test creating a new friendship."""
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

        if not user1.id or not user2.id:
            raise ValueError("Users must have IDs")

        friendship = Friendship(
            requester_id=user1.id,
            addressee_id=user2.id,
            status=FriendshipStatusEnum.PENDING,
        )

        created_friendship = create_friendship(session, friendship)

        assert created_friendship is not None
        assert created_friendship.id is not None
        assert created_friendship.requester_id == user1.id
        assert created_friendship.addressee_id == user2.id
        assert created_friendship.status == FriendshipStatusEnum.PENDING

    def test_get_friendship_any_status_exists(self, session: Session):
        """Test getting friendship with any status when it exists."""
        user1 = User(
            email="anystatus1@example.com",
            username="anystatus1",
            first_name="Any",
            last_name="One",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        user2 = User(
            email="anystatus2@example.com",
            username="anystatus2",
            first_name="Any",
            last_name="Two",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        if not user1.id or not user2.id:
            raise ValueError("Users must have IDs")

        friendship = Friendship(
            requester_id=user1.id,
            addressee_id=user2.id,
            status=FriendshipStatusEnum.PENDING,
        )
        session.add(friendship)
        session.commit()

        found = get_friendship_any_status(session, user1.id, user2.id)

        assert found is not None
        assert found.requester_id == user1.id
        assert found.addressee_id == user2.id

    def test_get_friendship_any_status_bidirectional(self, session: Session):
        """Test that get_friendship_any_status works in both directions."""
        user1 = User(
            email="bidir1@example.com",
            username="bidir1",
            first_name="Bidir",
            last_name="One",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        user2 = User(
            email="bidir2@example.com",
            username="bidir2",
            first_name="Bidir",
            last_name="Two",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        if not user1.id or not user2.id:
            raise ValueError("Users must have IDs")

        friendship = Friendship(
            requester_id=user1.id,
            addressee_id=user2.id,
            status=FriendshipStatusEnum.ACCEPTED,
        )
        session.add(friendship)
        session.commit()

        found_forward = get_friendship_any_status(session, user1.id, user2.id)
        found_reverse = get_friendship_any_status(session, user2.id, user1.id)

        assert found_forward is not None
        assert found_reverse is not None
        assert found_forward.id == found_reverse.id

    def test_get_friendship_any_status_not_exists(self, session: Session):
        """Test getting friendship when no relationship exists."""
        user1 = User(
            email="nostatus1@example.com",
            username="nostatus1",
            first_name="NoStatus",
            last_name="One",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        user2 = User(
            email="nostatus2@example.com",
            username="nostatus2",
            first_name="NoStatus",
            last_name="Two",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        if not user1.id or not user2.id:
            raise ValueError("Users must have IDs")

        found = get_friendship_any_status(session, user1.id, user2.id)

        assert found is None

    def test_get_pending_friendship_exists(self, session: Session):
        """Test getting pending friendship when it exists."""
        user1 = User(
            email="pending1@example.com",
            username="pending1",
            first_name="Pending",
            last_name="One",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        user2 = User(
            email="pending2@example.com",
            username="pending2",
            first_name="Pending",
            last_name="Two",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        if not user1.id or not user2.id:
            raise ValueError("Users must have IDs")

        friendship = Friendship(
            requester_id=user1.id,
            addressee_id=user2.id,
            status=FriendshipStatusEnum.PENDING,
        )
        session.add(friendship)
        session.commit()

        found = get_pending_friendship(session, user1.id, user2.id)

        assert found is not None
        assert found.requester_id == user1.id
        assert found.addressee_id == user2.id
        assert found.status == FriendshipStatusEnum.PENDING

    def test_get_pending_friendship_accepted_returns_none(self, session: Session):
        """Test that get_pending_friendship returns None for accepted friendship."""
        user1 = User(
            email="accepted1@example.com",
            username="accepted1",
            first_name="Accepted",
            last_name="One",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        user2 = User(
            email="accepted2@example.com",
            username="accepted2",
            first_name="Accepted",
            last_name="Two",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        if not user1.id or not user2.id:
            raise ValueError("Users must have IDs")

        friendship = Friendship(
            requester_id=user1.id,
            addressee_id=user2.id,
            status=FriendshipStatusEnum.ACCEPTED,
        )
        session.add(friendship)
        session.commit()

        found = get_pending_friendship(session, user1.id, user2.id)

        assert found is None

    def test_get_accepted_friendship_exists(self, session: Session):
        """Test getting accepted friendship when it exists."""
        user1 = User(
            email="getaccepted1@example.com",
            username="getaccepted1",
            first_name="GetAccepted",
            last_name="One",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        user2 = User(
            email="getaccepted2@example.com",
            username="getaccepted2",
            first_name="GetAccepted",
            last_name="Two",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        if not user1.id or not user2.id:
            raise ValueError("Users must have IDs")

        friendship = Friendship(
            requester_id=user1.id,
            addressee_id=user2.id,
            status=FriendshipStatusEnum.ACCEPTED,
        )
        session.add(friendship)
        session.commit()

        found = get_accepted_friendship(session, user1.id, user2.id)

        assert found is not None
        assert found.status == FriendshipStatusEnum.ACCEPTED

    def test_get_accepted_friendship_bidirectional(self, session: Session):
        """Test that get_accepted_friendship works in both directions."""
        user1 = User(
            email="acceptbidir1@example.com",
            username="acceptbidir1",
            first_name="AcceptBidir",
            last_name="One",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        user2 = User(
            email="acceptbidir2@example.com",
            username="acceptbidir2",
            first_name="AcceptBidir",
            last_name="Two",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        if not user1.id or not user2.id:
            raise ValueError("Users must have IDs")

        friendship = Friendship(
            requester_id=user1.id,
            addressee_id=user2.id,
            status=FriendshipStatusEnum.ACCEPTED,
        )
        session.add(friendship)
        session.commit()

        found_forward = get_accepted_friendship(session, user1.id, user2.id)
        found_reverse = get_accepted_friendship(session, user2.id, user1.id)

        assert found_forward is not None
        assert found_reverse is not None
        assert found_forward.id == found_reverse.id

    def test_update_friendship(self, session: Session):
        """Test updating a friendship status."""
        user1 = User(
            email="update1@example.com",
            username="update1",
            first_name="Update",
            last_name="One",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        user2 = User(
            email="update2@example.com",
            username="update2",
            first_name="Update",
            last_name="Two",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        if not user1.id or not user2.id:
            raise ValueError("Users must have IDs")

        friendship = Friendship(
            requester_id=user1.id,
            addressee_id=user2.id,
            status=FriendshipStatusEnum.PENDING,
        )
        session.add(friendship)
        session.commit()
        session.refresh(friendship)

        friendship.status = FriendshipStatusEnum.ACCEPTED
        updated = update_friendship(session, friendship)

        assert updated is not None
        assert updated.status == FriendshipStatusEnum.ACCEPTED
        assert updated.id == friendship.id

    def test_get_accepted_friends_empty(self, session: Session):
        """Test getting accepted friends when user has none."""
        user = User(
            email="nofriends@example.com",
            username="nofriends",
            first_name="No",
            last_name="Friends",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        friends = get_accepted_friends(session, user.id)

        assert friends == []
        assert len(friends) == 0

    def test_get_accepted_friends_as_requester(self, session: Session):
        """Test getting accepted friends where user is the requester."""
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

        if not user1.id or not user2.id:
            raise ValueError("Users must have IDs")

        friendship = Friendship(
            requester_id=user1.id,
            addressee_id=user2.id,
            status=FriendshipStatusEnum.ACCEPTED,
        )
        session.add(friendship)
        session.commit()

        friends = get_accepted_friends(session, user1.id)

        assert len(friends) == 1
        assert friends[0].id == user2.id
        assert friends[0].username == "addressee"

    def test_get_accepted_friends_as_addressee(self, session: Session):
        """Test getting accepted friends where user is the addressee."""
        user1 = User(
            email="asaddressee@example.com",
            username="asaddressee",
            first_name="AsAddressee",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        user2 = User(
            email="asrequester@example.com",
            username="asrequester",
            first_name="AsRequester",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        if not user1.id or not user2.id:
            raise ValueError("Users must have IDs")

        friendship = Friendship(
            requester_id=user2.id,
            addressee_id=user1.id,
            status=FriendshipStatusEnum.ACCEPTED,
        )
        session.add(friendship)
        session.commit()

        friends = get_accepted_friends(session, user1.id)

        assert len(friends) == 1
        assert friends[0].id == user2.id
        assert friends[0].username == "asrequester"

    def test_get_accepted_friends_multiple(self, session: Session):
        """Test getting accepted friends with multiple friends."""
        user1 = User(
            email="multifriend@example.com",
            username="multifriend",
            first_name="Multi",
            last_name="Friend",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        user2 = User(
            email="friend2@example.com",
            username="friendtwo",
            first_name="Friend",
            last_name="Two",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        user3 = User(
            email="friend3@example.com",
            username="friendthree",
            first_name="Friend",
            last_name="Three",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.add(user3)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)
        session.refresh(user3)

        if not user1.id or not user2.id or not user3.id:
            raise ValueError("Users must have IDs")

        friendship1 = Friendship(
            requester_id=user1.id,
            addressee_id=user2.id,
            status=FriendshipStatusEnum.ACCEPTED,
        )
        friendship2 = Friendship(
            requester_id=user3.id,
            addressee_id=user1.id,
            status=FriendshipStatusEnum.ACCEPTED,
        )
        session.add(friendship1)
        session.add(friendship2)
        session.commit()

        friends = get_accepted_friends(session, user1.id)

        assert len(friends) == 2
        usernames = {f.username for f in friends}
        assert "friendtwo" in usernames
        assert "friendthree" in usernames

    def test_get_accepted_friends_excludes_pending(self, session: Session):
        """Test that get_accepted_friends excludes pending friendships."""
        user1 = User(
            email="excludepending@example.com",
            username="excludepending",
            first_name="Exclude",
            last_name="Pending",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        user2 = User(
            email="pendingfriend@example.com",
            username="pendingfriend",
            first_name="Pending",
            last_name="Friend",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        if not user1.id or not user2.id:
            raise ValueError("Users must have IDs")

        friendship = Friendship(
            requester_id=user1.id,
            addressee_id=user2.id,
            status=FriendshipStatusEnum.PENDING,
        )
        session.add(friendship)
        session.commit()

        friends = get_accepted_friends(session, user1.id)

        assert len(friends) == 0

    def test_get_received_pending_requests(self, session: Session):
        """Test getting received pending friend requests."""
        user1 = User(
            email="receiver@example.com",
            username="receiver",
            first_name="Receiver",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        user2 = User(
            email="sender@example.com",
            username="sender",
            first_name="Sender",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        if not user1.id or not user2.id:
            raise ValueError("Users must have IDs")

        friendship = Friendship(
            requester_id=user2.id,
            addressee_id=user1.id,
            status=FriendshipStatusEnum.PENDING,
        )
        session.add(friendship)
        session.commit()

        requests = get_received_pending_requests(session, user1.id)

        assert len(requests) == 1
        assert requests[0].id == user2.id
        assert requests[0].username == "sender"

    def test_get_received_pending_requests_empty(self, session: Session):
        """Test getting received pending requests when there are none."""
        user = User(
            email="norequests@example.com",
            username="norequests",
            first_name="No",
            last_name="Requests",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        requests = get_received_pending_requests(session, user.id)

        assert len(requests) == 0

    def test_get_sent_pending_requests(self, session: Session):
        """Test getting sent pending friend requests."""
        user1 = User(
            email="sentrequests@example.com",
            username="sentrequests",
            first_name="Sent",
            last_name="Requests",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        user2 = User(
            email="recipient@example.com",
            username="recipient",
            first_name="Recipient",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        if not user1.id or not user2.id:
            raise ValueError("Users must have IDs")

        friendship = Friendship(
            requester_id=user1.id,
            addressee_id=user2.id,
            status=FriendshipStatusEnum.PENDING,
        )
        session.add(friendship)
        session.commit()

        requests = get_sent_pending_requests(session, user1.id)

        assert len(requests) == 1
        assert requests[0].id == user2.id
        assert requests[0].username == "recipient"

    def test_get_sent_pending_requests_empty(self, session: Session):
        """Test getting sent pending requests when there are none."""
        user = User(
            email="nosentrequests@example.com",
            username="nosentrequests",
            first_name="NoSent",
            last_name="Requests",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        requests = get_sent_pending_requests(session, user.id)

        assert len(requests) == 0
