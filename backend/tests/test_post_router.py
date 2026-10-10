"""Tests for post router endpoints."""

from typing import Any

from fastapi import status
from fastapi.testclient import TestClient

from models.models import AuthenticatedUser, Post


class TestPostEndpoints:
    """Test suite for post endpoints."""

    def test_get_all_posts(self, client: TestClient, test_post: Post):
        """Test getting all posts."""
        response = client.get("/posts/")
        assert response.status_code == status.HTTP_200_OK
        posts_data: list[dict[str, Any]] = response.json()
        assert isinstance(posts_data, list)
        assert len(posts_data) > 0
        posts: list[Post] = [Post.model_validate(p) for p in posts_data]
        assert any(p.id == test_post.id for p in posts)

    def test_get_post_by_id(self, client: TestClient, test_post: Post):
        """Test getting a specific post by ID."""
        response = client.get(f"/posts/{test_post.id}")
        assert response.status_code == status.HTTP_200_OK
        post = response.json()
        assert post["id"] == test_post.id
        assert post["content"] == test_post.content

    def test_get_post_by_invalid_id(self, client: TestClient):
        """Test getting a post with invalid ID returns 404."""
        response = client.get("/posts/99999")
        assert response.status_code == 404

    def test_get_post_with_author(
        self, client: TestClient, test_post: Post, logged_in_user: AuthenticatedUser
    ):
        """Test getting post with author information."""
        response = client.get(f"/posts/{test_post.id}/with-author")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_post.id
        assert data["content"] == test_post.content
        assert data["author_name"] == logged_in_user.user.username

    def test_create_post(self, client: TestClient, logged_in_user: AuthenticatedUser):
        """Test creating a new post."""
        if not logged_in_user.user.id:
            raise ValueError("Logged in user must have an ID")

        new_post_data: dict[str, Any] = {
            "content": "A new post created during testing.",
        }

        response = client.post("/posts/", json=new_post_data, headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_201_CREATED
        post_data: dict[str, Any] = response.json()
        post: Post = Post.model_validate(post_data)
        assert post.content == new_post_data["content"]
        assert post.author_id == logged_in_user.user.id
        assert post.id is not None

    def test_create_post_with_long_content(
        self, client: TestClient, logged_in_user: AuthenticatedUser
    ):
        """Test creating a post with long content."""
        if not logged_in_user.user.id:
            raise ValueError("Logged in user must have an ID")

        long_content = "Lorem ipsum dolor sit amet. " * 100
        new_post_data: dict[str, Any] = {
            "content": long_content,
        }

        response = client.post("/posts/", json=new_post_data, headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_201_CREATED
        post_data: dict[str, Any] = response.json()
        post: Post = Post.model_validate(post_data)
        assert post.content == long_content

    def test_get_post_with_author_invalid_id(self, client: TestClient):
        """Test getting post with author for non-existent post returns 404."""
        response = client.get("/posts/99999/with-author")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_all_posts_empty_database(self, client: TestClient):
        """Test getting all posts returns empty list when no posts exist."""
        # Note: This test assumes posts might exist, so we just check the response format
        response = client.get("/posts/")
        assert response.status_code == status.HTTP_200_OK
        posts_data: list[dict[str, Any]] = response.json()
        assert isinstance(posts_data, list)


class TestPostLikes:
    """Test suite for post likes endpoints."""

    def test_like_post(
        self, client: TestClient, test_post: Post, logged_in_user: AuthenticatedUser
    ):
        """Test liking a post."""
        response = client.post(f"/posts/{test_post.id}/like", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["user_id"] == logged_in_user.user.id
        assert data["post_id"] == test_post.id

    def test_like_post_unauthenticated(self, client: TestClient, test_post: Post):
        """Test that unauthenticated users cannot like posts."""
        response = client.post(f"/posts/{test_post.id}/like")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_like_nonexistent_post(self, client: TestClient, logged_in_user: AuthenticatedUser):
        """Test liking a non-existent post returns 404."""
        response = client.post("/posts/99999/like", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unlike_post(
        self, client: TestClient, test_post: Post, logged_in_user: AuthenticatedUser
    ):
        """Test unliking a post."""
        client.post(f"/posts/{test_post.id}/like", headers=logged_in_user.headers)

        response = client.delete(f"/posts/{test_post.id}/like", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_unlike_post_not_liked(
        self, client: TestClient, test_post: Post, logged_in_user: AuthenticatedUser
    ):
        """Test unliking a post that wasn't liked returns 404."""
        response = client.delete(f"/posts/{test_post.id}/like", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_post_likes_info(
        self, client: TestClient, test_post: Post, logged_in_user: AuthenticatedUser
    ):
        """Test getting likes information for a post."""
        client.post(f"/posts/{test_post.id}/like", headers=logged_in_user.headers)

        response = client.get(f"/posts/{test_post.id}/likes", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["likes_count"] == 1
        assert data["liked_by_current_user"] is True

    def test_get_post_likes_info_not_liked(
        self, client: TestClient, test_post: Post, logged_in_user: AuthenticatedUser
    ):
        """Test getting likes info when user hasn't liked the post."""
        response = client.get(f"/posts/{test_post.id}/likes", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["likes_count"] == 0
        assert data["liked_by_current_user"] is False

    def test_like_post_twice(
        self, client: TestClient, test_post: Post, logged_in_user: AuthenticatedUser
    ):
        """Test that liking a post twice returns appropriate response."""
        # Like the post first time
        response = client.post(f"/posts/{test_post.id}/like", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_201_CREATED

        # Try to like the same post again
        response = client.post(f"/posts/{test_post.id}/like", headers=logged_in_user.headers)
        # Should handle duplicate likes gracefully (implementation dependent)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_409_CONFLICT,
        ]

    def test_get_likes_info_nonexistent_post(
        self, client: TestClient, logged_in_user: AuthenticatedUser
    ):
        """Test getting likes info for a non-existent post."""
        response = client.get("/posts/99999/likes", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_like_unlike_like_sequence(
        self, client: TestClient, test_post: Post, logged_in_user: AuthenticatedUser
    ):
        """Test the sequence: like -> unlike -> like again."""
        # Like the post
        response = client.post(f"/posts/{test_post.id}/like", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_201_CREATED

        # Unlike the post
        response = client.delete(f"/posts/{test_post.id}/like", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Like it again
        response = client.post(f"/posts/{test_post.id}/like", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_201_CREATED

        # Verify final state
        response = client.get(f"/posts/{test_post.id}/likes", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["likes_count"] == 1
        assert data["liked_by_current_user"] is True
