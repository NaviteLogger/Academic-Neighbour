from sqlmodel import Session, and_, or_, select

from models.models import Friendship, FriendshipStatusEnum, User


def get_friendship_any_status(session: Session, user1_id: int, user2_id: int) -> Friendship | None:
    """Sprawdza, czy istnieje jakakolwiek relacja między dwoma użytkownikami."""
    statement = select(Friendship).where(
        or_(
            (Friendship.requester_id == user1_id) & (Friendship.addressee_id == user2_id),
            (Friendship.requester_id == user2_id) & (Friendship.addressee_id == user1_id),
        )
    )
    return session.exec(statement).one_or_none()


def get_pending_friendship(
    session: Session, requester_id: int, addressee_id: int
) -> Friendship | None:
    """Wyszukuje oczekujące zaproszenie od requester_id do addressee_id."""
    statement = select(Friendship).where(
        Friendship.requester_id == requester_id,
        Friendship.addressee_id == addressee_id,
        Friendship.status == FriendshipStatusEnum.PENDING,
    )
    return session.exec(statement).one_or_none()


def get_accepted_friendship(session: Session, user1_id: int, user2_id: int) -> Friendship | None:
    """Wyszukuje zaakceptowaną przyjaźń między dwoma użytkownikami."""
    statement = select(Friendship).where(
        and_(
            or_(
                (Friendship.requester_id == user1_id) & (Friendship.addressee_id == user2_id),
                (Friendship.requester_id == user2_id) & (Friendship.addressee_id == user1_id),
            ),
            Friendship.status == FriendshipStatusEnum.ACCEPTED,
        )
    )
    return session.exec(statement).one_or_none()


def create_friendship(session: Session, friendship: Friendship) -> Friendship:
    """Tworzy nowy wpis relacji w bazie danych."""
    session.add(friendship)
    session.commit()
    session.refresh(friendship)
    return friendship


def update_friendship(session: Session, friendship: Friendship) -> Friendship:
    """Aktualizuje istniejącą relację (np. zmienia status)."""
    session.add(friendship)
    session.commit()
    session.refresh(friendship)
    return friendship


# === NOWE FUNKCJE ===


def get_accepted_friends(session: Session, user_id: int) -> list[User]:
    """Pobiera listę zaakceptowanych znajomych dla danego użytkownika."""

    # 1. Użytkownicy, do których 'user_id' wysłał zaproszenie i zostało zaakceptowane
    statement1 = (
        select(User)
        .join(Friendship, User.id == Friendship.addressee_id)  # type: ignore
        .where(
            Friendship.requester_id == user_id,
            Friendship.status == FriendshipStatusEnum.ACCEPTED,
        )
    )

    # 2. Użytkownicy, od których 'user_id' otrzymał zaproszenie i je zaakceptował
    statement2 = (
        select(User)
        .join(Friendship, User.id == Friendship.requester_id)  # type: ignore
        .where(
            Friendship.addressee_id == user_id,
            Friendship.status == FriendshipStatusEnum.ACCEPTED,
        )
    )

    friends_as_requester = session.exec(statement1).all()
    friends_as_addressee = session.exec(statement2).all()

    return list(friends_as_requester) + list(friends_as_addressee)


def get_received_pending_requests(session: Session, user_id: int) -> list[User]:
    """
    Pobiera listę użytkowników (zapraszających),
    od których 'user_id' otrzymał oczekujące zaproszenia.
    """
    statement = (
        select(User)
        .join(Friendship, User.id == Friendship.requester_id)  # type: ignore
        .where(
            Friendship.addressee_id == user_id,
            Friendship.status == FriendshipStatusEnum.PENDING,
        )
    )
    return list(session.exec(statement).all())


def get_sent_pending_requests(session: Session, user_id: int) -> list[User]:
    """
    Pobiera listę użytkowników (zaproszonych),
    do których 'user_id' wysłał oczekujące zaproszenia.
    """
    statement = (
        select(User)
        .join(Friendship, User.id == Friendship.addressee_id)  # type: ignore
        .where(
            Friendship.requester_id == user_id,
            Friendship.status == FriendshipStatusEnum.PENDING,
        )
    )
    return list(session.exec(statement).all())
