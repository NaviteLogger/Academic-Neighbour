from datetime import UTC, datetime

from sqlmodel import Session, desc, func, select

from models.models import Event, EventAttendee, User


def create_event(session: Session, event: Event) -> Event:
    """Create a new event."""
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def get_all_events(session: Session) -> list[Event]:
    """Get all events ordered by start date (upcoming first)."""
    current_time = datetime.now(UTC)
    statement = (
        select(Event).where(Event.end_date >= current_time).order_by(Event.start_date)  # pyright: ignore[reportArgumentType]
    )
    return list(session.exec(statement).all())


def get_event_by_id(session: Session, event_id: int) -> Event | None:
    """Get an event by its ID."""
    return session.get(Event, event_id)


def get_event_with_creator(session: Session, event_id: int) -> tuple[Event, User] | None:
    """Get an event by ID with creator information."""
    event = session.get(Event, event_id)
    if not event:
        return None
    creator = session.get(User, event.creator_id)
    if not creator:
        return None
    return (event, creator)


def update_event(
    session: Session,
    event_id: int,
    title: str | None = None,
    description: str | None = None,
    location: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> Event | None:
    """Update an event. Returns updated event or None if not found."""
    event = session.get(Event, event_id)
    if not event:
        return None

    if title is not None:
        event.title = title
    if description is not None:
        event.description = description
    if location is not None:
        event.location = location
    if start_date is not None:
        event.start_date = start_date
    if end_date is not None:
        event.end_date = end_date

    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def delete_event(session: Session, event_id: int) -> bool:
    """Delete an event. Returns True if deleted, False if not found."""
    event = session.get(Event, event_id)
    if not event:
        return False
    session.delete(event)
    session.commit()
    return True


def get_event_attendees_count(session: Session, event_id: int) -> int:
    """Get the count of attendees for a specific event."""
    statement = (
        select(func.count()).select_from(EventAttendee).where(EventAttendee.event_id == event_id)
    )
    result = session.exec(statement).one()
    return result


def add_attendee(
    session: Session, user_id: int, event_id: int, status: str = "attending"
) -> EventAttendee:
    """Add a user as an attendee to an event with specified status. Updates if already exists."""
    # Check if already attending/interested
    existing = session.exec(
        select(EventAttendee).where(
            EventAttendee.user_id == user_id, EventAttendee.event_id == event_id
        )
    ).first()

    if existing:
        # Update status if already exists
        existing.status = status
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    attendee = EventAttendee(user_id=user_id, event_id=event_id, status=status)
    session.add(attendee)
    session.commit()
    session.refresh(attendee)
    return attendee


def remove_attendee(session: Session, user_id: int, event_id: int) -> bool:
    """Remove a user from event attendees. Returns True if removed, False if not found."""
    attendee = session.exec(
        select(EventAttendee).where(
            EventAttendee.user_id == user_id, EventAttendee.event_id == event_id
        )
    ).first()

    if not attendee:
        return False

    session.delete(attendee)
    session.commit()
    return True


def get_event_attendees(session: Session, event_id: int) -> list[tuple[EventAttendee, User]]:
    """Get all attendees for an event with their user information."""
    statement = (
        select(EventAttendee, User)
        .join(User, EventAttendee.user_id == User.id)
        .where(EventAttendee.event_id == event_id)
        .order_by(desc(EventAttendee.joined_at))
    )
    return list(session.exec(statement).all())
