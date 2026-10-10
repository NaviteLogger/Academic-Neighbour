from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pwdlib import PasswordHash
from sqlmodel import Session

from database.database import get_session
from models.models import TokenData, User, UserRole
from repositories.user_repo import get_user_by_email, get_user_by_username
from utils.logging import logger

# To get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
session = Depends(get_session)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plain password."""
    return password_hash.hash(password)


def authenticate_user(session: Session, username_or_email: str, password: str) -> User | None:
    """Authenticate a user by username or email and password."""
    user = get_user_by_username(session, username_or_email)
    if not user:
        user = get_user_by_email(session, username_or_email)
        if not user:
            logger.warning(f"Failed authentication attempt for: {username_or_email}")
            return None

    if not verify_password(password, user.hashed_password):
        logger.warning(f"Invalid password for user: {username_or_email}")
        return None

    if not user.is_active:
        logger.warning(f"Inactive user attempted login: {username_or_email}")
        return None

    logger.info(f"User authenticated successfully: {username_or_email}")
    return user


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token.

    Args:
        data (dict): Data to encode in the token
        expires_delta (timedelta | None, optional): Time duration for token expiration.
        Defaults to None.

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict[str, Any]:
    """Verify and decode JWT token.

    Args:
        token (str): JWT token to verify

    Returns:
        dict: Decoded token payload

    Raises:
        HTTPException: If token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception from e


async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = session) -> User:
    """Dependency to get the current user based on the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception from e

    if token_data.username is None:
        raise credentials_exception

    user = get_user_by_username(session, username=token_data.username)
    if user is None:
        logger.warning(f"User not found in database: {token_data.username}")
        raise credentials_exception
    return user


current_user = Depends(get_current_user)


async def get_current_active_user(current_user: User = current_user) -> User:
    """Dependency to ensure the current user is active."""
    if not current_user.is_active:
        logger.warning(f"Inactive user attempted access: {current_user.username}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account")
    return current_user


active_user = Depends(get_current_active_user)


def get_current_admin_user(active_user: User = active_user) -> User:
    """Dependency to ensure the current user has admin role."""
    if active_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return active_user
