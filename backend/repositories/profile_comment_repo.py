from sqlmodel import Session, select

from models.models import ProfileComment, User


def get_profile_comments(session: Session, profile_user_id: int) -> list[ProfileComment]:
    """Get all comments for a specific user profile."""
    statement = select(ProfileComment).where(ProfileComment.profile_user_id == profile_user_id)
    return list(session.exec(statement).all())


def get_profile_comments_with_authors(
    session: Session, profile_user_id: int
) -> list[tuple[ProfileComment, User]]:
    """Get profile comments with author information."""
    comments = get_profile_comments(session, profile_user_id)
    result: list[tuple[ProfileComment, User]] = []
    for comment in comments:
        author = session.get(User, comment.author_id)
        if author:
            result.append((comment, author))
    return result


def get_profile_comment_by_id(session: Session, comment_id: int) -> ProfileComment | None:
    """Get a profile comment by ID."""
    return session.get(ProfileComment, comment_id)


def create_profile_comment(session: Session, comment: ProfileComment) -> ProfileComment:
    """Create a new profile comment."""
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


def update_profile_comment(
    session: Session, comment_id: int, content: str
) -> ProfileComment | None:
    """Update a profile comment's content."""
    comment = session.get(ProfileComment, comment_id)
    if not comment:
        return None
    comment.content = content
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


def delete_profile_comment(session: Session, comment_id: int) -> bool:
    """Delete a profile comment. Returns True if deleted, False if not found."""
    comment = session.get(ProfileComment, comment_id)
    if not comment:
        return False
    session.delete(comment)
    session.commit()
    return True
