from sqlmodel import Session

from models.models import Post, User
from repositories.post_repo import (
    create_post,
    get_all_posts,
    get_post_by_id,
    get_post_likes_count,
    get_post_with_author,
    is_post_liked_by_user,
    like_post,
    unlike_post,
)
from services.security import get_password_hash


class TestPostRepository:
    """Tests for post repository functions."""

    def test_create_post(self, session: Session):
        """Test creating a new post."""
        user = User(
            email="poster@example.com",
            username="poster",
            first_name="Post",
            last_name="Author",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        post = Post(content="Test post content", author_id=user.id)

        created_post = create_post(session, post)

        assert created_post is not None
        assert created_post.id is not None
        assert created_post.content == "Test post content"
        assert created_post.author_id == user.id
        assert created_post.created_at is not None

    def test_get_all_posts_empty(self, session: Session):
        """Test getting all posts when database is empty."""
        posts = get_all_posts(session)

        assert posts == []
        assert len(posts) == 0

    def test_get_all_posts_with_data(self, session: Session):
        """Test getting all posts when posts exist."""
        user = User(
            email="multiposter@example.com",
            username="multiposter",
            first_name="Multi",
            last_name="Poster",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        post1 = Post(content="First post", author_id=user.id)
        post2 = Post(content="Second post", author_id=user.id)
        post3 = Post(content="Third post", author_id=user.id)

        session.add(post1)
        session.add(post2)
        session.add(post3)
        session.commit()

        posts = get_all_posts(session)

        assert len(posts) == 3
        assert any(p.content == "First post" for p in posts)
        assert any(p.content == "Second post" for p in posts)
        assert any(p.content == "Third post" for p in posts)

    def test_get_all_posts_ordered_by_newest(self, session: Session):
        """Test that posts are ordered by newest first."""
        user = User(
            email="orderposter@example.com",
            username="orderposter",
            first_name="Order",
            last_name="Poster",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        post1 = Post(content="Oldest post", author_id=user.id)
        session.add(post1)
        session.commit()

        post2 = Post(content="Middle post", author_id=user.id)
        session.add(post2)
        session.commit()

        post3 = Post(content="Newest post", author_id=user.id)
        session.add(post3)
        session.commit()

        posts = get_all_posts(session)

        assert len(posts) == 3
        assert posts[0].content == "Newest post"
        assert posts[2].content == "Oldest post"

    def test_get_post_by_id_exists(self, session: Session):
        """Test getting a post by ID when it exists."""
        user = User(
            email="singlepost@example.com",
            username="singlepost",
            first_name="Single",
            last_name="Post",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        post = Post(content="Specific post", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")

        found_post = get_post_by_id(session, post.id)

        assert found_post is not None
        assert found_post.id == post.id
        assert found_post.content == "Specific post"

    def test_get_post_by_id_not_exists(self, session: Session):
        """Test getting a post by ID when it doesn't exist."""
        found_post = get_post_by_id(session, 99999)

        assert found_post is None

    def test_get_post_with_author_exists(self, session: Session):
        """Test getting a post with author information."""
        user = User(
            email="authortest@example.com",
            username="authortest",
            first_name="Author",
            last_name="Test",
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

        result = get_post_with_author(session, post.id)

        assert result is not None
        post_result, author_result = result
        assert post_result.id == post.id
        assert post_result.content == "Post with author"
        assert author_result.id == user.id
        assert author_result.username == "authortest"

    def test_get_post_with_author_post_not_exists(self, session: Session):
        """Test getting post with author when post doesn't exist."""
        result = get_post_with_author(session, 99999)

        assert result is None

    def test_like_post(self, session: Session):
        """Test liking a post."""
        user = User(
            email="liker@example.com",
            username="liker",
            first_name="Liker",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        post = Post(content="Post to like", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")

        like = like_post(session, user.id, post.id)

        assert like is not None
        assert like.user_id == user.id
        assert like.post_id == post.id

    def test_like_post_twice(self, session: Session):
        """Test that liking a post twice returns the existing like."""
        user = User(
            email="doubleliker@example.com",
            username="doubleliker",
            first_name="Double",
            last_name="Liker",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        post = Post(content="Post to like twice", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")

        first_like = like_post(session, user.id, post.id)
        second_like = like_post(session, user.id, post.id)

        assert first_like.id == second_like.id

    def test_unlike_post_exists(self, session: Session):
        """Test unliking a post that is liked."""
        user = User(
            email="unliker@example.com",
            username="unliker",
            first_name="Unliker",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        post = Post(content="Post to unlike", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")

        like_post(session, user.id, post.id)
        result = unlike_post(session, user.id, post.id)

        assert result is True

    def test_unlike_post_not_liked(self, session: Session):
        """Test unliking a post that is not liked."""
        user = User(
            email="notliker@example.com",
            username="notliker",
            first_name="NotLiker",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        post = Post(content="Post not liked", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")

        result = unlike_post(session, user.id, post.id)

        assert result is False

    def test_get_post_likes_count_no_likes(self, session: Session):
        """Test getting likes count for a post with no likes."""
        user = User(
            email="nolikes@example.com",
            username="nolikes",
            first_name="NoLikes",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        post = Post(content="Post with no likes", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")

        count = get_post_likes_count(session, post.id)

        assert count == 0

    def test_get_post_likes_count_with_likes(self, session: Session):
        """Test getting likes count for a post with multiple likes."""
        user1 = User(
            email="likecounter1@example.com",
            username="likecounter1",
            first_name="Counter",
            last_name="One",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        user2 = User(
            email="likecounter2@example.com",
            username="likecounter2",
            first_name="Counter",
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

        post = Post(content="Popular post", author_id=user1.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")
        if not user2.id:
            raise ValueError("User2 must have an ID")

        like_post(session, user1.id, post.id)
        like_post(session, user2.id, post.id)

        count = get_post_likes_count(session, post.id)

        assert count == 2

    def test_is_post_liked_by_user_true(self, session: Session):
        """Test checking if user liked a post (true case)."""
        user = User(
            email="checklike@example.com",
            username="checklike",
            first_name="Check",
            last_name="Like",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        post = Post(content="Liked post", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")

        like_post(session, user.id, post.id)
        is_liked = is_post_liked_by_user(session, user.id, post.id)

        assert is_liked is True

    def test_is_post_liked_by_user_false(self, session: Session):
        """Test checking if user liked a post (false case)."""
        user = User(
            email="checknotlike@example.com",
            username="checknotlike",
            first_name="CheckNot",
            last_name="Like",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        post = Post(content="Not liked post", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        if not post.id:
            raise ValueError("Post must have an ID")

        is_liked = is_post_liked_by_user(session, user.id, post.id)

        assert is_liked is False
