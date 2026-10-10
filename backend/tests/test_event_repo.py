from datetime import UTC, datetime, timedelta

from sqlmodel import Session

from models.models import Event, User
from repositories.event_repo import (
    add_attendee,
    create_event,
    delete_event,
    get_all_events,
    get_event_attendees_count,
    get_event_by_id,
    get_event_with_creator,
    remove_attendee,
    update_event,
)
from services.security import get_password_hash


class TestEventRepository:
    """Tests for event repository functions."""

    def test_create_event(self, session: Session):
        """Test creating a new event."""
        user = User(
            email="eventcreator@example.com",
            username="eventcreator",
            first_name="Event",
            last_name="Creator",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        start_date = datetime.now(UTC) + timedelta(days=1)
        end_date = start_date + timedelta(hours=2)

        event = Event(
            title="Test Event",
            description="Test event description",
            location="Test Location",
            start_date=start_date,
            end_date=end_date,
            creator_id=user.id,
        )

        created_event = create_event(session, event)

        assert created_event is not None
        assert created_event.id is not None
        assert created_event.title == "Test Event"
        assert created_event.description == "Test event description"
        assert created_event.location == "Test Location"
        assert created_event.creator_id == user.id

    def test_get_all_events_empty(self, session: Session):
        """Test getting all events when database is empty."""
        events = get_all_events(session)

        assert events == []
        assert len(events) == 0

    def test_get_all_events_with_data(self, session: Session):
        """Test getting all events when events exist."""
        user = User(
            email="multievent@example.com",
            username="multievent",
            first_name="Multi",
            last_name="Event",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        start_date1 = datetime.now(UTC) + timedelta(days=1)
        start_date2 = datetime.now(UTC) + timedelta(days=2)
        start_date3 = datetime.now(UTC) + timedelta(days=3)

        event1 = Event(
            title="Event 1",
            description="First event",
            location="Location 1",
            start_date=start_date1,
            end_date=start_date1 + timedelta(hours=2),
            creator_id=user.id,
        )
        event2 = Event(
            title="Event 2",
            description="Second event",
            location="Location 2",
            start_date=start_date2,
            end_date=start_date2 + timedelta(hours=2),
            creator_id=user.id,
        )
        event3 = Event(
            title="Event 3",
            description="Third event",
            location="Location 3",
            start_date=start_date3,
            end_date=start_date3 + timedelta(hours=2),
            creator_id=user.id,
        )

        session.add(event1)
        session.add(event2)
        session.add(event3)
        session.commit()

        events = get_all_events(session)

        assert len(events) == 3
        titles = {e.title for e in events}
        assert "Event 1" in titles
        assert "Event 2" in titles
        assert "Event 3" in titles

    def test_get_all_events_excludes_past_events(self, session: Session):
        """Test that get_all_events excludes past events."""
        user = User(
            email="pastevents@example.com",
            username="pastevents",
            first_name="Past",
            last_name="Events",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        past_date = datetime.now(UTC) - timedelta(days=1)
        future_date = datetime.now(UTC) + timedelta(days=1)

        past_event = Event(
            title="Past Event",
            description="Event in the past",
            location="Past Location",
            start_date=past_date - timedelta(hours=2),
            end_date=past_date,
            creator_id=user.id,
        )
        future_event = Event(
            title="Future Event",
            description="Event in the future",
            location="Future Location",
            start_date=future_date,
            end_date=future_date + timedelta(hours=2),
            creator_id=user.id,
        )

        session.add(past_event)
        session.add(future_event)
        session.commit()

        events = get_all_events(session)

        assert len(events) == 1
        assert events[0].title == "Future Event"

    def test_get_event_by_id_exists(self, session: Session):
        """Test getting an event by ID when it exists."""
        user = User(
            email="singleevent@example.com",
            username="singleevent",
            first_name="Single",
            last_name="Event",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        start_date = datetime.now(UTC) + timedelta(days=1)
        event = Event(
            title="Specific Event",
            description="Event to find",
            location="Specific Location",
            start_date=start_date,
            end_date=start_date + timedelta(hours=2),
            creator_id=user.id,
        )
        session.add(event)
        session.commit()
        session.refresh(event)

        if not event.id:
            raise ValueError("Event must have an ID")

        found_event = get_event_by_id(session, event.id)

        assert found_event is not None
        assert found_event.id == event.id
        assert found_event.title == "Specific Event"

    def test_get_event_by_id_not_exists(self, session: Session):
        """Test getting an event by ID when it doesn't exist."""
        found_event = get_event_by_id(session, 99999)

        assert found_event is None

    def test_get_event_with_creator_exists(self, session: Session):
        """Test getting an event with creator information."""
        user = User(
            email="creatorevent@example.com",
            username="creatorevent",
            first_name="Creator",
            last_name="Event",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        start_date = datetime.now(UTC) + timedelta(days=1)
        event = Event(
            title="Event with Creator",
            description="Event with creator info",
            location="Creator Location",
            start_date=start_date,
            end_date=start_date + timedelta(hours=2),
            creator_id=user.id,
        )
        session.add(event)
        session.commit()
        session.refresh(event)

        if not event.id:
            raise ValueError("Event must have an ID")

        result = get_event_with_creator(session, event.id)

        assert result is not None
        event_result, creator_result = result
        assert event_result.id == event.id
        assert event_result.title == "Event with Creator"
        assert creator_result.id == user.id
        assert creator_result.username == "creatorevent"

    def test_get_event_with_creator_not_exists(self, session: Session):
        """Test getting event with creator when event doesn't exist."""
        result = get_event_with_creator(session, 99999)

        assert result is None

    def test_update_event_title(self, session: Session):
        """Test updating an event's title."""
        user = User(
            email="updateevent@example.com",
            username="updateevent",
            first_name="Update",
            last_name="Event",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        start_date = datetime.now(UTC) + timedelta(days=1)
        event = Event(
            title="Original Title",
            description="Original description",
            location="Original Location",
            start_date=start_date,
            end_date=start_date + timedelta(hours=2),
            creator_id=user.id,
        )
        session.add(event)
        session.commit()
        session.refresh(event)

        if not event.id:
            raise ValueError("Event must have an ID")

        updated_event = update_event(session, event.id, title="Updated Title")

        assert updated_event is not None
        assert updated_event.title == "Updated Title"
        assert updated_event.description == "Original description"

    def test_update_event_all_fields(self, session: Session):
        """Test updating all event fields."""
        user = User(
            email="updateall@example.com",
            username="updateall",
            first_name="Update",
            last_name="All",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        start_date = datetime.now(UTC) + timedelta(days=1)
        event = Event(
            title="Original",
            description="Original",
            location="Original",
            start_date=start_date,
            end_date=start_date + timedelta(hours=2),
            creator_id=user.id,
        )
        session.add(event)
        session.commit()
        session.refresh(event)

        if not event.id:
            raise ValueError("Event must have an ID")

        new_start = datetime.now(UTC) + timedelta(days=5)
        new_end = new_start + timedelta(hours=3)

        updated_event = update_event(
            session,
            event.id,
            title="Updated Title",
            description="Updated Description",
            location="Updated Location",
            start_date=new_start,
            end_date=new_end,
        )

        assert updated_event is not None
        assert updated_event.title == "Updated Title"
        assert updated_event.description == "Updated Description"
        assert updated_event.location == "Updated Location"
        assert updated_event.start_date.replace(tzinfo=None) == new_start.replace(tzinfo=None)
        assert updated_event.end_date.replace(tzinfo=None) == new_end.replace(tzinfo=None)

    def test_update_event_not_exists(self, session: Session):
        """Test updating an event that doesn't exist."""
        result = update_event(session, 99999, title="New Title")

        assert result is None

    def test_delete_event_exists(self, session: Session):
        """Test deleting an event that exists."""
        user = User(
            email="deleteevent@example.com",
            username="deleteevent",
            first_name="Delete",
            last_name="Event",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        start_date = datetime.now(UTC) + timedelta(days=1)
        event = Event(
            title="Event to Delete",
            description="This will be deleted",
            location="Delete Location",
            start_date=start_date,
            end_date=start_date + timedelta(hours=2),
            creator_id=user.id,
        )
        session.add(event)
        session.commit()
        session.refresh(event)

        if not event.id:
            raise ValueError("Event must have an ID")

        result = delete_event(session, event.id)

        assert result is True
        deleted = get_event_by_id(session, event.id)
        assert deleted is None

    def test_delete_event_not_exists(self, session: Session):
        """Test deleting an event that doesn't exist."""
        result = delete_event(session, 99999)

        assert result is False

    def test_add_attendee(self, session: Session):
        """Test adding an attendee to an event."""
        user = User(
            email="attendee@example.com",
            username="attendee",
            first_name="Attendee",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        start_date = datetime.now(UTC) + timedelta(days=1)
        event = Event(
            title="Event for Attendee",
            description="Event to attend",
            location="Attendee Location",
            start_date=start_date,
            end_date=start_date + timedelta(hours=2),
            creator_id=user.id,
        )
        session.add(event)
        session.commit()
        session.refresh(event)

        if not event.id:
            raise ValueError("Event must have an ID")

        attendee = add_attendee(session, user.id, event.id, "attending")

        assert attendee is not None
        assert attendee.user_id == user.id
        assert attendee.event_id == event.id
        assert attendee.status == "attending"

    def test_add_attendee_updates_existing(self, session: Session):
        """Test that adding an existing attendee updates their status."""
        user = User(
            email="updateattendee@example.com",
            username="updateattendee",
            first_name="Update",
            last_name="Attendee",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        start_date = datetime.now(UTC) + timedelta(days=1)
        event = Event(
            title="Event for Status Update",
            description="Event to update status",
            location="Status Location",
            start_date=start_date,
            end_date=start_date + timedelta(hours=2),
            creator_id=user.id,
        )
        session.add(event)
        session.commit()
        session.refresh(event)

        if not event.id:
            raise ValueError("Event must have an ID")

        first_attendee = add_attendee(session, user.id, event.id, "interested")
        updated_attendee = add_attendee(session, user.id, event.id, "attending")

        assert first_attendee.id == updated_attendee.id
        assert updated_attendee.status == "attending"

    def test_remove_attendee_exists(self, session: Session):
        """Test removing an attendee that exists."""
        user = User(
            email="removeattendee@example.com",
            username="removeattendee",
            first_name="Remove",
            last_name="Attendee",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        start_date = datetime.now(UTC) + timedelta(days=1)
        event = Event(
            title="Event for Removal",
            description="Event to remove from",
            location="Removal Location",
            start_date=start_date,
            end_date=start_date + timedelta(hours=2),
            creator_id=user.id,
        )
        session.add(event)
        session.commit()
        session.refresh(event)

        if not event.id:
            raise ValueError("Event must have an ID")

        add_attendee(session, user.id, event.id, "attending")
        result = remove_attendee(session, user.id, event.id)

        assert result is True

    def test_remove_attendee_not_exists(self, session: Session):
        """Test removing an attendee that doesn't exist."""
        user = User(
            email="noattendee@example.com",
            username="noattendee",
            first_name="No",
            last_name="Attendee",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        start_date = datetime.now(UTC) + timedelta(days=1)
        event = Event(
            title="Event No Attendee",
            description="Event with no attendees",
            location="No Attendee Location",
            start_date=start_date,
            end_date=start_date + timedelta(hours=2),
            creator_id=user.id,
        )
        session.add(event)
        session.commit()
        session.refresh(event)

        if not event.id:
            raise ValueError("Event must have an ID")

        result = remove_attendee(session, user.id, event.id)

        assert result is False

    def test_get_event_attendees_count_zero(self, session: Session):
        """Test getting attendee count for event with no attendees."""
        user = User(
            email="countattendee@example.com",
            username="countattendee",
            first_name="Count",
            last_name="Attendee",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        if not user.id:
            raise ValueError("User must have an ID")

        start_date = datetime.now(UTC) + timedelta(days=1)
        event = Event(
            title="Event for Count",
            description="Event to count attendees",
            location="Count Location",
            start_date=start_date,
            end_date=start_date + timedelta(hours=2),
            creator_id=user.id,
        )
        session.add(event)
        session.commit()
        session.refresh(event)

        if not event.id:
            raise ValueError("Event must have an ID")

        count = get_event_attendees_count(session, event.id)

        assert count == 0

    def test_get_event_attendees_count_with_attendees(self, session: Session):
        """Test getting attendee count for event with multiple attendees."""
        user1 = User(
            email="attendeecount1@example.com",
            username="attendeecount1",
            first_name="Count",
            last_name="One",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        user2 = User(
            email="attendeecount2@example.com",
            username="attendeecount2",
            first_name="Count",
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

        start_date = datetime.now(UTC) + timedelta(days=1)
        event = Event(
            title="Popular Event",
            description="Event with many attendees",
            location="Popular Location",
            start_date=start_date,
            end_date=start_date + timedelta(hours=2),
            creator_id=user1.id,
        )
        session.add(event)
        session.commit()
        session.refresh(event)

        if not event.id:
            raise ValueError("Event must have an ID")
        if not user2.id:
            raise ValueError("User2 must have an ID")

        add_attendee(session, user1.id, event.id, "attending")
        add_attendee(session, user2.id, event.id, "attending")

        count = get_event_attendees_count(session, event.id)

        assert count == 2
