from sqlmodel import Session, select

from models.models import User


def get_user_by_email(session: Session, email: str) -> User | None:
    """

    Args:
        session (Session): The database session to use for the query.
        email (str): The email address to search for.

    Returns:
        User | None: The user with the specified email, or None if not found.
    """
    user = session.exec(select(User).where(User.email == email)).one_or_none()
    return user


def get_user_by_username(session: Session, username: str) -> User | None:
    """
    Retrieve a user by their username.

    Args:
        session (Session): The database session to use for the query.
        username (str): The username to search for.

    Returns:
        User | None: The user with the specified username, or None if not found.
    """
    user = session.exec(select(User).where(User.username == username)).one_or_none()
    return user


def create_user(session: Session, user: User) -> User | None:
    """Create a new user in the database."""
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_by_id(session: Session, user_id: int) -> User | None:
    """Retrieve a user by their ID."""
    statement = select(User).where(User.id == user_id)
    return session.exec(statement).one_or_none()


def search_users(session: Session, query: str) -> list[User]:
    """
    Search for users by username, first name, or last name.

    Args:
        session (Session): The database session.
        query (str): The search query string.

    Returns:
        list[User]: A list of users matching the search criteria.
    """
    statement = select(User).where(
        (User.username.ilike(f"%{query}%"))  # type: ignore
        | (User.first_name.ilike(f"%{query}%"))  # type: ignore
        | (User.last_name.ilike(f"%{query}%"))  # type: ignore
    )
    return list(session.exec(statement).all())
