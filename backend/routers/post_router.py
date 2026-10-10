from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from database.database import get_session
from models.models import LikesInfo, Post, PostCreate, PostLike, PostWithAuthor, User
from repositories.post_repo import (
    create_post as repo_create_post,
)
from repositories.post_repo import (
    get_all_posts,
    get_post_by_id,
    get_post_likes_count,
    get_post_with_author,
    is_post_liked_by_user,
    like_post,
    unlike_post,
)
from services.security import get_current_active_user

router = APIRouter(prefix="/posts", tags=["posts"])

session: Session = Depends(get_session)
current_user = Depends(get_current_active_user)


@router.get("/")
def read_posts(session: Session = session) -> list[Post]:
    """Get all posts."""
    return get_all_posts(session)


@router.get("/{post_id}")
def read_post(post_id: int, session: Session = session) -> Post:
    """Get a post by ID."""
    post = get_post_by_id(session, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.get("/{post_id}/with-author")
def read_post_with_author(post_id: int, session: Session = session) -> PostWithAuthor:
    """Get a post by ID with author information."""
    result = get_post_with_author(session, post_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post or author not found"
        )

    post, author = result

    if not post.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Post ID is missing"
        )

    return PostWithAuthor(
        id=post.id,
        content=post.content,
        author_id=post.author_id,
        created_at=str(post.created_at),
        author_name=author.username,
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: PostCreate,
    current_user: User = current_user,
    session: Session = session,
) -> Post:
    """Create a new post. Requires authentication."""
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User ID is missing"
        )

    new_post = Post(
        content=post_data.content,
        author_id=current_user.id,
    )
    return repo_create_post(session, new_post)


@router.post("/{post_id}/like", status_code=status.HTTP_201_CREATED)
def like_post_endpoint(
    post_id: int,
    current_user: User = current_user,
    session: Session = session,
) -> PostLike:
    """Like a post. Requires authentication."""
    # Check if post exists
    post = get_post_by_id(session, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User ID is missing"
        )

    return like_post(session, current_user.id, post_id)


@router.delete("/{post_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def unlike_post_endpoint(
    post_id: int,
    current_user: User = current_user,
    session: Session = session,
) -> None:
    """Unlike a post. Requires authentication."""
    # Check if post exists
    post = get_post_by_id(session, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User ID is missing"
        )

    was_unliked = unlike_post(session, current_user.id, post_id)
    if not was_unliked:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Like not found")


@router.get("/{post_id}/likes")
def get_post_likes(
    post_id: int,
    current_user: User | None = current_user,
    session: Session = session,
) -> LikesInfo:
    """Get likes information for a post. Returns count and whether current user has liked it."""
    post = get_post_by_id(session, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    likes_count = get_post_likes_count(session, post_id)

    liked_by_current_user = False
    if current_user and current_user.id:
        liked_by_current_user = is_post_liked_by_user(session, current_user.id, post_id)

    return LikesInfo(
        likes_count=likes_count,
        liked_by_current_user=liked_by_current_user,
    )
