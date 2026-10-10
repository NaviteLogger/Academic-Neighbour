from sqlmodel import Session, desc, select

from models.models import Comment, User


def create_comment(session: Session, comment: Comment) -> Comment:
    """Create a new comment."""
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


def get_comments_by_post(session: Session, post_id: int) -> list[Comment]:
    """Get all comments for a specific post, ordered by newest first."""
    statement = select(Comment).where(Comment.post_id == post_id).order_by(desc(Comment.created_at))
    return list(session.exec(statement).all())


def get_comment_by_id(session: Session, comment_id: int) -> Comment | None:
    """Get a comment by its ID."""
    return session.get(Comment, comment_id)


def get_comment_with_author(session: Session, comment_id: int) -> tuple[Comment, User] | None:
    """Get a comment by ID with author information."""
    comment = session.get(Comment, comment_id)
    if not comment:
        return None
    author = session.get(User, comment.author_id)
    if not author:
        return None
    return (comment, author)


def get_comments_with_authors(session: Session, post_id: int) -> list[tuple[Comment, User]]:
    """Get all comments for a post with their authors."""
    comments = get_comments_by_post(session, post_id)
    result: list[tuple[Comment, User]] = []
    for comment in comments:
        author = session.get(User, comment.author_id)
        if author:
            result.append((comment, author))
    return result


def delete_comment(session: Session, comment_id: int) -> bool:
    """Delete a comment. Returns True if deleted, False if not found."""
    comment = session.get(Comment, comment_id)
    if not comment:
        return False
    session.delete(comment)
    session.commit()
    return True


def update_comment(session: Session, comment_id: int, new_content: str) -> Comment | None:
    """Update a comment's content. Returns updated comment or None if not found."""
    comment = session.get(Comment, comment_id)
    if not comment:
        return None
    comment.content = new_content
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment
