import re
import string

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from database.database import get_session
from models.models import (
    CommentRequest,
    ProfileComment,
    ProfileCommentWithAuthor,
    User,
    UserCreate,
    UserRead,
)
from repositories.profile_comment_repo import (
    create_profile_comment,
    get_profile_comment_by_id,
    get_profile_comments_with_authors,
    update_profile_comment,
)
from repositories.user_repo import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    search_users,
)
from routers.auth_routes import TokenWithUser, login
from services.security import get_current_active_user, get_password_hash
from utils.logging import logger

router = APIRouter(prefix="/users", tags=["users"])

session: Session = Depends(get_session)
active_user = Depends(get_current_active_user)
current_user = Depends(get_current_active_user)


def is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def is_valid_password(password: str) -> bool:
    has_upper = any(ch.isupper() for ch in password)
    has_special = any(ch in string.punctuation for ch in password)
    long_enough = len(password) >= 8

    return has_upper and has_special and long_enough


@router.post("/register", response_model=TokenWithUser)
async def register_user(user: UserCreate, session: Session = session) -> TokenWithUser:
    """Register a new user and return an access token."""
    valid_email = is_valid_email(user.email)
    if not valid_email:
        logger.debug(f"Invalid email attempted during registration: {user.email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect Email")
    valid_password = is_valid_password(user.password)
    if not valid_password:
        logger.debug(f"Weak password attempted during registration for email: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must have: min. 8 characters, a special "
            "character and an uppercase letter",
        )
    user_from_database = get_user_by_username(session=session, username=user.username)
    if user_from_database:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )
    user_from_database = get_user_by_email(session=session, email=user.email)
    if user_from_database:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    user_create = User(
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=get_password_hash(user.password),
        is_active=True,
    )

    created_user: User | None = create_user(session=session, user=user_create)
    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User could not be created"
        )

    return await login(
        form_data=OAuth2PasswordRequestForm(
            username=user.username,
            password=user.password,
            scope="",
            grant_type="",
            client_id=None,
            client_secret=None,
        ),
        session=session,
    )


@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = active_user) -> User:
    """Get current authenticated user information. Returns user data excluding password."""
    return current_user


@router.post("/{user_id}/comments", status_code=status.HTTP_201_CREATED)
def create_profile_comment_endpoint(
    user_id: int,
    comment_data: CommentRequest,
    current_user: User = current_user,
    session: Session = session,
) -> ProfileCommentWithAuthor:
    """Create a new comment on a user profile. Requires authentication."""
    profile_user = get_user_by_id(session, user_id)
    if not profile_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not current_user.id:
        logger.error("User ID is missing")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User ID is missing"
        )

    new_comment = ProfileComment(
        content=comment_data.content,
        author_id=current_user.id,
        profile_user_id=user_id,
    )

    created_comment = create_profile_comment(session, new_comment)

    if not created_comment.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Comment ID is missing"
        )

    return ProfileCommentWithAuthor(
        id=created_comment.id,
        content=created_comment.content,
        author_id=created_comment.author_id,
        profile_user_id=created_comment.profile_user_id,
        created_at=str(created_comment.created_at),
        author_name=current_user.username,
    )


@router.get("/{user_id}/comments")
def get_profile_comments_endpoint(
    user_id: int,
    session: Session = session,
) -> list[ProfileCommentWithAuthor]:
    """Get all comments for a specific user profile."""
    # Check if profile user exists
    profile_user = get_user_by_id(session, user_id)
    if not profile_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Get comments with authors
    comments_with_authors = get_profile_comments_with_authors(session, user_id)

    # Build response
    result: list[ProfileCommentWithAuthor] = []
    for comment, author in comments_with_authors:
        if not comment.id:
            continue

        result.append(
            ProfileCommentWithAuthor(
                id=comment.id,
                content=comment.content,
                author_id=comment.author_id,
                profile_user_id=comment.profile_user_id,
                created_at=str(comment.created_at),
                author_name=author.username,
            )
        )

    return result


@router.put("/comments/{comment_id}")
def update_profile_comment_endpoint(
    comment_id: int,
    comment_data: CommentRequest,
    current_user: User = current_user,
    session: Session = session,
) -> ProfileCommentWithAuthor:
    """Update a profile comment's content.

    Only the comment author can update. Requires authentication.
    """
    comment = get_profile_comment_by_id(session, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    # Check if user is the author
    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own comments",
        )

    updated_comment = update_profile_comment(session, comment_id, comment_data.content)
    if not updated_comment:
        logger.error("Failed to update profile comment")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update comment"
        )

    if not updated_comment.id:
        logger.error("Comment ID is missing")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Comment ID is missing"
        )

    return ProfileCommentWithAuthor(
        id=updated_comment.id,
        content=updated_comment.content,
        author_id=updated_comment.author_id,
        profile_user_id=updated_comment.profile_user_id,
        created_at=str(updated_comment.created_at),
        author_name=current_user.username,
    )


@router.get("/search", response_model=list[UserRead])
def search_users_endpoint(
    query: str,
    session: Session = session,
) -> list[User]:
    """
    Search for users by username, first name, or last name.
    """
    if len(query) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 3 characters long",
        )
    return search_users(session, query)


@router.get("/{user_id}", response_model=UserRead)
def get_user_profile(user_id: int, session: Session = session) -> User:
    """Get user profile information by user ID. Returns public user data excluding password."""
    user = get_user_by_id(session=session, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
