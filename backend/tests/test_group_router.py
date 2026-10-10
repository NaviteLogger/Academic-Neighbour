"""Tests for group router endpoints."""

from typing import Any

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from models.models import AuthenticatedUser, Group, GroupMember


class TestGroupEndpoints:
    """Test suite for group endpoints."""

    def test_create_group(self, client: TestClient, logged_in_user: AuthenticatedUser):
        """Test creating a new group."""
        response = client.post(
            "/groups/",
            json={"name": "Test Group", "description": "A test group"},
            headers=logged_in_user.headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Test Group"
        assert data["description"] == "A test group"
        assert data["creator_id"] == logged_in_user.user.id

    def test_get_groups(
        self, client: TestClient, session: Session, logged_in_user: AuthenticatedUser
    ):
        """Test listing all groups."""
        if not logged_in_user.user.id:
            raise ValueError("Logged in user must have an ID")

        # Create a group first
        group = Group(
            name="Test Group List",
            description="A test group",
            creator_id=logged_in_user.user.id,
        )
        session.add(group)
        session.commit()

        response = client.get("/groups/")
        assert response.status_code == status.HTTP_200_OK
        data: list[dict[str, Any]] = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # Check if our created group is in the list
        assert any(g["name"] == "Test Group List" for g in data)

    def test_get_group_details(
        self, client: TestClient, session: Session, logged_in_user: AuthenticatedUser
    ):
        """Test getting group details."""
        if not logged_in_user.user.id:
            raise ValueError("Logged in user must have an ID")

        group = Group(
            name="Test Group Details",
            description="A test group",
            creator_id=logged_in_user.user.id,
        )
        session.add(group)
        session.commit()

        response = client.get(f"/groups/{group.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test Group Details"

    def test_join_leave_group(
        self,
        client: TestClient,
        session: Session,
        logged_in_user: AuthenticatedUser,
        second_user: AuthenticatedUser,
    ):
        """Test joining and leaving a group."""
        if not logged_in_user.user.id:
            raise ValueError("Logged in user must have an ID")
        if not second_user.user.id:
            raise ValueError("Second user must have an ID")

        # User 1 creates group
        group = Group(
            name="Test Group Join",
            description="A test group",
            creator_id=logged_in_user.user.id,
        )
        session.add(group)
        session.commit()

        # User 2 joins
        response = client.post(
            f"/groups/{group.id}/join",
            headers=second_user.headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Successfully joined the group"

        # Verify membership
        members_response = client.get(f"/groups/{group.id}/members")
        assert members_response.status_code == status.HTTP_200_OK
        members = members_response.json()
        member_ids = [m["id"] for m in members]
        assert second_user.user.id in member_ids

        # User 2 leaves
        response = client.post(
            f"/groups/{group.id}/leave",
            headers=second_user.headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Successfully left the group"

    def test_group_posts(
        self, client: TestClient, session: Session, logged_in_user: AuthenticatedUser
    ):
        """Test creating and reading group posts."""
        if not logged_in_user.user.id:
            raise ValueError("Logged in user must have an ID")

        # Create group
        group = Group(
            name="Test Group Posts",
            description="A test group",
            creator_id=logged_in_user.user.id,
        )
        session.add(group)
        session.commit()

        # Add user as member (creator is not auto-added in this manual setup)
        member = GroupMember(group_id=group.id, user_id=logged_in_user.user.id)  # type: ignore
        session.add(member)
        session.commit()

        # Create post
        response = client.post(
            f"/groups/{group.id}/posts",
            json={"content": "Hello Group!"},
            headers=logged_in_user.headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["content"] == "Hello Group!"

        # Read posts
        response = client.get(f"/groups/{group.id}/posts")
        assert response.status_code == status.HTTP_200_OK
        posts: list[dict[str, Any]] = response.json()
        assert isinstance(posts, list)
        assert len(posts) == 1
        assert posts[0]["content"] == "Hello Group!"


class TestSampleGroupData:
    """Test suite for sample group data creation."""

    def test_sample_groups_created(self, session: Session):
        """Test that sample groups can be created (logic test, not startup data test)."""
        from sqlmodel import select

        from main import create_sample_groups, create_user_if_not_exists
        from models.models import Group, GroupMember, User, UserRole

        # Create the required users first (simulating startup)
        create_user_if_not_exists(
            session=session,
            username="testuser",
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            password="TestPassword123",
            is_active=True,
        )
        create_user_if_not_exists(
            session=session,
            username="testuser2",
            email="testuser2@example.com",
            first_name="Test2",
            last_name="User2",
            password="TestPassword123",
            is_active=True,
        )
        create_user_if_not_exists(
            session=session,
            username="admin",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            password="AdminPassword123",
            role=UserRole.ADMIN,
            is_active=True,
        )

        # Create sample groups for testing (simulating what happens at startup)
        create_sample_groups(session)

        # Check that sample groups exist
        groups = session.exec(select(Group)).all()
        assert len(groups) >= 5, "At least 5 sample groups should be created"

        # Check specific groups
        cs_group = session.exec(
            select(Group).where(Group.name == "Koło Naukowe Informatyki")
        ).first()
        assert cs_group is not None, "Koło Naukowe Informatyki should exist"
        assert "studentów informatyki" in cs_group.description

        dorm_group = session.exec(select(Group).where(Group.name == "Społeczność Piętro 3")).first()
        assert dorm_group is not None, "Społeczność Piętro 3 should exist"

        movie_group = session.exec(select(Group).where(Group.name == "Klub Filmowy")).first()
        assert movie_group is not None, "Klub Filmowy should exist"

        # Check that groups have members
        if cs_group and cs_group.id:
            cs_members = session.exec(
                select(GroupMember).where(GroupMember.group_id == cs_group.id)
            ).all()
            assert len(cs_members) >= 4, "Koło Naukowe Informatyki should have at least 4 members"

        # Check that new users were created
        alice = session.exec(select(User).where(User.username == "alice")).first()
        assert alice is not None, "User 'alice' should be created"
        assert alice.first_name == "Alice"
        assert alice.last_name == "Johnson"

        bob = session.exec(select(User).where(User.username == "bob")).first()
        assert bob is not None, "User 'bob' should be created"

        charlie = session.exec(select(User).where(User.username == "charlie")).first()
        assert charlie is not None, "User 'charlie' should be created"
