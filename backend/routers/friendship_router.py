import enum

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from database.database import get_session
from models.models import Friendship, FriendshipStatusEnum, User
from repositories.friendship_repo import (
    create_friendship,
    get_accepted_friends,
    get_accepted_friendship,
    get_friendship_any_status,
    get_pending_friendship,
    get_received_pending_requests,
    get_sent_pending_requests,
    update_friendship,
)
from repositories.user_repo import get_user_by_id
from services.security import get_current_active_user, get_current_user
from utils.logging import logger

router = APIRouter(prefix="/friendships", tags=["friendships"])

current_user = Depends(get_current_user)
session = Depends(get_session)
current_active_user = Depends(get_current_active_user)


class FriendListFilter(str, enum.Enum):
    """Filter options for listing friends."""

    ACCEPTED = "accepted"
    PENDING = "pending"
    SENT = "sent"


@router.post(
    "/request/{addressee_id}",
    response_model=Friendship,
    status_code=status.HTTP_201_CREATED,
)
def send_friend_request(
    addressee_id: int,
    current_user: User = current_user,
    session: Session = session,
) -> Friendship:
    """Sends a friend request to the user with the given ID.

    Args:
        addressee_id (int): ID of the user to send the friend request to
        current_user (User, optional): The user sending the friend request. Defaults to current_user
        session (Session, optional): Database session. Defaults to session.

    Raises:
        HTTPException: 400 Bad Request if the user tries to send a request to themselves
        HTTPException: 404 Not Found if the addressee user does not exist
        HTTPException: 500 Internal Server Error if the current user is missing an ID
        HTTPException: 409 Conflict if a friendship or request already exists

    Returns:
        Friendship: The created friendship object
    """
    if addressee_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sending friend requests to yourself is not allowed.",
        )

    addressee = get_user_by_id(session, addressee_id)
    if not addressee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist.")

    if not current_user.id:
        logger.error("User missing id identifier")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User missing id identifier"
        )

    existing_friendship = get_friendship_any_status(session, current_user.id, addressee_id)
    if existing_friendship:
        match existing_friendship.status:
            case FriendshipStatusEnum.ACCEPTED:
                detail = "You are already friends."
            case FriendshipStatusEnum.PENDING:
                detail = "Friend request has already been sent."
            case FriendshipStatusEnum.DECLINED:
                detail = "User has already declined your friend request."
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)

    return create_friendship(
        session,
        Friendship(
            requester_id=current_user.id,
            addressee_id=addressee_id,
            status=FriendshipStatusEnum.PENDING,
        ),
    )


@router.post("/accept/{requester_id}", response_model=Friendship)
def accept_friend_request(
    requester_id: int,
    current_user: User = current_active_user,
    session: Session = session,
) -> Friendship:
    """Accept a friend request from a user with the given ID.

    Args:
        requester_id (int): ID of the user who sent the friend request
        current_user (User, optional): The user accepting the request.
            Defaults to current_active_user
        session (Session, optional): Database session. Defaults to session.

    Raises:
        HTTPException: 500 Internal Server Error if the current user is missing an ID
        HTTPException: 404 Not Found if no pending request from this user exists

    Returns:
        Friendship: The updated friendship object with ACCEPTED status
    """
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User missing id identifier"
        )

    pending_request = get_pending_friendship(
        session, requester_id=requester_id, addressee_id=current_user.id
    )
    if not pending_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending friend request found from this user.",
        )

    pending_request.status = FriendshipStatusEnum.ACCEPTED
    return update_friendship(session, pending_request)


@router.post("/decline/{requester_id}", response_model=Friendship)
def decline_friend_request(
    requester_id: int,
    current_user: User = current_active_user,
    session: Session = session,
) -> Friendship:
    """Decline a friend request from a user with the given ID.

    Args:
        requester_id (int): ID of the user who sent the friend request
        current_user (User, optional): The user declining the request.
            Defaults to current_active_user
        session (Session, optional): Database session. Defaults to session.

    Raises:
        HTTPException: 500 Internal Server Error if the current user is missing an ID
        HTTPException: 404 Not Found if no pending request from this user exists

    Returns:
        Friendship: The updated friendship object with DECLINED status
    """
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User missing id identifier"
        )

    pending_request = get_pending_friendship(
        session, requester_id=requester_id, addressee_id=current_user.id
    )
    if not pending_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending friend request found from this user.",
        )

    pending_request.status = FriendshipStatusEnum.DECLINED
    return update_friendship(session, pending_request)


@router.delete("/remove/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_friend(
    friend_id: int,
    current_user: User = current_active_user,
    session: Session = session,
) -> None:
    """Remove a friend (delete friendship).

    Args:
        friend_id (int): ID of the friend to remove
        current_user (User, optional): The user removing the friend.
            Defaults to current_active_user
        session (Session, optional): Database session. Defaults to session.

    Raises:
        HTTPException: 500 Internal Server Error if the current user is missing an ID
        HTTPException: 404 Not Found if no friendship exists with this user

    Returns:
        None: Returns 204 No Content on success
    """
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User missing id identifier"
        )

    accepted_friendship = get_accepted_friendship(
        session, user1_id=current_user.id, user2_id=friend_id
    )
    if not accepted_friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not friends with this user.",
        )

    session.delete(accepted_friendship)
    session.commit()
    return


@router.get("/", response_model=list[User])
def read_friends(
    filter_type: FriendListFilter = FriendListFilter.ACCEPTED,
    current_user: User = current_active_user,
    session: Session = session,
) -> list[User]:
    """Get a list of friends or pending requests.

    Query Parameters:
        filter_type: Filter friends by status
            - accepted: Accepted friends (default)
            - pending: Received pending friend requests
            - sent: Sent pending friend requests

    Args:
        current_user (User, optional): The user whose friends to retrieve.
            Defaults to current_active_user
        session (Session, optional): Database session. Defaults to session.

    Raises:
        HTTPException: 500 Internal Server Error if the current user is missing an ID

    Returns:
        list[User]: List of users based on the filter type
    """
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User missing id identifier"
        )

    match filter_type:
        case FriendListFilter.ACCEPTED:
            return get_accepted_friends(session=session, user_id=current_user.id)
        case FriendListFilter.PENDING:
            return get_received_pending_requests(session=session, user_id=current_user.id)
        case FriendListFilter.SENT:
            return get_sent_pending_requests(session=session, user_id=current_user.id)
        case _:
            return get_accepted_friends(session=session, user_id=current_user.id)
