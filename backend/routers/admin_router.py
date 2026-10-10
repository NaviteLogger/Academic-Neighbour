from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database.database import get_session
from models.models import User
from repositories.user_repo import get_user_by_email, get_user_by_username
from services.security import get_current_admin_user

router = APIRouter(prefix="/admin", tags=["admin"])

session: Session = Depends(get_session)
current_admin: User = Depends(get_current_admin_user)


@router.get("/users", response_model=list[User])
def read_all_users(
    session: Session = session,
    current_admin: User = current_admin,
) -> list[User]:
    """Admin-only endpoint to get all users."""
    users = session.exec(select(User)).all()
    return list(users)


@router.get("/user/{identifier}", response_model=User)
def read_user_by_username(
    identifier: str,
    session: Session = session,
    current_admin: User = current_admin,
) -> User | None:
    """Admin-only endpoint to get user by username or email."""
    user = get_user_by_username(session, identifier)
    if not user:
        user = get_user_by_email(session, identifier)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
