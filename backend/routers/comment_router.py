from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from database.database import get_session
from models.models import Comment, CommentRequest, CommentWithAuthor, User
from repositories.comment_repo import (
    create_comment,
    delete_comment,
    get_comment_by_id,
    get_comments_with_authors,
    update_comment,
)
from repositories.post_repo import get_post_by_id
from services.security import get_current_active_user
from utils.logging import logger

router = APIRouter(prefix="/posts", tags=["comments"])

session: Session = Depends(get_session)
current_user = Depends(get_current_active_user)


@router.post("/{post_id}/comments", status_code=status.HTTP_201_CREATED)
def create_comment_endpoint(
    post_id: int,
    comment_data: CommentRequest,
    current_user: User = current_user,
    session: Session = session,
) -> CommentWithAuthor:
    """Create a new comment on a post. Requires authentication."""
    post = get_post_by_id(session, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if not current_user.id:
        logger.error("User ID is missing")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User ID is missing"
        )

    new_comment = Comment(
        content=comment_data.content,
        author_id=current_user.id,
        post_id=post_id,
    )

    created_comment = create_comment(session, new_comment)

    if not created_comment.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Comment ID is missing"
        )

    return CommentWithAuthor(
        id=created_comment.id,
        content=created_comment.content,
        author_id=created_comment.author_id,
        post_id=created_comment.post_id,
        created_at=str(created_comment.created_at),
        author_name=current_user.username,
    )


@router.get("/{post_id}/comments")
def get_post_comments(
    post_id: int,
    session: Session = session,
) -> list[CommentWithAuthor]:
    """Get all comments for a specific post."""
    # Check if post exists
    post = get_post_by_id(session, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    # Get comments with authors
    comments_with_authors = get_comments_with_authors(session, post_id)

    # Build response
    result: list[CommentWithAuthor] = []
    for comment, author in comments_with_authors:
        if not comment.id:
            continue

        result.append(
            CommentWithAuthor(
                id=comment.id,
                content=comment.content,
                author_id=comment.author_id,
                post_id=comment.post_id,
                created_at=str(comment.created_at),
                author_name=author.username,
            )
        )

    return result


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment_endpoint(
    comment_id: int,
    current_user: User = current_user,
    session: Session = session,
) -> None:
    """Delete a comment. Only the comment author or admin can delete. Requires authentication."""
    comment = get_comment_by_id(session, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    # Check if user is the author or an admin
    if comment.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments",
        )

    was_deleted = delete_comment(session, comment_id)
    if not was_deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete comment"
        )


@router.put("/comments/{comment_id}")
def update_comment_endpoint(
    comment_id: int,
    comment_data: CommentRequest,
    current_user: User = current_user,
    session: Session = session,
) -> CommentWithAuthor:
    """Update a comment's content. Only the comment author can update. Requires authentication."""
    comment = get_comment_by_id(session, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    # Check if user is the author
    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own comments",
        )

    updated_comment = update_comment(session, comment_id, comment_data.content)
    if not updated_comment:
        logger.error("Failed to update comment")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update comment"
        )

    if not updated_comment.id:
        logger.error("Comment ID is missing")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Comment ID is missing"
        )

    return CommentWithAuthor(
        id=updated_comment.id,
        content=updated_comment.content,
        author_id=updated_comment.author_id,
        post_id=updated_comment.post_id,
        created_at=str(updated_comment.created_at),
        author_name=current_user.username,
    )
