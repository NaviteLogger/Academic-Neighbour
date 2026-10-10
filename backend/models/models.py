import enum
from datetime import UTC, datetime

from sqlalchemy import TEXT, Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel  # type: ignore

# ============================================================================
# ENUMERATIONS
# ============================================================================


class UserRole(str, enum.Enum):
    """User role enumeration for role-based access control."""

    USER = "user"
    ADMIN = "admin"


class FriendshipStatusEnum(str, enum.Enum):
    """Friendship status enumeration."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class AttendanceStatusEnum(str, enum.Enum):
    """Event attendance status enumeration."""

    ATTENDING = "attending"
    INTERESTED = "interested"
    NOT_ATTENDING = "not_attending"


# ============================================================================
# DATABASE MODELS (SQLModel with table=True)
# ============================================================================


class User(SQLModel, table=True):
    """User model for storing user information."""

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    username: str = Field(unique=True, index=True, max_length=50)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    hashed_password: str = Field(max_length=255)
    role: UserRole = Field(sa_column=Column(SAEnum(UserRole)), default=UserRole.USER)
    is_active: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Post(SQLModel, table=True):
    """Post model for storing user posts."""

    id: int | None = Field(default=None, primary_key=True)
    content: str = Field(sa_column=Column(TEXT))
    author_id: int = Field(foreign_key="user.id", index=True)
    group_id: int | None = Field(default=None, foreign_key="group.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Friendship(SQLModel, table=True):
    """Friendship model for managing user friendships."""

    id: int | None = Field(default=None, primary_key=True)
    requester_id: int = Field(foreign_key="user.id", index=True)
    addressee_id: int = Field(foreign_key="user.id", index=True)
    status: FriendshipStatusEnum = Field(
        sa_column=Column(SAEnum(FriendshipStatusEnum)), default=FriendshipStatusEnum.PENDING
    )


class PostLike(SQLModel, table=True):
    """PostLike model for managing likes on posts. Each user can like a post only once."""

    __tablename__ = "post_likes"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    post_id: int = Field(foreign_key="post.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Comment(SQLModel, table=True):
    """Comment model for storing comments on posts."""

    id: int | None = Field(default=None, primary_key=True)
    content: str = Field(sa_column=Column(TEXT))
    author_id: int = Field(foreign_key="user.id", index=True)
    post_id: int = Field(foreign_key="post.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProfileComment(SQLModel, table=True):
    """ProfileComment model for storing comments on user profiles."""

    __tablename__ = "profile_comment"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    content: str = Field(sa_column=Column(TEXT))
    author_id: int = Field(foreign_key="user.id", index=True)
    profile_user_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Conversation(SQLModel, table=True):
    """Conversation model for managing conversations."""

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ConversationParticipant(SQLModel, table=True):
    """ConversationParticipant model for managing conversation participants."""

    __tablename__ = "conversation_participants"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    joined_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Message(SQLModel, table=True):
    """Message model for managing messages in conversations."""

    id: int | None = Field(default=None, primary_key=True)
    content: str = Field(sa_column=Column(TEXT))
    sender_id: int = Field(foreign_key="user.id", index=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Event(SQLModel, table=True):
    """Event model for storing events in the university dorm."""

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    description: str = Field(sa_column=Column(TEXT))
    location: str = Field(max_length=255)
    start_date: datetime
    end_date: datetime
    creator_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EventAttendee(SQLModel, table=True):
    """EventAttendee model for managing event participants."""

    __tablename__ = "event_attendees"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    event_id: int = Field(foreign_key="event.id", index=True)
    status: AttendanceStatusEnum = Field(
        sa_column=Column(SAEnum(AttendanceStatusEnum)), default=AttendanceStatusEnum.ATTENDING
    )
    joined_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Group(SQLModel, table=True):
    """Group model for managing user groups."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    description: str = Field(sa_column=Column(TEXT))
    creator_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class GroupMember(SQLModel, table=True):
    """GroupMember model for managing group membership."""

    __tablename__ = "group_members"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="group.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    joined_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ============================================================================
# REQUEST/RESPONSE MODELS (SQLModel without table=True)
# ============================================================================


class EventCreate(SQLModel):
    """Event creation model for creating new events."""

    title: str = Field(max_length=255)
    description: str
    location: str = Field(max_length=255)
    start_date: datetime
    end_date: datetime


class EventUpdate(SQLModel):
    """Event update model for modifying existing events."""

    title: str | None = Field(default=None, max_length=255)
    description: str | None = None
    location: str | None = Field(default=None, max_length=255)
    start_date: datetime | None = None
    end_date: datetime | None = None


# User-related models
class UserCreate(SQLModel):
    """User creation model for user registration."""

    email: str
    username: str = Field(min_length=3, max_length=50)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8)


class UserRead(SQLModel):
    """User read model for API responses (excludes sensitive data)."""

    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool
    created_at: datetime


# Authentication models
class Token(SQLModel):
    """Token model for authentication responses."""

    access_token: str
    token_type: str


class TokenData(SQLModel):
    """Token data model for storing decoded token information."""

    username: str | None = None


class TokenWithUser(SQLModel):
    """Token response with user information."""

    access_token: str
    token_type: str
    user: UserRead


class CommentRequest(SQLModel):
    """Request model for creating/updating a comment."""

    content: str = Field(min_length=1)


class PostCreate(SQLModel):
    """Request model for creating a post."""

    content: str = Field(min_length=1)


class ContentWithAuthor(SQLModel):
    """Generic response model for any content with author details."""

    id: int
    content: str
    author_id: int
    group_id: int | None = None
    created_at: str
    author_name: str


class CommentWithAuthor(ContentWithAuthor):
    """Response model for comment with author details."""

    post_id: int


class ProfileCommentWithAuthor(ContentWithAuthor):
    """Response model for profile comment with author details."""

    profile_user_id: int


class PostWithAuthor(ContentWithAuthor):
    """Response model for post with author details."""

    pass


class LikesInfo(SQLModel):
    """Response model for post likes information."""

    likes_count: int
    liked_by_current_user: bool


class GroupCreate(SQLModel):
    """Group creation model."""

    name: str = Field(min_length=3, max_length=100)
    description: str


class GroupRead(SQLModel):
    """Group read model."""

    id: int
    name: str
    description: str
    creator_id: int
    created_at: datetime


class ConversationCreate(SQLModel):
    """Conversation creation model - one-to-one only."""

    participant_id: int  # Single participant ID for one-to-one conversation


class ConversationRead(SQLModel):
    """Conversation read model."""

    id: int
    title: str
    created_at: datetime


class MessageCreate(SQLModel):
    """Message creation model."""

    content: str = Field(min_length=1)


class MessageRead(SQLModel):
    """Message read model with sender information."""

    id: int
    content: str
    sender_id: int
    sender_name: str
    conversation_id: int
    created_at: str


# ============================================================================
# TEST FIXTURE MODELS
# ============================================================================


class AuthenticatedUser(SQLModel):
    """Model for authenticated user with token and headers (used in tests)."""

    user: User
    token: str
    headers: dict[str, str]


class FriendshipScenario(SQLModel):
    """Model for friendship test scenario with user IDs (used in tests)."""

    user_a_id: int
    user_b_id: int
    user_c_id: int
    user_d_id: int
