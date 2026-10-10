from typing import Any

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from models.models import AuthenticatedUser, Comment, Post, User
from services.security import get_password_hash


class TestCommentCreation:
    """Tests for creating comments on posts."""

    def test_create_comment_success(
        self, client: TestClient, session: Session, logged_in_user: AuthenticatedUser
    ):
        """Test creating a comment successfully."""
        if not logged_in_user.user.id:
            raise ValueError("Logged in user must have an ID")
        post = Post(
            content="This is a test post for commenting",
            author_id=logged_in_user.user.id,
        )
        session.add(post)
        session.commit()
        session.refresh(post)

        comment_data: dict[str, Any] = {"content": "This is a test comment"}

        response = client.post(
            f"/posts/{post.id}/comments",
            json=comment_data,
            headers=logged_in_user.headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data: dict[str, Any] = response.json()
        assert data["content"] == "This is a test comment"
        assert data["author_id"] == logged_in_user.user.id
        assert data["post_id"] == post.id
        assert data["author_name"] == logged_in_user.user.username
        assert "id" in data
        assert "created_at" in data

    def test_create_comment_on_nonexistent_post(
        self, client: TestClient, logged_in_user: AuthenticatedUser
    ):
        """Test creating a comment on a post that doesn't exist."""
        comment_data: dict[str, Any] = {"content": "Comment on nonexistent post"}

        response = client.post(
            "/posts/99999/comments",
            json=comment_data,
            headers=logged_in_user.headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data: dict[str, Any] = response.json()
        assert data["detail"] == "Post not found"

    def test_create_comment_unauthenticated(self, client: TestClient, session: Session):
        """Test that creating a comment requires authentication."""
        user = User(
            email="poster@example.com",
            username="poster",
            first_name="Post",
            last_name="Author",
            hashed_password=get_password_hash("testpassword"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")
        post = Post(content="Test post", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        comment_data: dict[str, Any] = {"content": "Unauthorized comment"}

        response = client.post(f"/posts/{post.id}/comments", json=comment_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_comment_empty_content(
        self, client: TestClient, session: Session, logged_in_user: AuthenticatedUser
    ):
        """Test creating a comment with empty content."""
        if not logged_in_user.user.id:
            raise ValueError("Logged in user must have an ID")
        post = Post(
            content="Test post for empty comment",
            author_id=logged_in_user.user.id,
        )
        session.add(post)
        session.commit()
        session.refresh(post)

        comment_data: dict[str, Any] = {"content": ""}

        response = client.post(
            f"/posts/{post.id}/comments",
            json=comment_data,
            headers=logged_in_user.headers,
        )

        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        ]

    def test_create_comment_with_long_content(
        self, client: TestClient, session: Session, logged_in_user: AuthenticatedUser
    ):
        """Test creating a comment with very long content."""
        if not logged_in_user.user.id:
            raise ValueError("Logged in user must have an ID")
        post = Post(
            content="Test post for long comment",
            author_id=logged_in_user.user.id,
        )
        session.add(post)
        session.commit()
        session.refresh(post)

        long_content = "This is a very long comment. " * 50

        comment_data: dict[str, Any] = {"content": long_content}

        response = client.post(
            f"/posts/{post.id}/comments",
            json=comment_data,
            headers=logged_in_user.headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data: dict[str, Any] = response.json()
        assert data["content"] == long_content


class TestCommentRetrieval:
    """Tests for retrieving comments from posts."""

    def test_get_comments_empty_post(self, client: TestClient, session: Session):
        """Test getting comments for a post with no comments."""
        user = User(
            email="nocomments@example.com",
            username="nocomments",
            first_name="No",
            last_name="Comments",
            hashed_password=get_password_hash("testpassword"),
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

        response = client.get(f"/posts/{post.id}/comments")

        assert response.status_code == status.HTTP_200_OK
        data: list[dict[str, Any]] = response.json()
        assert len(data) == 0
        assert data == []

    def test_get_comments_with_data(
        self, client: TestClient, session: Session, logged_in_user: AuthenticatedUser
    ):
        """Test getting comments for a post that has comments."""
        if not logged_in_user.user.id:
            raise ValueError("Logged in user must have an ID")
        post = Post(
            content="Post with comments",
            author_id=logged_in_user.user.id,
        )
        session.add(post)
        session.commit()
        session.refresh(post)

        if not logged_in_user.user.id:
            raise ValueError("Logged in user must have an ID")
        if not post.id:
            raise ValueError("Post must have an ID")
        comment1 = Comment(
            content="First comment",
            author_id=logged_in_user.user.id,
            post_id=post.id,
        )
        comment2 = Comment(
            content="Second comment",
            author_id=logged_in_user.user.id,
            post_id=post.id,
        )
        session.add(comment1)
        session.add(comment2)
        session.commit()

        response = client.get(f"/posts/{post.id}/comments")

        assert response.status_code == status.HTTP_200_OK
        data: list[dict[str, Any]] = response.json()
        assert len(data) == 2
        contents = {comment["content"] for comment in data}
        assert "First comment" in contents
        assert "Second comment" in contents
        assert all(comment["author_name"] == logged_in_user.user.username for comment in data)
        assert all("created_at" in comment for comment in data)
        assert all("id" in comment for comment in data)

    def test_get_comments_nonexistent_post(self, client: TestClient):
        """Test getting comments for a post that doesn't exist."""
        response = client.get("/posts/99999/comments")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data: dict[str, Any] = response.json()
        assert data["detail"] == "Post not found"

    def test_get_comments_multiple_authors(
        self, client: TestClient, session: Session, logged_in_user: AuthenticatedUser
    ):
        """Test getting comments from multiple authors."""
        other_user = User(
            email="otherguy@example.com",
            username="otherguy",
            first_name="Other",
            last_name="Guy",
            hashed_password=get_password_hash("testpassword"),
            is_active=True,
        )
        session.add(other_user)
        session.commit()
        session.refresh(other_user)

        if not logged_in_user.user.id:
            raise ValueError("Logged in user must have an ID")
        post = Post(
            content="Post with multi-author comments",
            author_id=logged_in_user.user.id,
        )
        session.add(post)
        session.commit()
        session.refresh(post)

        if not logged_in_user.user.id:
            raise ValueError("Logged in user must have an ID")
        if not post.id:
            raise ValueError("Post must have an ID")
        if not other_user.id:
            raise ValueError("Other user must have an ID")
        comment1 = Comment(
            content="Comment from first user",
            author_id=logged_in_user.user.id,
            post_id=post.id,
        )
        comment2 = Comment(
            content="Comment from second user",
            author_id=other_user.id,
            post_id=post.id,
        )
        session.add(comment1)
        session.add(comment2)
        session.commit()

        response = client.get(f"/posts/{post.id}/comments")

        assert response.status_code == status.HTTP_200_OK
        data: list[dict[str, Any]] = response.json()
        assert len(data) == 2
        author_names = {comment["author_name"] for comment in data}
        assert logged_in_user.user.username in author_names
        assert other_user.username in author_names


class TestCommentUpdate:
    """Tests for updating comments."""

    def test_update_comment_success(
        self, client: TestClient, session: Session, logged_in_user: AuthenticatedUser
    ):
        """Test updating a comment successfully."""
        if not logged_in_user.user.id:
            raise ValueError("Logged in user must have an ID")
        post = Post(
            content="Post for update test",
            author_id=logged_in_user.user.id,
        )
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")
        comment = Comment(
            content="Original comment content",
            author_id=logged_in_user.user.id,
            post_id=post.id,
        )
        session.add(comment)
        session.commit()
        session.refresh(comment)

        update_data: dict[str, Any] = {"content": "Updated comment content"}

        response = client.put(
            f"/posts/comments/{comment.id}",
            json=update_data,
            headers=logged_in_user.headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data: dict[str, Any] = response.json()
        assert data["content"] == "Updated comment content"
        assert data["id"] == comment.id
        assert data["author_id"] == logged_in_user.user.id

    def test_update_comment_not_author(
        self, client: TestClient, session: Session, logged_in_user: AuthenticatedUser
    ):
        """Test that non-author cannot update comment."""
        other_user = User(
            email="otherauthor@example.com",
            username="otherauthor",
            first_name="Other",
            last_name="Author",
            hashed_password=get_password_hash("testpassword"),
            is_active=True,
        )
        session.add(other_user)
        session.commit()
        session.refresh(other_user)

        if not other_user.id:
            raise ValueError("Other user must have an ID")
        post = Post(content="Post by other user", author_id=other_user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")
        comment = Comment(
            content="Comment by other user",
            author_id=other_user.id,
            post_id=post.id,
        )
        session.add(comment)
        session.commit()
        session.refresh(comment)

        update_data: dict[str, Any] = {"content": "Trying to update others comment"}

        response = client.put(
            f"/posts/comments/{comment.id}",
            json=update_data,
            headers=logged_in_user.headers,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data: dict[str, Any] = response.json()
        assert "only edit your own comments" in data["detail"].lower()

    def test_update_nonexistent_comment(
        self, client: TestClient, logged_in_user: AuthenticatedUser
    ):
        """Test updating a comment that doesn't exist."""
        update_data: dict[str, Any] = {"content": "Update nonexistent comment"}

        response = client.put(
            "/posts/comments/99999",
            json=update_data,
            headers=logged_in_user.headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data: dict[str, Any] = response.json()
        assert data["detail"] == "Comment not found"

    def test_update_comment_unauthenticated(self, client: TestClient, session: Session):
        """Test that updating a comment requires authentication."""
        user = User(
            email="commentowner@example.com",
            username="commentowner",
            first_name="Comment",
            last_name="Owner",
            hashed_password=get_password_hash("testpassword"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")
        post = Post(content="Test post", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")
        comment = Comment(
            content="Original content",
            author_id=user.id,
            post_id=post.id,
        )
        session.add(comment)
        session.commit()
        session.refresh(comment)

        update_data: dict[str, Any] = {"content": "Updated without auth"}

        response = client.put(f"/posts/comments/{comment.id}", json=update_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_comment_empty_content(
        self, client: TestClient, session: Session, logged_in_user: AuthenticatedUser
    ):
        """Test updating a comment with empty content."""
        if not logged_in_user.user.id:
            raise ValueError("Logged in user must have an ID")
        post = Post(
            content="Post for empty update test",
            author_id=logged_in_user.user.id,
        )
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")
        comment = Comment(
            content="Original content",
            author_id=logged_in_user.user.id,
            post_id=post.id,
        )
        session.add(comment)
        session.commit()
        session.refresh(comment)

        update_data: dict[str, Any] = {"content": ""}

        response = client.put(
            f"/posts/comments/{comment.id}",
            json=update_data,
            headers=logged_in_user.headers,
        )

        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        ]


class TestCommentDeletion:
    """Tests for deleting comments."""

    def test_delete_comment_by_author(
        self, client: TestClient, session: Session, logged_in_user: AuthenticatedUser
    ):
        """Test deleting a comment by its author."""
        if not logged_in_user.user.id:
            raise ValueError("Logged in user must have an ID")
        post = Post(
            content="Post for delete test",
            author_id=logged_in_user.user.id,
        )
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")
        comment = Comment(
            content="Comment to delete",
            author_id=logged_in_user.user.id,
            post_id=post.id,
        )
        session.add(comment)
        session.commit()
        session.refresh(comment)

        response = client.delete(
            f"/posts/comments/{comment.id}",
            headers=logged_in_user.headers,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        verify_response = client.get(f"/posts/{post.id}/comments")
        comments: list[dict[str, Any]] = verify_response.json()
        assert len(comments) == 0

    def test_delete_comment_by_admin(
        self, client: TestClient, session: Session, logged_in_admin: AuthenticatedUser
    ):
        """Test that admin can delete any comment."""
        user = User(
            email="regularuser@example.com",
            username="regularuser",
            first_name="Regular",
            last_name="User",
            hashed_password=get_password_hash("testpassword"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")
        post = Post(content="Post by regular user", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")
        comment = Comment(
            content="Comment by regular user",
            author_id=user.id,
            post_id=post.id,
        )
        session.add(comment)
        session.commit()
        session.refresh(comment)

        response = client.delete(
            f"/posts/comments/{comment.id}",
            headers=logged_in_admin.headers,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_comment_by_non_author_non_admin(
        self, client: TestClient, session: Session, logged_in_user: AuthenticatedUser
    ):
        """Test that non-author non-admin cannot delete comment."""
        other_user = User(
            email="otherperson@example.com",
            username="otherperson",
            first_name="Other",
            last_name="Person",
            hashed_password=get_password_hash("testpassword"),
            is_active=True,
        )
        session.add(other_user)
        session.commit()
        session.refresh(other_user)

        if not other_user.id:
            raise ValueError("Other user must have an ID")
        post = Post(content="Someone elses post", author_id=other_user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")
        comment = Comment(
            content="Someone elses comment",
            author_id=other_user.id,
            post_id=post.id,
        )
        session.add(comment)
        session.commit()
        session.refresh(comment)

        response = client.delete(
            f"/posts/comments/{comment.id}",
            headers=logged_in_user.headers,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data: dict[str, Any] = response.json()
        assert "only delete your own comments" in data["detail"].lower()

    def test_delete_nonexistent_comment(
        self, client: TestClient, logged_in_user: AuthenticatedUser
    ):
        """Test deleting a comment that doesn't exist."""
        response = client.delete(
            "/posts/comments/99999",
            headers=logged_in_user.headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data: dict[str, Any] = response.json()
        assert data["detail"] == "Comment not found"

    def test_delete_comment_unauthenticated(self, client: TestClient, session: Session):
        """Test that deleting a comment requires authentication."""
        user = User(
            email="deletetest@example.com",
            username="deletetest",
            first_name="Delete",
            last_name="Test",
            hashed_password=get_password_hash("testpassword"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")
        post = Post(content="Test post", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")
        comment = Comment(
            content="Comment to delete",
            author_id=user.id,
            post_id=post.id,
        )
        session.add(comment)
        session.commit()
        session.refresh(comment)

        response = client.delete(f"/posts/comments/{comment.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
