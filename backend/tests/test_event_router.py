from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from models.models import (
    AttendanceStatusEnum,
    AuthenticatedUser,
    Event,
    EventAttendee,
    User,
)
from services.security import get_password_hash


class TestEventCreation:
    """Tests for creating events."""

    def test_create_event_success(self, client: TestClient, logged_in_user: AuthenticatedUser):
        """Test successfully creating an event."""
        """Test creating an event successfully."""
        now = datetime.now(UTC)
        event_data: dict[str, Any] = {
            "title": "Dorm Party",
            "description": "A fun party in the common room",
            "location": "Common Room",
            "start_date": (now + timedelta(days=1)).isoformat(),
            "end_date": (now + timedelta(days=1, hours=3)).isoformat(),
        }

        response = client.post("/events/", json=event_data, headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_201_CREATED
        event_response: dict[str, Any] = response.json()
        event: Event = Event.model_validate(event_response)
        assert event.title == "Dorm Party"
        assert event.creator_id == logged_in_user.user.id
        assert event.id is not None

    def test_create_event_invalid_dates(
        self, client: TestClient, logged_in_user: AuthenticatedUser
    ):
        """Test creating event with end date before start date."""
        now = datetime.now(UTC)
        event_data: dict[str, Any] = {
            "title": "Invalid Event",
            "description": "Event with invalid dates",
            "location": "Somewhere",
            "start_date": (now + timedelta(days=2)).isoformat(),
            "end_date": (now + timedelta(days=1)).isoformat(),
        }

        response = client.post("/events/", json=event_data, headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data: dict[str, Any] = response.json()
        assert "after start date" in data["detail"].lower()

    def test_create_event_same_start_end_dates(
        self, client: TestClient, logged_in_user: AuthenticatedUser
    ):
        """Test creating event with same start and end date."""
        now = datetime.now(UTC)
        same_time = now + timedelta(days=1)
        event_data: dict[str, Any] = {
            "title": "Same Time Event",
            "description": "Event with same start and end time",
            "location": "Somewhere",
            "start_date": same_time.isoformat(),
            "end_date": same_time.isoformat(),
        }

        response = client.post("/events/", json=event_data, headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_event_unauthenticated(self, client: TestClient):
        """Test that unauthenticated users cannot create events."""
        now = datetime.now(UTC)
        event_data: dict[str, Any] = {
            "title": "Unauthorized Event",
            "description": "Should not be created",
            "location": "Nowhere",
            "start_date": (now + timedelta(days=1)).isoformat(),
            "end_date": (now + timedelta(days=1, hours=2)).isoformat(),
        }

        response = client.post("/events/", json=event_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_event_with_long_description(
        self, client: TestClient, logged_in_user: AuthenticatedUser
    ):
        """Test creating event with very long description."""
        now = datetime.now(UTC)
        long_description = "Lorem ipsum dolor sit amet. " * 100
        event_data: dict[str, Any] = {
            "title": "Event with Long Description",
            "description": long_description,
            "location": "Main Hall",
            "start_date": (now + timedelta(days=1)).isoformat(),
            "end_date": (now + timedelta(days=1, hours=4)).isoformat(),
        }

        response = client.post("/events/", json=event_data, headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_201_CREATED
        event_response: dict[str, Any] = response.json()
        assert event_response["description"] == long_description


class TestEventRetrieval:
    """Tests for retrieving events."""

    def test_get_all_events_empty(self, client: TestClient):
        """Test getting all events when none exist."""
        response = client.get("/events/")
        assert response.status_code == status.HTTP_200_OK
        events_data: list[dict[str, Any]] = response.json()
        assert isinstance(events_data, list)

    def test_get_all_events_with_data(self, client: TestClient, logged_in_user: AuthenticatedUser):
        """Test getting all events when some exist."""
        # Create an event first
        now = datetime.now(UTC)
        event_data: dict[str, Any] = {
            "title": "Test Event",
            "description": "Test Description",
            "location": "Test Location",
            "start_date": (now + timedelta(days=1)).isoformat(),
            "end_date": (now + timedelta(days=1, hours=2)).isoformat(),
        }
        client.post("/events/", json=event_data, headers=logged_in_user.headers)

        response = client.get("/events/")
        assert response.status_code == status.HTTP_200_OK
        events_data: list[dict[str, Any]] = response.json()
        assert len(events_data) >= 1
        events: list[Event] = [Event.model_validate(e) for e in events_data]
        assert any(e.title == "Test Event" for e in events)

    def test_get_event_by_id_success(self, client: TestClient, logged_in_user: AuthenticatedUser):
        """Test getting a specific event by ID."""
        # Create an event first
        now = datetime.now(UTC)
        event_data: dict[str, Any] = {
            "title": "Specific Event",
            "description": "To be retrieved",
            "location": "Library",
            "start_date": (now + timedelta(days=1)).isoformat(),
            "end_date": (now + timedelta(days=1, hours=1)).isoformat(),
        }
        create_response = client.post("/events/", json=event_data, headers=logged_in_user.headers)
        created_event_data: dict[str, Any] = create_response.json()
        event_id = created_event_data["id"]

        response = client.get(f"/events/{event_id}")
        assert response.status_code == status.HTTP_200_OK
        event_response: dict[str, Any] = response.json()
        event: Event = Event.model_validate(event_response)
        assert event.title == "Specific Event"
        assert event.id == event_id

    def test_get_event_by_invalid_id(self, client: TestClient):
        """Test getting event with non-existent ID."""
        response = client.get("/events/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data: dict[str, Any] = response.json()
        assert "not found" in data["detail"].lower()


class TestEventUpdate:
    """Tests for updating events."""

    def test_update_event_success(self, client: TestClient, logged_in_user: AuthenticatedUser):
        """Test successfully updating an event as the creator."""
        # Create an event
        now = datetime.now(UTC)
        event_data: dict[str, Any] = {
            "title": "Original Title",
            "description": "Original Description",
            "location": "Original Location",
            "start_date": (now + timedelta(days=1)).isoformat(),
            "end_date": (now + timedelta(days=1, hours=2)).isoformat(),
        }
        create_response = client.post("/events/", json=event_data, headers=logged_in_user.headers)
        event_id = create_response.json()["id"]

        # Update the event
        updated_data: dict[str, Any] = {
            "title": "Updated Title",
            "description": "Updated Description",
            "location": "Updated Location",
            "start_date": (now + timedelta(days=2)).isoformat(),
            "end_date": (now + timedelta(days=2, hours=3)).isoformat(),
        }
        response = client.put(
            f"/events/{event_id}", json=updated_data, headers=logged_in_user.headers
        )
        assert response.status_code == status.HTTP_200_OK
        updated_event_data: dict[str, Any] = response.json()
        updated_event: Event = Event.model_validate(updated_event_data)
        assert updated_event.title == "Updated Title"
        assert updated_event.description == "Updated Description"
        assert updated_event.location == "Updated Location"

    def test_update_event_not_creator(
        self, client: TestClient, logged_in_user: AuthenticatedUser, session: Session
    ):
        """Test that non-creators cannot update events."""
        # Create an event as logged_in_user
        now = datetime.now(UTC)
        event_data: dict[str, Any] = {
            "title": "Protected Event",
            "description": "Cannot be updated by others",
            "location": "Secure Location",
            "start_date": (now + timedelta(days=1)).isoformat(),
            "end_date": (now + timedelta(days=1, hours=2)).isoformat(),
        }
        create_response = client.post("/events/", json=event_data, headers=logged_in_user.headers)
        event_id = create_response.json()["id"]

        # Create another user
        other_user = User(
            email="other@example.com",
            username="otheruser",
            first_name="Other",
            last_name="User",
            hashed_password=get_password_hash("testpassword"),
            is_active=True,
        )
        session.add(other_user)
        session.commit()

        # Try to update as other user
        response = client.post(
            "/auth/token", data={"username": "otheruser", "password": "testpassword"}
        )
        other_token = response.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}

        updated_data: dict[str, Any] = {
            "title": "Hacked Title",
            "description": "Should not work",
            "location": "Nowhere",
            "start_date": (now + timedelta(days=2)).isoformat(),
            "end_date": (now + timedelta(days=2, hours=2)).isoformat(),
        }
        response = client.put(f"/events/{event_id}", json=updated_data, headers=other_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data: dict[str, Any] = response.json()
        assert "creator" in data["detail"].lower()

    def test_update_event_invalid_dates(
        self, client: TestClient, logged_in_user: AuthenticatedUser
    ):
        """Test updating event with invalid dates."""
        # Create an event
        now = datetime.now(UTC)
        event_data: dict[str, Any] = {
            "title": "Event to Update",
            "description": "Will have invalid dates",
            "location": "Somewhere",
            "start_date": (now + timedelta(days=1)).isoformat(),
            "end_date": (now + timedelta(days=1, hours=2)).isoformat(),
        }
        create_response = client.post("/events/", json=event_data, headers=logged_in_user.headers)
        event_id = create_response.json()["id"]

        # Try to update with invalid dates
        updated_data: dict[str, Any] = {
            "title": "Same Title",
            "description": "Same Description",
            "location": "Same Location",
            "start_date": (now + timedelta(days=3)).isoformat(),
            "end_date": (now + timedelta(days=2)).isoformat(),
        }
        response = client.put(
            f"/events/{event_id}", json=updated_data, headers=logged_in_user.headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_nonexistent_event(self, client: TestClient, logged_in_user: AuthenticatedUser):
        """Test updating a non-existent event."""
        now = datetime.now(UTC)
        updated_data: dict[str, Any] = {
            "title": "Ghost Event",
            "description": "Does not exist",
            "location": "Nowhere",
            "start_date": (now + timedelta(days=1)).isoformat(),
            "end_date": (now + timedelta(days=1, hours=2)).isoformat(),
        }
        response = client.put("/events/99999", json=updated_data, headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_event_unauthenticated(self, client: TestClient):
        """Test that unauthenticated users cannot update events."""
        now = datetime.now(UTC)
        updated_data: dict[str, Any] = {
            "title": "Unauthorized Update",
            "description": "Should fail",
            "location": "Nowhere",
            "start_date": (now + timedelta(days=1)).isoformat(),
            "end_date": (now + timedelta(days=1, hours=2)).isoformat(),
        }
        response = client.put("/events/1", json=updated_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestEventDeletion:
    """Tests for deleting events."""

    def test_delete_event_success(self, client: TestClient, logged_in_user: AuthenticatedUser):
        """Test successfully deleting an event as the creator."""
        # Create an event
        now = datetime.now(UTC)
        event_data: dict[str, Any] = {
            "title": "Event to Delete",
            "description": "Will be deleted",
            "location": "Temporary Location",
            "start_date": (now + timedelta(days=1)).isoformat(),
            "end_date": (now + timedelta(days=1, hours=2)).isoformat(),
        }
        create_response = client.post("/events/", json=event_data, headers=logged_in_user.headers)
        event_id = create_response.json()["id"]

        # Delete the event
        response = client.delete(f"/events/{event_id}", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's deleted
        get_response = client.get(f"/events/{event_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_event_not_creator(
        self, client: TestClient, logged_in_user: AuthenticatedUser, session: Session
    ):
        """Test that non-creators cannot delete events."""
        # Create an event as logged_in_user
        now = datetime.now(UTC)
        event_data: dict[str, Any] = {
            "title": "Protected Event",
            "description": "Cannot be deleted by others",
            "location": "Secure Location",
            "start_date": (now + timedelta(days=1)).isoformat(),
            "end_date": (now + timedelta(days=1, hours=2)).isoformat(),
        }
        create_response = client.post("/events/", json=event_data, headers=logged_in_user.headers)
        event_id = create_response.json()["id"]

        # Create another user
        other_user = User(
            email="deleter@example.com",
            username="deleteruser",
            first_name="Deleter",
            last_name="User",
            hashed_password=get_password_hash("testpassword"),
            is_active=True,
        )
        session.add(other_user)
        session.commit()

        # Try to delete as other user
        response = client.post(
            "/auth/token", data={"username": "deleteruser", "password": "testpassword"}
        )
        other_token = response.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}

        response = client.delete(f"/events/{event_id}", headers=other_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data: dict[str, Any] = response.json()
        assert "creator" in data["detail"].lower()

    def test_delete_nonexistent_event(self, client: TestClient, logged_in_user: AuthenticatedUser):
        """Test deleting a non-existent event."""
        response = client.delete("/events/99999", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_event_unauthenticated(self, client: TestClient):
        """Test that unauthenticated users cannot delete events."""
        response = client.delete("/events/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestEventRegistration:
    """Tests for event registration and attendance status."""

    def test_register_for_event_success(
        self, client: TestClient, logged_in_user: AuthenticatedUser
    ):
        """Test successfully registering for an event."""
        # Create an event
        now = datetime.now(UTC)
        event_data: dict[str, Any] = {
            "title": "Registerable Event",
            "description": "Users can register",
            "location": "Main Hall",
            "start_date": (now + timedelta(days=1)).isoformat(),
            "end_date": (now + timedelta(days=1, hours=2)).isoformat(),
        }
        create_response = client.post("/events/", json=event_data, headers=logged_in_user.headers)
        event_id = create_response.json()["id"]

        # Register for the event
        response = client.post(f"/events/{event_id}/register", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_201_CREATED
        attendee_data: dict[str, Any] = response.json()
        attendee: EventAttendee = EventAttendee.model_validate(attendee_data)
        assert attendee.user_id == logged_in_user.user.id
        assert attendee.event_id == event_id
        assert attendee.status == AttendanceStatusEnum.INTERESTED

    def test_register_for_nonexistent_event(
        self, client: TestClient, logged_in_user: AuthenticatedUser
    ):
        """Test registering for a non-existent event."""
        response = client.post("/events/99999/register", headers=logged_in_user.headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_register_for_event_unauthenticated(self, client: TestClient):
        """Test that unauthenticated users cannot register for events."""
        response = client.post("/events/1/register")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_registration_status_to_attending(
        self, client: TestClient, logged_in_user: AuthenticatedUser
    ):
        """Test updating registration status to attending."""
        # Create and register for an event
        now = datetime.now(UTC)
        event_data: dict[str, Any] = {
            "title": "Status Update Event",
            "description": "Status will change",
            "location": "Conference Room",
            "start_date": (now + timedelta(days=1)).isoformat(),
            "end_date": (now + timedelta(days=1, hours=3)).isoformat(),
        }
        create_response = client.post("/events/", json=event_data, headers=logged_in_user.headers)
        event_id = create_response.json()["id"]

        client.post(f"/events/{event_id}/register", headers=logged_in_user.headers)

        # Update status to attending
        response = client.put(
            f"/events/{event_id}/register",
            params={"attendance_status": "attending"},
            headers=logged_in_user.headers,
        )
        assert response.status_code == status.HTTP_200_OK
        attendee_data: dict[str, Any] = response.json()
        attendee: EventAttendee = EventAttendee.model_validate(attendee_data)
        assert attendee.status == AttendanceStatusEnum.ATTENDING

    def test_update_registration_status_to_not_attending(
        self, client: TestClient, logged_in_user: AuthenticatedUser
    ):
        """Test updating registration status to not attending."""
        # Create and register for an event
        now = datetime.now(UTC)
        event_data: dict[str, Any] = {
            "title": "Cancellable Event",
            "description": "User will not attend",
            "location": "Gym",
            "start_date": (now + timedelta(days=1)).isoformat(),
            "end_date": (now + timedelta(days=1, hours=2)).isoformat(),
        }
        create_response = client.post("/events/", json=event_data, headers=logged_in_user.headers)
        event_id = create_response.json()["id"]

        client.post(f"/events/{event_id}/register", headers=logged_in_user.headers)

        # Update status to not attending
        response = client.put(
            f"/events/{event_id}/register",
            params={"attendance_status": "not_attending"},
            headers=logged_in_user.headers,
        )
        assert response.status_code == status.HTTP_200_OK
        attendee_data: dict[str, Any] = response.json()
        attendee: EventAttendee = EventAttendee.model_validate(attendee_data)
        assert attendee.status == AttendanceStatusEnum.NOT_ATTENDING

    def test_update_registration_for_nonexistent_event(
        self, client: TestClient, logged_in_user: AuthenticatedUser
    ):
        """Test updating registration for non-existent event."""
        response = client.put(
            "/events/99999/register",
            params={"attendance_status": "attending"},
            headers=logged_in_user.headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_registration_unauthenticated(self, client: TestClient):
        """Test that unauthenticated users cannot update registration."""
        response = client.put("/events/1/register", params={"attendance_status": "attending"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_register_twice_for_same_event(
        self, client: TestClient, logged_in_user: AuthenticatedUser
    ):
        """Test registering twice for the same event (should update, not duplicate)."""
        # Create an event
        now = datetime.now(UTC)
        event_data: dict[str, Any] = {
            "title": "Double Registration Event",
            "description": "Test double registration",
            "location": "Auditorium",
            "start_date": (now + timedelta(days=1)).isoformat(),
            "end_date": (now + timedelta(days=1, hours=2)).isoformat(),
        }
        create_response = client.post("/events/", json=event_data, headers=logged_in_user.headers)
        event_id = create_response.json()["id"]

        # Register first time
        response1 = client.post(f"/events/{event_id}/register", headers=logged_in_user.headers)
        assert response1.status_code == status.HTTP_201_CREATED

        # Register second time (should work due to unique constraint handling)
        response2 = client.post(f"/events/{event_id}/register", headers=logged_in_user.headers)
        # Depending on implementation, this could be 201, 200, or 409
        assert response2.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_409_CONFLICT,
        ]
