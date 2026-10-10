from sqlmodel import Session, desc, select

from models.models import Post, PostLike, User


def get_all_posts(session: Session) -> list[Post]:
    """Get all posts ordered by newest first. Excludes group posts."""
    statement = select(Post).where(Post.group_id == None).order_by(desc(Post.created_at))  # noqa: E711
    return list(session.exec(statement).all())


def get_post_by_id(session: Session, post_id: int) -> Post | None:
    """Get a post by ID."""
    return session.get(Post, post_id)


def get_post_with_author(session: Session, post_id: int) -> tuple[Post, User] | None:
    """Get a post by ID with author information."""
    post = session.get(Post, post_id)
    if not post:
        return None
    author = session.get(User, post.author_id)
    if not author:
        return None
    return (post, author)


def create_post(session: Session, post: Post) -> Post:
    """Create a new post."""
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


def like_post(session: Session, user_id: int, post_id: int) -> PostLike:
    """Like a post. Creates a new like record."""
    # Check if already liked
    existing_like = session.exec(
        select(PostLike).where(PostLike.user_id == user_id, PostLike.post_id == post_id)
    ).first()

    if existing_like:
        return existing_like

    new_like = PostLike(user_id=user_id, post_id=post_id)
    session.add(new_like)
    session.commit()
    session.refresh(new_like)
    return new_like


def unlike_post(session: Session, user_id: int, post_id: int) -> bool:
    """Unlike a post. Returns True if a like was removed, False if no like existed."""
    like = session.exec(
        select(PostLike).where(PostLike.user_id == user_id, PostLike.post_id == post_id)
    ).first()

    if not like:
        return False

    session.delete(like)
    session.commit()
    return True


def get_post_likes_count(session: Session, post_id: int) -> int:
    """Get the count of likes for a specific post."""
    statement = select(PostLike).where(PostLike.post_id == post_id)
    likes = session.exec(statement).all()
    return len(likes)


def is_post_liked_by_user(session: Session, user_id: int, post_id: int) -> bool:
    """Check if a specific user has liked a specific post."""
    like = session.exec(
        select(PostLike).where(PostLike.user_id == user_id, PostLike.post_id == post_id)
    ).first()
    return like is not None
