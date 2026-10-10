from sqlmodel import Session

from models.models import Comment, Post, User
from repositories.comment_repo import (
    create_comment,
    delete_comment,
    get_comment_by_id,
    get_comment_with_author,
    get_comments_by_post,
    get_comments_with_authors,
    update_comment,
)
from services.security import get_password_hash


class TestCommentRepository:
    """Tests for comment repository functions."""

    def test_create_comment(self, session: Session):
        """Test creating a new comment."""
        user = User(
            email="commenter@example.com",
            username="commenter",
            first_name="Comment",
            last_name="Author",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        post = Post(content="Post to comment on", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")

        comment = Comment(content="Test comment content", author_id=user.id, post_id=post.id)

        created_comment = create_comment(session, comment)

        assert created_comment is not None
        assert created_comment.id is not None
        assert created_comment.content == "Test comment content"
        assert created_comment.author_id == user.id
        assert created_comment.post_id == post.id
        assert created_comment.created_at is not None

    def test_get_comments_by_post_empty(self, session: Session):
        """Test getting comments for a post with no comments."""
        user = User(
            email="nocomments@example.com",
            username="nocomments",
            first_name="No",
            last_name="Comments",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        post = Post(content="Post with no comments", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")

        comments = get_comments_by_post(session, post.id)

        assert comments == []
        assert len(comments) == 0

    def test_get_comments_by_post_with_data(self, session: Session):
        """Test getting comments for a post with multiple comments."""
        user = User(
            email="multicomment@example.com",
            username="multicomment",
            first_name="Multi",
            last_name="Comment",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        post = Post(content="Post with comments", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")

        comment1 = Comment(content="First comment", author_id=user.id, post_id=post.id)
        comment2 = Comment(content="Second comment", author_id=user.id, post_id=post.id)
        comment3 = Comment(content="Third comment", author_id=user.id, post_id=post.id)

        session.add(comment1)
        session.add(comment2)
        session.add(comment3)
        session.commit()

        comments = get_comments_by_post(session, post.id)

        assert len(comments) == 3
        contents = {c.content for c in comments}
        assert "First comment" in contents
        assert "Second comment" in contents
        assert "Third comment" in contents

    def test_get_comments_by_post_ordered_by_newest(self, session: Session):
        """Test that comments are ordered by newest first."""
        user = User(
            email="ordercomment@example.com",
            username="ordercomment",
            first_name="Order",
            last_name="Comment",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        post = Post(content="Post for order test", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")

        comment1 = Comment(content="Oldest comment", author_id=user.id, post_id=post.id)
        session.add(comment1)
        session.commit()

        comment2 = Comment(content="Middle comment", author_id=user.id, post_id=post.id)
        session.add(comment2)
        session.commit()

        comment3 = Comment(content="Newest comment", author_id=user.id, post_id=post.id)
        session.add(comment3)
        session.commit()

        comments = get_comments_by_post(session, post.id)

        assert len(comments) == 3
        assert comments[0].content == "Newest comment"
        assert comments[2].content == "Oldest comment"

    def test_get_comment_by_id_exists(self, session: Session):
        """Test getting a comment by ID when it exists."""
        user = User(
            email="singlecomment@example.com",
            username="singlecomment",
            first_name="Single",
            last_name="Comment",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        post = Post(content="Post for ID test", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")

        comment = Comment(content="Specific comment", author_id=user.id, post_id=post.id)
        session.add(comment)
        session.commit()
        session.refresh(comment)

        if not comment.id:
            raise ValueError("Comment must have an ID")

        found_comment = get_comment_by_id(session, comment.id)

        assert found_comment is not None
        assert found_comment.id == comment.id
        assert found_comment.content == "Specific comment"

    def test_get_comment_by_id_not_exists(self, session: Session):
        """Test getting a comment by ID when it doesn't exist."""
        found_comment = get_comment_by_id(session, 99999)

        assert found_comment is None

    def test_get_comment_with_author_exists(self, session: Session):
        """Test getting a comment with author information."""
        user = User(
            email="authorcomment@example.com",
            username="authorcomment",
            first_name="Author",
            last_name="Comment",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        post = Post(content="Post with author", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")

        comment = Comment(content="Comment with author", author_id=user.id, post_id=post.id)
        session.add(comment)
        session.commit()
        session.refresh(comment)

        if not comment.id:
            raise ValueError("Comment must have an ID")

        result = get_comment_with_author(session, comment.id)

        assert result is not None
        comment_result, author_result = result
        assert comment_result.id == comment.id
        assert comment_result.content == "Comment with author"
        assert author_result.id == user.id
        assert author_result.username == "authorcomment"

    def test_get_comment_with_author_not_exists(self, session: Session):
        """Test getting comment with author when comment doesn't exist."""
        result = get_comment_with_author(session, 99999)

        assert result is None

    def test_get_comments_with_authors(self, session: Session):
        """Test getting all comments with authors for a post."""
        user1 = User(
            email="multiauthor1@example.com",
            username="multiauthor1",
            first_name="Author",
            last_name="One",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        user2 = User(
            email="multiauthor2@example.com",
            username="multiauthor2",
            first_name="Author",
            last_name="Two",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        if not user1.id:
            raise ValueError("User1 must have an ID")

        post = Post(content="Post with multiple authors", author_id=user1.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")
        if not user2.id:
            raise ValueError("User2 must have an ID")

        comment1 = Comment(content="Comment from user1", author_id=user1.id, post_id=post.id)
        comment2 = Comment(content="Comment from user2", author_id=user2.id, post_id=post.id)
        session.add(comment1)
        session.add(comment2)
        session.commit()

        results = get_comments_with_authors(session, post.id)

        assert len(results) == 2
        usernames = {author.username for _, author in results}
        assert "multiauthor1" in usernames
        assert "multiauthor2" in usernames

    def test_delete_comment_exists(self, session: Session):
        """Test deleting a comment that exists."""
        user = User(
            email="deletecomment@example.com",
            username="deletecomment",
            first_name="Delete",
            last_name="Comment",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        post = Post(content="Post to delete comment from", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")

        comment = Comment(content="Comment to delete", author_id=user.id, post_id=post.id)
        session.add(comment)
        session.commit()
        session.refresh(comment)

        if not comment.id:
            raise ValueError("Comment must have an ID")

        result = delete_comment(session, comment.id)

        assert result is True
        deleted = get_comment_by_id(session, comment.id)
        assert deleted is None

    def test_delete_comment_not_exists(self, session: Session):
        """Test deleting a comment that doesn't exist."""
        result = delete_comment(session, 99999)

        assert result is False

    def test_update_comment_exists(self, session: Session):
        """Test updating a comment that exists."""
        user = User(
            email="updatecomment@example.com",
            username="updatecomment",
            first_name="Update",
            last_name="Comment",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        post = Post(content="Post to update comment in", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")

        comment = Comment(content="Original content", author_id=user.id, post_id=post.id)
        session.add(comment)
        session.commit()
        session.refresh(comment)

        if not comment.id:
            raise ValueError("Comment must have an ID")

        updated_comment = update_comment(session, comment.id, "Updated content")

        assert updated_comment is not None
        assert updated_comment.id == comment.id
        assert updated_comment.content == "Updated content"

    def test_update_comment_not_exists(self, session: Session):
        """Test updating a comment that doesn't exist."""
        result = update_comment(session, 99999, "New content")

        assert result is None

    def test_update_comment_to_empty_string(self, session: Session):
        """Test updating a comment to empty string."""
        user = User(
            email="emptyupdate@example.com",
            username="emptyupdate",
            first_name="Empty",
            last_name="Update",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        post = Post(content="Post for empty update", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")

        comment = Comment(content="Original content", author_id=user.id, post_id=post.id)
        session.add(comment)
        session.commit()
        session.refresh(comment)

        if not comment.id:
            raise ValueError("Comment must have an ID")

        updated_comment = update_comment(session, comment.id, "")

        assert updated_comment is not None
        assert updated_comment.content == ""
