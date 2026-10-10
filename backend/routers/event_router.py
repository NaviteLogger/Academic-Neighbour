from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from database.database import get_session
from models.models import (
    AttendanceStatusEnum,
    Event,
    EventAttendee,
    EventCreate,
    EventUpdate,
    User,
    UserRead,
)


class EventAttendeeResponse(BaseModel):
    """Response model for event attendee with user information."""

    user: UserRead
    status: str
    joined_at: str


from repositories.event_repo import (
    add_attendee,
    create_event,
    delete_event,
    get_all_events,
    get_event_attendees,
    get_event_by_id,
    update_event,
)
from services.security import get_current_active_user
from utils.logging import logger

router = APIRouter(prefix="/events", tags=["events"])

session: Session = Depends(get_session)
current_user = Depends(get_current_active_user)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_event_endpoint(
    event_data: EventCreate,
    current_user: User = current_user,
    session: Session = session,
) -> Event:
    """Create a new event. Requires authentication. Creator is the current user."""
    if not current_user.id:
        logger.error("User ID is missing")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User ID is missing"
        )

    if event_data.start_date >= event_data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date",
        )

    # Create Event from EventCreate
    event = Event(
        title=event_data.title,
        description=event_data.description,
        location=event_data.location,
        start_date=event_data.start_date,
        end_date=event_data.end_date,
        creator_id=current_user.id,
    )

    return create_event(session, event)


@router.get("/")
def get_events(
    session: Session = session,
) -> list[Event]:
    """Get all upcoming events."""
    return get_all_events(session)


@router.get("/{event_id}")
def get_event(
    event_id: int,
    session: Session = session,
) -> Event:
    """Get details of a specific event."""
    event = get_event_by_id(session, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.put("/{event_id}")
def update_event_endpoint(
    event_id: int,
    event_data: EventUpdate,
    current_user: User = current_user,
    session: Session = session,
) -> Event:
    """Update an event. Only the creator can update. Requires authentication."""
    event = get_event_by_id(session, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    # Check if user is the creator
    if event.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the event creator can update this event",
        )

    # Validate dates if both are provided or if only one is being updated
    start = event_data.start_date if event_data.start_date else event.start_date
    end = event_data.end_date if event_data.end_date else event.end_date

    if start >= end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date",
        )

    updated_event = update_event(
        session,
        event_id,
        title=event_data.title,
        description=event_data.description,
        location=event_data.location,
        start_date=event_data.start_date,
        end_date=event_data.end_date,
    )

    if not updated_event:
        logger.error("Failed to update event")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update event"
        )

    return updated_event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event_endpoint(
    event_id: int,
    current_user: User = current_user,
    session: Session = session,
) -> None:
    """Delete an event. Only the creator can delete. Requires authentication."""
    event = get_event_by_id(session, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    # Check if user is the creator
    if event.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the event creator can delete this event",
        )

    was_deleted = delete_event(session, event_id)
    if not was_deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete event"
        )


@router.post("/{event_id}/register", status_code=status.HTTP_201_CREATED)
def register_for_event(
    event_id: int,
    current_user: User = current_user,
    session: Session = session,
) -> EventAttendee:
    """
    Register logged-in user as interested in the event.
    Creates a new EventAttendees record with status 'interested'.

    Requires authentication.
    """
    # Check if event exists
    event = get_event_by_id(session, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User ID is missing"
        )

    # Add user as interested
    attendee = add_attendee(
        session, current_user.id, event_id, status=AttendanceStatusEnum.INTERESTED.value
    )
    return attendee


@router.put("/{event_id}/register", status_code=status.HTTP_200_OK)
def update_registration_status(
    event_id: int,
    attendance_status: AttendanceStatusEnum,
    current_user: User = current_user,
    session: Session = session,
) -> EventAttendee:
    """
    Update logged-in user's registration status for the event.

    Query parameters:
    - attendance_status: 'attending', 'interested', or 'not_attending'

    Requires authentication and existing registration.
    """
    # Check if event exists
    event = get_event_by_id(session, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User ID is missing"
        )

    # Update user registration status (enum.value converts to string)
    attendee = add_attendee(session, current_user.id, event_id, status=attendance_status.value)
    return attendee


@router.get("/{event_id}/attendees", response_model=list[EventAttendeeResponse])
def get_event_attendees_endpoint(
    event_id: int,
    session: Session = session,
) -> list[EventAttendeeResponse]:
    """
    Get all attendees for a specific event with their user information and attendance status.

    Returns a list of attendees with user details (id, username, email, etc.)
    and their attendance status. This endpoint is public - no authentication required.
    """
    # Check if event exists
    event = get_event_by_id(session, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    # Get attendees with user information
    attendees_data = get_event_attendees(session, event_id)

    # Format response
    result: list[EventAttendeeResponse] = []
    for attendee, user in attendees_data:
        result.append(
            EventAttendeeResponse(
                user=UserRead(
                    id=user.id,  # type: ignore
                    email=user.email,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    role=user.role,
                    is_active=user.is_active,
                    created_at=user.created_at,
                ),
                status=attendee.status.value,  # type: ignore
                joined_at=str(attendee.joined_at),
            )
        )

    return result
