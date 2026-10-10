from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from database.database import get_session
from models.models import TokenWithUser, UserRead
from services.security import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token
from utils.logging import logger

router = APIRouter(prefix="/auth", tags=["auth"])

session: Session = Depends(get_session)


@router.post("/token", response_model=TokenWithUser)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  # noqa: B008
    session: Session = session,
) -> TokenWithUser:
    """
    OAuth2 compatible token login. Use username and password to get an access token.
    Returns token along with user information including role for frontend routing.
    The other fields (grant_type, scope, client_id, client_secret) are optional
    and can be left empty.
    """
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        logger.warning(
            f"Failed login attempt for username: {form_data.username}. Error: Invalid credentials."
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    if user.id is None:
        logger.error(f"User ID not found for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User ID not found",
        )

    # Convert User to UserRead to exclude hashed_password
    user_read = UserRead(
        id=user.id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )

    return TokenWithUser(
        access_token=access_token,
        token_type="bearer",
        user=user_read,
    )
