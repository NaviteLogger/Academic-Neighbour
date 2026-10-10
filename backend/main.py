from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlmodel import Session, SQLModel, select

from database.database import engine
from models.models import (
    Conversation,
    ConversationParticipant,
    Event,
    Group,
    GroupMember,
    Message,
    Post,
    ProfileComment,
    User,
    UserRole,
)
from routers import (
    admin_router,
    auth_routes,
    comment_router,
    event_router,
    friendship_router,
    group_router,
    message_router,
    post_router,
    user_router,
)
from services.security import get_password_hash
from utils.logging import logger


def create_user_if_not_exists(
    session: Session,
    username: str,
    email: str,
    first_name: str,
    last_name: str,
    password: str,
    role: UserRole = UserRole.USER,
    is_active: bool = True,
) -> User | None:
    """
    Create a user if they don't already exist.

    Args:
        session: Database session
        username: User's unique username
        email: User's unique email address
        first_name: User's first name
        last_name: User's last name
        password: Plain text password (will be hashed)
        role: User role (default: USER)
        is_active: Whether the user account is active (default: True)

    Returns:
        User object if created or already exists, None if creation fails
    """
    existing_user = session.exec(select(User).where(User.username == username)).one_or_none()

    if existing_user:
        logger.info(f"User '{username}' already exists. Skipping creation.")
        return existing_user

    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        hashed_password=get_password_hash(password),
        is_active=is_active,
        role=role,
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    logger.info(f"Created user '{username}' with role '{role.value}'.")
    return user


def create_sample_posts(session: Session) -> None:
    """
    Create sample posts for testing if they don't already exist.

    Args:
        session: Database session
    """
    existing_posts = session.exec(select(Post)).all()
    if existing_posts:
        logger.info(f"{len(existing_posts)} posts already exist. Skipping sample post creation.")
        return

    testuser = session.exec(select(User).where(User.username == "testuser")).one_or_none()
    testuser2 = session.exec(select(User).where(User.username == "testuser2")).one_or_none()
    admin = session.exec(select(User).where(User.username == "admin")).one_or_none()

    if not testuser or not testuser2 or not admin:
        logger.warning("Cannot create sample posts: required users not found.")
        return

    if not testuser.id or not testuser2.id or not admin.id:
        logger.warning("Cannot create sample posts: user IDs are missing.")
        return

    sample_posts = [
        Post(
            content="Wspólne gotowanie w kuchni na korytarzu to najlepsza forma integracji! "
            "Ktoś ma przepis na dobry makaron? 🍝",
            author_id=testuser.id,
        ),
        Post(
            content="Organizujemy wieczór filmowy w piątek o 20:00. Kto chce dołączyć?",
            author_id=testuser2.id,
        ),
        Post(
            content="Dzisiaj sprzątanie wspólnej kuchni - "
            "dzięki wszystkim za pomoc! Razem jest lepiej",
            author_id=testuser.id,
        ),
        Post(
            content="Informacja: W sobotę o 10:00 planowana jest kontrola pokoi. "
            "Prosimy o porządek",
            author_id=admin.id,
        ),
    ]

    for post in sample_posts:
        session.add(post)

    session.commit()
    logger.info(f"Created {len(sample_posts)} sample posts.")


def create_sample_events(session: Session) -> None:
    """
    Create sample events for testing if they don't already exist.

    Args:
        session: Database session
    """
    existing_events = session.exec(select(Event)).all()
    if existing_events:
        logger.info(f"{len(existing_events)} events already exist. Skipping sample event creation.")
        return

    admin = session.exec(select(User).where(User.username == "admin")).one_or_none()

    if not admin:
        logger.warning("Cannot create sample events: admin user not found.")
        return

    if not admin.id:
        logger.warning("Cannot create sample events: admin ID is missing.")
        return

    now = datetime.now(UTC)

    sample_events = [
        Event(
            title="Hackathon 2025",
            description="COroczny hackathon dla studentów wszystkich kierunków. "
            "Zarejestruj się, aby współpracować nad innowacyjnymi projektami!",
            location="Hala Główna",
            start_date=now + timedelta(days=7),
            end_date=now + timedelta(days=7, hours=24),
            creator_id=admin.id,
        ),
        Event(
            title="Wspólna nauka: Python",
            description="Cotygodniowa grupa naukowa Pythona dla początkujących.",
            location="Biblioteka Pokój 301",
            start_date=now + timedelta(days=2, hours=14),
            end_date=now + timedelta(days=2, hours=16),
            creator_id=admin.id,
        ),
    ]

    for event in sample_events:
        session.add(event)

    session.commit()
    logger.info(f"Created {len(sample_events)} sample events.")


def create_sample_profile_comments(session: Session) -> None:
    """
    Create sample profile comments for testing if they don't already exist.

    Args:
        session: Database session
    """
    existing_comments = session.exec(select(ProfileComment)).all()
    if existing_comments:
        logger.info(f"{len(existing_comments)} profile comments already exist. Skipping creation.")
        return

    testuser = session.exec(select(User).where(User.username == "testuser")).one_or_none()
    testuser2 = session.exec(select(User).where(User.username == "testuser2")).one_or_none()
    admin = session.exec(select(User).where(User.username == "admin")).one_or_none()

    if not testuser or not testuser2 or not admin:
        logger.warning("Cannot create sample profile comments: required users not found.")
        return

    if not testuser.id or not testuser2.id or not admin.id:
        logger.warning("Cannot create sample profile comments: user IDs are missing.")
        return

    sample_comments = [
        ProfileComment(
            content="Świetny współlokator! Zawsze sprząta po sobie.",
            author_id=testuser2.id,
            profile_user_id=testuser.id,
        ),
        ProfileComment(
            content="Bardzo pomocny przy projektach z Pythona.",
            author_id=admin.id,
            profile_user_id=testuser.id,
        ),
        ProfileComment(
            content="Dzięki za pożyczenie notatek!",
            author_id=testuser.id,
            profile_user_id=testuser2.id,
        ),
    ]

    for comment in sample_comments:
        session.add(comment)

    session.commit()
    logger.info(f"Created {len(sample_comments)} sample profile comments.")


def create_sample_conversations(session: Session) -> None:
    """
    Create sample conversations and messages for testing if they don't already exist.

    Args:
        session: Database session
    """
    existing_conversations = session.exec(select(Conversation)).all()
    if existing_conversations:
        logger.info(
            f"{len(existing_conversations)} conversations already exist. Skipping creation."
        )
        return

    testuser = session.exec(select(User).where(User.username == "testuser")).one_or_none()
    testuser2 = session.exec(select(User).where(User.username == "testuser2")).one_or_none()
    admin = session.exec(select(User).where(User.username == "admin")).one_or_none()

    if not testuser or not testuser2 or not admin:
        logger.warning("Cannot create sample conversations: required users not found.")
        return

    if not testuser.id or not testuser2.id or not admin.id:
        logger.warning("Cannot create sample conversations: user IDs are missing.")
        return

    # Conversation 1: testuser and testuser2
    conversation1 = Conversation(title="Roommate Chat")
    session.add(conversation1)
    session.commit()
    session.refresh(conversation1)

    if conversation1.id:
        participant1 = ConversationParticipant(
            conversation_id=conversation1.id, user_id=testuser.id
        )
        participant2 = ConversationParticipant(
            conversation_id=conversation1.id, user_id=testuser2.id
        )
        session.add(participant1)
        session.add(participant2)
        session.commit()

        # Messages in conversation 1
        message1 = Message(
            content="Cześć! Kiedy planujesz wrócić do akademika?",
            sender_id=testuser.id,
            conversation_id=conversation1.id,
        )
        message2 = Message(
            content="Hej! Będę za godzinę. Potrzebujesz czegoś?",
            sender_id=testuser2.id,
            conversation_id=conversation1.id,
        )
        session.add(message1)
        session.add(message2)

    session.commit()
    logger.info("Created a sample one-to-one conversations with messages.")


def create_sample_groups(session: Session) -> None:
    """
    Create sample groups for testing if they don't already exist.

    Args:
        session: Database session
    """
    existing_groups = session.exec(select(Group)).all()
    if existing_groups:
        logger.info(f"{len(existing_groups)} groups already exist. Skipping sample group creation.")
        return

    # Get existing users
    testuser = session.exec(select(User).where(User.username == "testuser")).one_or_none()
    testuser2 = session.exec(select(User).where(User.username == "testuser2")).one_or_none()
    admin = session.exec(select(User).where(User.username == "admin")).one_or_none()

    if not testuser or not testuser2 or not admin:
        logger.warning("Required users not found. Skipping sample group creation.")
        return

    # Create additional users for groups
    user3 = create_user_if_not_exists(
        session=session,
        username="alice",
        email="alice@example.com",
        first_name="Alice",
        last_name="Johnson",
        password="TestPassword123",
        is_active=True,
    )

    user4 = create_user_if_not_exists(
        session=session,
        username="bob",
        email="bob@example.com",
        first_name="Bob",
        last_name="Smith",
        password="TestPassword123",
        is_active=True,
    )

    user5 = create_user_if_not_exists(
        session=session,
        username="charlie",
        email="charlie@example.com",
        first_name="Charlie",
        last_name="Brown",
        password="TestPassword123",
        is_active=True,
    )

    if not user3 or not user4 or not user5:
        logger.warning("Failed to create additional users. Skipping sample group creation.")
        return

    # Create sample groups
    group1 = Group(
        name="Koło Naukowe Informatyki",
        description=(
            "Grupa dla studentów informatyki do wspólnej pracy nad zadaniami "
            "i dzielenia się zasobami."
        ),
        creator_id=testuser.id,  # type: ignore
    )
    session.add(group1)
    session.flush()

    group2 = Group(
        name="Społeczność Piętro 3",
        description=(
            "Grupa społeczności mieszkańców 3. piętra. "
            "Dziel się ogłoszeniami i organizuj wydarzenia!"
        ),
        creator_id=testuser2.id,  # type: ignore
    )
    session.add(group2)
    session.flush()

    group3 = Group(
        name="Weekendowi Wędrowcy",
        description=(
            "Grupa dla studentów kochających wędrówki i aktywności na świeżym powietrzu. "
            "Odkrywajmy razem szlaki!"
        ),
        creator_id=user3.id,  # type: ignore
    )
    session.add(group3)
    session.flush()

    group4 = Group(
        name="Klub Filmowy",
        description=(
            "Cotygodniowe wieczory filmowe w świetlicy. Głosuj na filmy i dołącz do nas na popcorn!"
        ),
        creator_id=admin.id,  # type: ignore
    )
    session.add(group4)
    session.flush()

    group5 = Group(
        name="Siłownia Razem",
        description=(
            "Ćwiczmy razem i motywujmy się nawzajem. Mile widziane wszystkie poziomy zaawansowania!"
        ),
        creator_id=user4.id,  # type: ignore
    )
    session.add(group5)
    session.flush()

    # Add members to groups
    # CS Study Group members
    session.add(GroupMember(group_id=group1.id, user_id=testuser.id))  # type: ignore
    session.add(GroupMember(group_id=group1.id, user_id=testuser2.id))  # type: ignore
    session.add(GroupMember(group_id=group1.id, user_id=user3.id))  # type: ignore
    session.add(GroupMember(group_id=group1.id, user_id=user5.id))  # type: ignore

    # Dorm Floor 3 members
    session.add(GroupMember(group_id=group2.id, user_id=testuser2.id))  # type: ignore
    session.add(GroupMember(group_id=group2.id, user_id=testuser.id))  # type: ignore
    session.add(GroupMember(group_id=group2.id, user_id=user4.id))  # type: ignore
    session.add(GroupMember(group_id=group2.id, user_id=user5.id))  # type: ignore

    # Weekend Hikers members
    session.add(GroupMember(group_id=group3.id, user_id=user3.id))  # type: ignore
    session.add(GroupMember(group_id=group3.id, user_id=testuser.id))  # type: ignore
    session.add(GroupMember(group_id=group3.id, user_id=user4.id))  # type: ignore

    # Movie Night Club members
    session.add(GroupMember(group_id=group4.id, user_id=admin.id))  # type: ignore
    session.add(GroupMember(group_id=group4.id, user_id=testuser.id))  # type: ignore
    session.add(GroupMember(group_id=group4.id, user_id=testuser2.id))  # type: ignore
    session.add(GroupMember(group_id=group4.id, user_id=user3.id))  # type: ignore
    session.add(GroupMember(group_id=group4.id, user_id=user4.id))  # type: ignore
    session.add(GroupMember(group_id=group4.id, user_id=user5.id))  # type: ignore

    # Fitness Buddies members
    session.add(GroupMember(group_id=group5.id, user_id=user4.id))  # type: ignore
    session.add(GroupMember(group_id=group5.id, user_id=testuser2.id))  # type: ignore
    session.add(GroupMember(group_id=group5.id, user_id=user5.id))  # type: ignore

    session.commit()
    logger.info("Created 5 sample groups with members.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for application startup/shutdown events."""
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
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

        create_sample_posts(session)
        create_sample_events(session)
        create_sample_profile_comments(session)
        create_sample_conversations(session)
        create_sample_groups(session)

    logger.info("Application lifespan startup complete.")
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(user_router.router)
app.include_router(admin_router.router)
app.include_router(auth_routes.router)
app.include_router(post_router.router)
app.include_router(comment_router.router)
app.include_router(event_router.router)
app.include_router(friendship_router.router)
app.include_router(group_router.router)
app.include_router(message_router.router)

origins: list[str] = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=RedirectResponse)
def read_root() -> RedirectResponse:
    """Redirect root endpoint to API documentation."""
    logger.info("Root endpoint accessed, redirecting to /docs")
    return RedirectResponse(url="/docs")
