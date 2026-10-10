"""Performance and concurrent operations tests."""

import time

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from models.models import Post, User
from services.security import get_password_hash


class TestPerformance:
    """Performance tests for API endpoints."""

    def test_post_list_performance(self, client: TestClient, session: Session):
        """Test performance of listing posts with many records."""
        user = User(
            email="perftest@example.com",
            username="perftest",
            first_name="Perf",
            last_name="Test",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have ID")

        for i in range(100):
            post = Post(content=f"Performance test post {i}", author_id=user.id)
            session.add(post)
        session.commit()

        start_time = time.time()
        response = client.get("/posts/")
        end_time = time.time()

        assert response.status_code == 200
        duration = end_time - start_time
        assert duration < 2.0, f"Post listing took {duration:.2f}s, expected < 2s"

    def test_authentication_performance(self, client: TestClient, session: Session):
        """Test authentication endpoint performance."""
        user = User(
            email="authperf@example.com",
            username="authperf",
            first_name="Auth",
            last_name="Perf",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()

        start_time = time.time()
        response = client.post(
            "/auth/token", data={"username": "authperf", "password": "password123"}
        )
        end_time = time.time()

        assert response.status_code == 200
        duration = end_time - start_time
        assert duration < 1.0, f"Authentication took {duration:.2f}s, expected < 1s"

    def test_multiple_sequential_requests(self, client: TestClient, session: Session):
        """Test performance of multiple sequential requests."""
        user = User(
            email="seqtest@example.com",
            username="seqtest",
            first_name="Seq",
            last_name="Test",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have ID")

        post = Post(content="Sequential test post", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)

        start_time = time.time()
        for _ in range(20):
            response = client.get(f"/posts/{post.id}")
            assert response.status_code == 200
        end_time = time.time()

        duration = end_time - start_time
        avg_duration = duration / 20
        assert avg_duration < 0.1, f"Average request took {avg_duration:.3f}s, expected < 0.1s"


class TestStressTests:
    """Stress tests for system limits."""

    @pytest.mark.slow
    def test_many_posts_retrieval(self, client: TestClient, session: Session):
        """Test retrieving large number of posts."""
        user = User(
            email="stresstest@example.com",
            username="stresstest",
            first_name="Stress",
            last_name="Test",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have ID")

        for i in range(500):
            post = Post(content=f"Stress test post {i}", author_id=user.id)
            session.add(post)
            if i % 100 == 0:
                session.commit()
        session.commit()

        response = client.get("/posts/")
        assert response.status_code == 200
        posts = response.json()
        assert len(posts) == 500

    @pytest.mark.slow
    def test_rapid_sequential_requests(self, client: TestClient, session: Session):
        """Test rapid sequential requests."""
        user = User(
            email="rapidtest@example.com",
            username="rapidtest",
            first_name="Rapid",
            last_name="Test",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()

        login = client.post(
            "/auth/token", data={"username": "rapidtest", "password": "password123"}
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        success_count = 0
        for _ in range(100):
            response = client.get("/users/me", headers=headers)
            if response.status_code == 200:
                success_count += 1

        assert success_count >= 95
