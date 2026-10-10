# Dokumentacja Techniczna - Academic Neighbour API

## Spis treści

1. [Architektura systemu](#architektura-systemu)
2. [Stack technologiczny](#stack-technologiczny)
3. [Struktura projektu](#struktura-projektu)
4. [Baza danych](#baza-danych)
5. [Modele danych](#modele-danych)
6. [Warstwa bezpieczeństwa](#warstwa-bezpieczeństwa)
7. [Endpointy API](#endpointy-api)
8. [WebSocket](#websocket)
9. [Repozytoria](#repozytoria)
10. [Testy](#testy)
11. [Deployment](#deployment)
12. [Konfiguracja środowiska](#konfiguracja-środowiska)

---

## Architektura systemu

Aplikacja została zbudowana w oparciu o architekturę warstwową (layered architecture) z wyraźnym podziałem odpowiedzialności:

```
┌─────────────────────────────────────┐
│     Warstwa prezentacji (API)       │
│        FastAPI Routers              │
├─────────────────────────────────────┤
│      Warstwa logiki biznesowej      │
│           Services                   │
├─────────────────────────────────────┤
│      Warstwa dostępu do danych      │
│         Repositories                 │
├─────────────────────────────────────┤
│         Warstwa danych              │
│    PostgreSQL + SQLModel/SQLAlchemy │
└─────────────────────────────────────┘
```

### Wzorce projektowe zastosowane w systemie

- **Repository Pattern**: Oddzielenie logiki dostępu do danych od logiki biznesowej
- **Dependency Injection**: Wykorzystanie systemu dependencies FastAPI do zarządzania zależnościami
- **Singleton Pattern**: Manager połączeń WebSocket
- **Factory Pattern**: Tworzenie sesji bazy danych
- **DTO Pattern**: Modele Pydantic do walidacji i serializacji danych

---

## Stack technologiczny

### Framework i języki

- **Python 3.12+**: Język programowania
- **FastAPI 0.119.1+**: Framework webowy ASGI
- **SQLModel 0.0.27**: ORM łączący SQLAlchemy i Pydantic
- **Uvicorn**: Serwer ASGI

### Baza danych

- **PostgreSQL**: Relacyjna baza danych
- **psycopg2 2.9.11**: Adapter PostgreSQL dla Pythona

### Bezpieczeństwo

- **python-jose[cryptography] 3.5.0**: Obsługa JWT (JSON Web Tokens)
- **pwdlib[argon2] 0.3.0**: Hashowanie haseł algorytmem Argon2
- **OAuth2PasswordBearer**: Schemat autentykacji OAuth2

### Testowanie

- **pytest 8.4.2**: Framework testowy
- **pytest-asyncio 1.2.0**: Wsparcie dla testów asynchronicznych
- **pytest-cov**: Analiza pokrycia kodu testami
- **httpx**: Klient HTTP do testów API

### Narzędzia deweloperskie

- **Ruff 0.14.3**: Linter i formatter kodu
- **Black**: Formatter kodu
- **isort**: Sortowanie importów
- **mypy**: Statyczna analiza typów

### Dodatkowe biblioteki

- **python-dotenv 1.1.1**: Zarządzanie zmiennymi środowiskowymi
- **python-multipart 0.0.20**: Obsługa formularzy multipart

---

## Struktura projektu

```
/workspaces/Python-FastAPI/
│
├── main.py                    # Punkt wejścia aplikacji
├── pyproject.toml             # Konfiguracja projektu i zależności
├── pytest.ini                 # Konfiguracja testów
├── Dockerfile                 # Definicja obrazu Docker
├── README.md                  # Dokumentacja podstawowa
│
├── database/                  # Warstwa bazy danych
│   ├── __init__.py
│   └── database.py           # Konfiguracja połączenia i engine
│
├── models/                    # Modele danych
│   ├── __init__.py
│   └── models.py             # Modele SQLModel i Pydantic
│
├── repositories/              # Warstwa dostępu do danych
│   ├── __init__.py
│   ├── user_repo.py          # Operacje na użytkownikach
│   ├── post_repo.py          # Operacje na postach
│   ├── comment_repo.py       # Operacje na komentarzach
│   ├── friendship_repo.py    # Operacje na znajomościach
│   ├── group_repo.py         # Operacje na grupach
│   ├── event_repo.py         # Operacje na wydarzeniach
│   ├── message_repo.py       # Operacje na wiadomościach
│   └── profile_comment_repo.py # Operacje na komentarzach profilowych
│
├── routers/                   # Endpointy API
│   ├── __init__.py
│   ├── auth_routes.py        # Autentykacja i autoryzacja
│   ├── user_router.py        # Endpointy użytkowników
│   ├── post_router.py        # Endpointy postów
│   ├── comment_router.py     # Endpointy komentarzy
│   ├── friendship_router.py  # Endpointy znajomości
│   ├── group_router.py       # Endpointy grup
│   ├── event_router.py       # Endpointy wydarzeń
│   ├── message_router.py     # Endpointy wiadomości
│   └── admin_router.py       # Panel administracyjny
│
├── services/                  # Logika biznesowa
│   ├── __init__.py
│   ├── security.py           # Autentykacja, autoryzacja, JWT
│   └── websocket_manager.py  # Zarządzanie połączeniami WebSocket
│
├── utils/                     # Narzędzia pomocnicze
│   ├── __init__.py
│   └── logging.py            # Konfiguracja logowania
│
├── tests/                     # Testy jednostkowe i integracyjne
│   ├── __init__.py
│   ├── conftest.py           # Fixtures pytest
│   ├── test_auth_router.py
│   ├── test_user_router.py
│   ├── test_post_router.py
│   ├── test_comment_router.py
│   ├── test_friendship_router.py
│   ├── test_group_router.py
│   ├── test_event_router.py
│   ├── test_message_router.py
│   ├── test_websocket.py
│   ├── test_user_repo.py
│   ├── test_post_repo.py
│   ├── test_comment_repo.py
│   ├── test_friendship_repo.py
│   ├── test_event_repo.py
│   ├── test_security.py
│   ├── test_error_handling.py
│   ├── test_integration.py
│   └── test_performance.py
│
├── docs/                      # Dokumentacja
│   ├── database.drawio       # Diagram bazy danych
│   ├── DOKUMENTACJA_UZYTKOWNIKA.md
│   ├── DOKUMENTACJA_TECHNICZNA.md
│   └── WEBSOCKET.md
│
└── logs/                      # Logi aplikacji
```

---

## Baza danych

### Konfiguracja połączenia

**Plik**: `database/database.py`

```python
from sqlmodel import Session, create_engine

postgres_url: str = "postgresql://postgres:postgres@postgres:5432/postgres"
engine: Engine = create_engine(postgres_url, echo=True)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
```

### Parametry połączenia

- **Host**: postgres (kontener Docker)
- **Port**: 5432
- **Użytkownik**: postgres
- **Hasło**: postgres
- **Baza danych**: postgres
- **Echo**: True (logowanie wszystkich zapytań SQL)

### Engine SQLAlchemy

- Wykorzystuje connection pooling
- Automatyczne zarządzanie transakcjami
- Wsparcie dla operacji asynchronicznych

---

## Modele danych

### Enumeracje

#### UserRole

```python
class UserRole(str, enum.Enum):
    USER = "user"      # Standardowy użytkownik
    ADMIN = "admin"    # Administrator systemu
```

#### FriendshipStatusEnum

```python
class FriendshipStatusEnum(str, enum.Enum):
    PENDING = "pending"        # Oczekujące zaproszenie
    ACCEPTED = "accepted"      # Zaakceptowane zaproszenie
    DECLINED = "declined"      # Odrzucone zaproszenie
```

#### AttendanceStatusEnum

```python
class AttendanceStatusEnum(str, enum.Enum):
    ATTENDING = "attending"            # Uczestniczy
    INTERESTED = "interested"          # Zainteresowany
    NOT_ATTENDING = "not_attending"    # Nie uczestniczy
```

### Modele bazodanowe (SQLModel)

#### User

Reprezentuje użytkownika systemu.

**Pola**:

- `id`: int (PK, auto-increment)
- `email`: str (unique, indexed, max 255 znaków)
- `username`: str (unique, indexed, max 50 znaków)
- `first_name`: str (max 100 znaków)
- `last_name`: str (max 100 znaków)
- `hashed_password`: str (max 255 znaków)
- `role`: UserRole (domyślnie USER)
- `is_active`: bool (domyślnie False)
- `created_at`: datetime (UTC)

**Indeksy**:

- email (unique)
- username (unique)

#### Post

Reprezentuje post użytkownika.

**Pola**:

- `id`: int (PK)
- `content`: TEXT
- `author_id`: int (FK -> user.id, indexed)
- `group_id`: int | None (FK -> group.id, indexed)
- `created_at`: datetime (UTC)

**Relacje**:

- Należy do jednego użytkownika (author)
- Może należeć do grupy (opcjonalnie)

#### Friendship

Reprezentuje relację znajomości między użytkownikami.

**Pola**:

- `id`: int (PK)
- `requester_id`: int (FK -> user.id, indexed)
- `addressee_id`: int (FK -> user.id, indexed)
- `status`: FriendshipStatusEnum (domyślnie PENDING)

**Logika**:

- Requester wysyła zaproszenie do addressee
- Status może być: PENDING, ACCEPTED, DECLINED

#### PostLike

Reprezentuje polubienie posta przez użytkownika.

**Pola**:

- `id`: int (PK)
- `user_id`: int (FK -> user.id, indexed)
- `post_id`: int (FK -> post.id, indexed)
- `created_at`: datetime (UTC)

**Ograniczenia**:

- Użytkownik może polubić post tylko raz

#### Comment

Reprezentuje komentarz pod postem.

**Pola**:

- `id`: int (PK)
- `content`: TEXT
- `author_id`: int (FK -> user.id, indexed)
- `post_id`: int (FK -> post.id, indexed)
- `created_at`: datetime (UTC)

#### ProfileComment

Reprezentuje komentarz na profilu użytkownika.

**Pola**:

- `id`: int (PK)
- `content`: TEXT
- `author_id`: int (FK -> user.id, indexed)
- `profile_owner_id`: int (FK -> user.id, indexed)
- `created_at`: datetime (UTC)

#### Group

Reprezentuje grupę użytkowników.

**Pola**:

- `id`: int (PK)
- `name`: str (max 100 znaków)
- `description`: TEXT | None
- `creator_id`: int (FK -> user.id, indexed)
- `created_at`: datetime (UTC)

#### GroupMember

Reprezentuje członkostwo w grupie.

**Pola**:

- `id`: int (PK)
- `group_id`: int (FK -> group.id, indexed)
- `user_id`: int (FK -> user.id, indexed)
- `joined_at`: datetime (UTC)

#### Event

Reprezentuje wydarzenie.

**Pola**:

- `id`: int (PK)
- `title`: str (max 200 znaków)
- `description`: TEXT | None
- `location`: str | None (max 255 znaków)
- `start_time`: datetime
- `end_time`: datetime | None
- `creator_id`: int (FK -> user.id, indexed)
- `group_id`: int | None (FK -> group.id, indexed)
- `created_at`: datetime (UTC)

#### EventAttendance

Reprezentuje uczestnictwo w wydarzeniu.

**Pola**:

- `id`: int (PK)
- `event_id`: int (FK -> event.id, indexed)
- `user_id`: int (FK -> user.id, indexed)
- `status`: AttendanceStatusEnum (domyślnie INTERESTED)
- `created_at`: datetime (UTC)

#### Conversation

Reprezentuje konwersację między użytkownikami.

**Pola**:

- `id`: int (PK)
- `created_at`: datetime (UTC)

#### ConversationParticipant

Reprezentuje uczestnika konwersacji.

**Pola**:

- `id`: int (PK)
- `conversation_id`: int (FK -> conversation.id, indexed)
- `user_id`: int (FK -> user.id, indexed)
- `joined_at`: datetime (UTC)

#### Message

Reprezentuje wiadomość w konwersacji.

**Pola**:

- `id`: int (PK)
- `conversation_id`: int (FK -> conversation.id, indexed)
- `sender_id`: int (FK -> user.id, indexed)
- `content`: TEXT
- `created_at`: datetime (UTC)

### Modele Pydantic (DTO)

Modele Pydantic służą do walidacji danych wejściowych i serializacji odpowiedzi API.

#### Przykładowe modele

- `UserRead`: Reprezentacja użytkownika bez hasła
- `UserCreate`: Dane do utworzenia użytkownika
- `UserUpdate`: Dane do aktualizacji użytkownika
- `TokenData`: Dane zawarte w tokenie JWT
- `TokenWithUser`: Token z informacjami o użytkowniku
- `PostCreate`, `PostRead`, `PostUpdate`
- `CommentCreate`, `CommentRead`
- `FriendshipCreate`, `FriendshipRead`
- Itp.

---

## Warstwa bezpieczeństwa

### Algorytmy i standardy

**Plik**: `services/security.py`

#### Hashowanie haseł

```python
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()  # Domyślnie Argon2
```

**Algorytm**: Argon2id

- Zwycięzca konkursu Password Hashing Competition (2015)
- Odporny na ataki GPU i side-channel
- Parametry: memory-hard, time-hard

#### JWT (JSON Web Tokens)

```python
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000
```

**Konfiguracja**:

- Algorytm: HS256 (HMAC with SHA-256)
- Czas wygaśnięcia: 3000 minut (~50 godzin)
- Secret key: 256-bit klucz wygenerowany przez openssl

### Funkcje bezpieczeństwa

#### verify_password

```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)
```

Weryfikuje hasło w postaci jawnej z zahashowanym hasłem.

#### get_password_hash

```python
def get_password_hash(password: str) -> str:
    return password_hash.hash(password)
```

Hashuje hasło w postaci jawnej.

#### authenticate_user

```python
def authenticate_user(session: Session, username_or_email: str, password: str) -> User | None:
    user = get_user_by_username(session, username_or_email)
    if not user:
        user = get_user_by_email(session, username_or_email)
        if not user:
            return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    if not user.is_active:
        return None
    
    return user
```

**Proces autentykacji**:

1. Wyszukuje użytkownika po username lub email
2. Weryfikuje hasło
3. Sprawdza czy konto jest aktywne
4. Zwraca obiekt User lub None

#### create_access_token

```python
def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

**Struktura tokenu JWT**:

- Header: `{"alg": "HS256", "typ": "JWT"}`
- Payload: `{"sub": "username", "exp": timestamp}`
- Signature: HMAC-SHA256(base64(header) + "." + base64(payload), SECRET_KEY)

#### verify_token

```python
def verify_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

### OAuth2PasswordBearer

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
```

**Schemat autoryzacji**:

- Standard OAuth2 Password Flow
- Token w nagłówku: `Authorization: Bearer <token>`
- Automatyczna walidacja przez FastAPI

### Dependency dla chronionych endpointów

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    payload = verify_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = get_user_by_username(session, username)
    if user is None:
        raise credentials_exception
    
    return user
```

### Kontrola dostępu oparta na rolach (RBAC)

```python
async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
```

---

## Endpointy API

### Struktura routera

Każdy router jest zorganizowany jako moduł FastAPI APIRouter z określonym prefixsem i tagami.

```python
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])
```

### Auth Routes (`/auth`)

#### POST `/auth/token`

Logowanie użytkownika i generowanie tokenu JWT.

**Request Body** (form-data):

```
username: string
password: string
```

**Response** (200):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "testuser",
    "first_name": "Jan",
    "last_name": "Kowalski",
    "role": "user",
    "is_active": true,
    "created_at": "2025-01-01T12:00:00Z"
  }
}
```

**Błędy**:

- 401: Nieprawidłowe dane logowania

### User Routes (`/users`)

#### GET `/users/me`

Pobiera dane aktualnie zalogowanego użytkownika.

**Autoryzacja**: Bearer Token (wymagana)

**Response** (200):

```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "testuser",
  "first_name": "Jan",
  "last_name": "Kowalski",
  "role": "user",
  "is_active": true,
  "created_at": "2025-01-01T12:00:00Z"
}
```

#### POST `/users/register`

Rejestracja nowego użytkownika.

**Request Body**:

```json
{
  "email": "newuser@example.com",
  "username": "newuser",
  "first_name": "Anna",
  "last_name": "Nowak",
  "password": "SecurePassword123!"
}
```

**Response** (201):

```json
{
  "id": 2,
  "email": "newuser@example.com",
  "username": "newuser",
  "first_name": "Anna",
  "last_name": "Nowak",
  "role": "user",
  "is_active": false,
  "created_at": "2025-01-01T12:30:00Z"
}
```

**Błędy**:

- 400: Użytkownik już istnieje

#### GET `/users/search?q={query}`

Wyszukiwanie użytkowników po nazwie użytkownika lub imieniu/nazwisku.

**Parametry**:

- `q`: string (query parameter)

**Autoryzacja**: Bearer Token (wymagana)

**Response** (200):

```json
[
  {
    "id": 1,
    "username": "testuser",
    "first_name": "Jan",
    "last_name": "Kowalski"
  }
]
```

#### GET `/users/{user_id}`

Pobiera dane użytkownika o podanym ID.

**Parametry**:

- `user_id`: int (path parameter)

**Autoryzacja**: Bearer Token (wymagana)

### Post Routes (`/posts`)

#### GET `/posts/`

Lista wszystkich postów z paginacją.

**Parametry**:

- `skip`: int = 0
- `limit`: int = 100

**Autoryzacja**: Bearer Token (wymagana)

**Response** (200):

```json
[
  {
    "id": 1,
    "content": "To jest treść posta",
    "author_id": 1,
    "group_id": null,
    "created_at": "2025-01-01T12:00:00Z",
    "author": {
      "id": 1,
      "username": "testuser"
    },
    "likes_count": 5,
    "comments_count": 3
  }
]
```

#### POST `/posts/`

Tworzy nowy post.

**Request Body**:

```json
{
  "content": "Treść nowego posta",
  "group_id": null
}
```

**Autoryzacja**: Bearer Token (wymagana)

**Response** (201):

```json
{
  "id": 2,
  "content": "Treść nowego posta",
  "author_id": 1,
  "group_id": null,
  "created_at": "2025-01-01T13:00:00Z"
}
```

#### DELETE `/posts/{post_id}`

Usuwa post (tylko autor lub admin).

**Parametry**:

- `post_id`: int

**Autoryzacja**: Bearer Token (wymagana)

**Response** (204): No Content

**Błędy**:

- 403: Brak uprawnień
- 404: Post nie istnieje

#### POST `/posts/{post_id}/like`

Dodaje polubienie do posta.

**Parametry**:

- `post_id`: int

**Autoryzacja**: Bearer Token (wymagana)

**Response** (200):

```json
{
  "message": "Post liked successfully"
}
```

**Błędy**:

- 400: Post już polubiony

#### DELETE `/posts/{post_id}/like`

Usuwa polubienie z posta.

### Comment Routes (`/comments`)

#### GET `/posts/{post_id}/comments`

Lista komentarzy dla danego posta.

**Parametry**:

- `post_id`: int

**Autoryzacja**: Bearer Token (wymagana)

#### POST `/posts/{post_id}/comments`

Dodaje komentarz do posta.

**Request Body**:

```json
{
  "content": "To jest komentarz"
}
```

**Autoryzacja**: Bearer Token (wymagana)

#### DELETE `/comments/{comment_id}`

Usuwa komentarz (tylko autor lub admin).

### Friendship Routes (`/friendships`)

#### GET `/friendships/`

Lista znajomości użytkownika.

**Autoryzacja**: Bearer Token (wymagana)

**Response** (200):

```json
[
  {
    "id": 1,
    "requester_id": 1,
    "addressee_id": 2,
    "status": "accepted"
  }
]
```

#### POST `/friendships/`

Wysyła zaproszenie do znajomych.

**Request Body**:

```json
{
  "addressee_id": 2
}
```

**Autoryzacja**: Bearer Token (wymagana)

#### PUT `/friendships/{friendship_id}/accept`

Akceptuje zaproszenie do znajomych.

#### PUT `/friendships/{friendship_id}/decline`

Odrzuca zaproszenie do znajomych.

#### DELETE `/friendships/{friendship_id}`

Usuwa znajomość.

### Group Routes (`/groups`)

#### GET `/groups/`

Lista wszystkich grup.

#### POST `/groups/`

Tworzy nową grupę.

**Request Body**:

```json
{
  "name": "Grupa studialna",
  "description": "Grupa do nauki programowania"
}
```

#### POST `/groups/{group_id}/join`

Dołącza do grupy.

#### DELETE `/groups/{group_id}/leave`

Opuszcza grupę.

#### GET `/groups/{group_id}/members`

Lista członków grupy.

#### GET `/groups/{group_id}/posts`

Lista postów w grupie.

### Event Routes (`/events`)

#### GET `/events/`

Lista wszystkich wydarzeń.

#### POST `/events/`

Tworzy nowe wydarzenie.

**Request Body**:

```json
{
  "title": "Spotkanie grupy",
  "description": "Spotkanie w sprawie projektu",
  "location": "Sala 101",
  "start_time": "2025-01-15T10:00:00Z",
  "end_time": "2025-01-15T12:00:00Z",
  "group_id": 1
}
```

#### POST `/events/{event_id}/attend`

Zmienia status uczestnictwa w wydarzeniu.

**Request Body**:

```json
{
  "status": "attending"
}
```

### Message Routes (`/messages`)

#### GET `/conversations/`

Lista konwersacji użytkownika.

#### POST `/conversations/`

Tworzy nową konwersację.

**Request Body**:

```json
{
  "participant_ids": [2, 3]
}
```

#### GET `/conversations/{conversation_id}/messages`

Lista wiadomości w konwersacji.

#### POST `/conversations/{conversation_id}/messages`

Wysyła wiadomość w konwersacji.

**Request Body**:

```json
{
  "content": "Treść wiadomości"
}
```

### Admin Routes (`/admin`)

**Uwaga**: Wszystkie endpointy wymagają roli ADMIN.

#### GET `/admin/users`

Lista wszystkich użytkowników (tylko admin).

#### DELETE `/admin/users/{user_id}`

Usuwa użytkownika (tylko admin).

#### PUT `/admin/users/{user_id}/activate`

Aktywuje konto użytkownika (tylko admin).

#### PUT `/admin/users/{user_id}/deactivate`

Dezaktywuje konto użytkownika (tylko admin).

---

## WebSocket

### ConnectionManager

**Plik**: `services/websocket_manager.py`

Manager zarządzający połączeniami WebSocket dla komunikacji w czasie rzeczywistym.

#### Struktura danych

```python
class ConnectionManager:
    def __init__(self):
        # {conversation_id: [websocket1, websocket2, ...]}
        self.active_connections: dict[int, list[WebSocket]] = {}
        # {websocket: user_id}
        self.connection_users: dict[WebSocket, int] = {}
```

#### Metody

##### connect

```python
async def connect(self, websocket: WebSocket, conversation_id: int, user_id: int)
```

Akceptuje i przechowuje nowe połączenie WebSocket.

**Proces**:

1. Akceptuje połączenie WebSocket
2. Dodaje do listy aktywnych połączeń dla konwersacji
3. Zapisuje mapping websocket -> user_id

##### disconnect

```python
def disconnect(self, websocket: WebSocket, conversation_id: int)
```

Usuwa połączenie WebSocket.

**Proces**:

1. Usuwa z listy aktywnych połączeń
2. Usuwa mapping websocket -> user_id
3. Czyści puste "pokoje" konwersacji

##### send_personal_message

```python
async def send_personal_message(self, message: str, websocket: WebSocket)
```

Wysyła wiadomość do konkretnego połączenia.

##### broadcast_to_conversation

```python
async def broadcast_to_conversation(
    self, 
    message: dict[str, Any], 
    conversation_id: int, 
    exclude_sender: WebSocket | None = None
)
```

Rozgłasza wiadomość do wszystkich uczestników konwersacji.

**Parametry**:

- `message`: Słownik z danymi wiadomości
- `conversation_id`: ID konwersacji
- `exclude_sender`: Opcjonalne wykluczenie nadawcy

**Proces**:

1. Serializuje message do JSON
2. Iteruje po wszystkich połączeniach w konwersacji
3. Wysyła wiadomość (z opcjonalnym wykluczeniem nadawcy)
4. Obsługuje błędy zamkniętych połączeń

##### get_conversation_connections_count

```python
def get_conversation_connections_count(self, conversation_id: int) -> int
```

Zwraca liczbę aktywnych połączeń dla konwersacji.

### Endpoint WebSocket

```python
@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: int,
    token: str = Query(...),
    session: Session = Depends(get_session)
):
    # 1. Weryfikacja tokenu
    current_user = await get_current_user_from_token(token, session)
    
    # 2. Weryfikacja uprawnień do konwersacji
    conversation = get_conversation(session, conversation_id)
    if not user_in_conversation(current_user.id, conversation):
        await websocket.close(code=1008)  # Policy Violation
        return
    
    # 3. Połączenie
    await manager.connect(websocket, conversation_id, current_user.id)
    
    try:
        while True:
            # 4. Odbieranie wiadomości
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # 5. Zapisanie w bazie danych
            message = create_message(
                session,
                conversation_id,
                current_user.id,
                message_data["content"]
            )
            
            # 6. Broadcast do wszystkich uczestników
            await manager.broadcast_to_conversation(
                {
                    "id": message.id,
                    "content": message.content,
                    "sender_id": current_user.id,
                    "created_at": message.created_at.isoformat()
                },
                conversation_id
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)
```

### Format wiadomości WebSocket

#### Wiadomość od klienta do serwera

```json
{
  "content": "Treść wiadomości"
}
```

#### Wiadomość od serwera do klienta

```json
{
  "id": 123,
  "content": "Treść wiadomości",
  "sender_id": 1,
  "created_at": "2025-01-01T12:00:00Z"
}
```

### Kody zamknięcia WebSocket

- **1000**: Normal Closure
- **1008**: Policy Violation (brak uprawnień)
- **1011**: Internal Server Error

---

## Repozytoria

Repozytoria implementują wzorzec Repository Pattern, oddzielając logikę dostępu do danych od logiki biznesowej.

### Struktura repozytorium

```python
from sqlmodel import Session, select
from models.models import User

def get_user_by_id(session: Session, user_id: int) -> User | None:
    """Retrieve a user by their ID."""
    statement = select(User).where(User.id == user_id)
    return session.exec(statement).one_or_none()

def create_user(session: Session, user: User) -> User:
    """Create a new user in the database."""
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
```

### user_repo.py

**Funkcje**:

- `get_user_by_email(session, email)`: Pobiera użytkownika po email
- `get_user_by_username(session, username)`: Pobiera użytkownika po username
- `get_user_by_id(session, user_id)`: Pobiera użytkownika po ID
- `create_user(session, user)`: Tworzy nowego użytkownika
- `search_users(session, query)`: Wyszukuje użytkowników

### post_repo.py

**Funkcje**:

- `get_posts(session, skip, limit)`: Lista postów z paginacją
- `get_post_by_id(session, post_id)`: Pobiera post po ID
- `create_post(session, post)`: Tworzy nowy post
- `delete_post(session, post_id)`: Usuwa post
- `get_posts_by_author(session, author_id)`: Posty danego autora
- `get_posts_by_group(session, group_id)`: Posty w danej grupie

### comment_repo.py

**Funkcje**:

- `get_comments_by_post(session, post_id)`: Komentarze dla posta
- `create_comment(session, comment)`: Tworzy komentarz
- `delete_comment(session, comment_id)`: Usuwa komentarz
- `get_comment_by_id(session, comment_id)`: Pobiera komentarz po ID

### friendship_repo.py

**Funkcje**:

- `get_friendships(session, user_id)`: Lista znajomości użytkownika
- `create_friendship(session, friendship)`: Tworzy zaproszenie
- `update_friendship_status(session, friendship_id, status)`: Aktualizuje status
- `delete_friendship(session, friendship_id)`: Usuwa znajomość
- `get_friendship_by_id(session, friendship_id)`: Pobiera znajomość po ID

### group_repo.py

**Funkcje**:

- `get_groups(session)`: Lista wszystkich grup
- `get_group_by_id(session, group_id)`: Pobiera grupę po ID
- `create_group(session, group)`: Tworzy grupę
- `add_member(session, group_id, user_id)`: Dodaje członka
- `remove_member(session, group_id, user_id)`: Usuwa członka
- `get_group_members(session, group_id)`: Lista członków grupy

### event_repo.py

**Funkcje**:

- `get_events(session)`: Lista wszystkich wydarzeń
- `get_event_by_id(session, event_id)`: Pobiera wydarzenie po ID
- `create_event(session, event)`: Tworzy wydarzenie
- `update_attendance(session, event_id, user_id, status)`: Aktualizuje status uczestnictwa
- `get_event_attendees(session, event_id)`: Lista uczestników wydarzenia

### message_repo.py

**Funkcje**:

- `get_conversations(session, user_id)`: Lista konwersacji użytkownika
- `create_conversation(session, participant_ids)`: Tworzy konwersację
- `get_messages(session, conversation_id)`: Lista wiadomości w konwersacji
- `create_message(session, message)`: Tworzy wiadomość
- `get_conversation_participants(session, conversation_id)`: Lista uczestników

### profile_comment_repo.py

**Funkcje**:

- `get_profile_comments(session, profile_owner_id)`: Komentarze na profilu
- `create_profile_comment(session, comment)`: Tworzy komentarz profilowy
- `delete_profile_comment(session, comment_id)`: Usuwa komentarz profilowy

---

## Testy

### Struktura testów

Projekt wykorzystuje pytest z fixtures do testowania.

**Plik**: `tests/conftest.py`

#### Fixtures

##### test_session

```python
@pytest.fixture
def test_session():
    """Creates a test database session."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
```

##### test_client

```python
@pytest.fixture
def test_client(test_session):
    """Creates a test FastAPI client."""
    app.dependency_overrides[get_session] = lambda: test_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
```

##### test_user

```python
@pytest.fixture
def test_user(test_session):
    """Creates a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        hashed_password=get_password_hash("password"),
        is_active=True
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user
```

##### auth_headers

```python
@pytest.fixture
def auth_headers(test_user):
    """Creates authentication headers with valid JWT token."""
    token = create_access_token({"sub": test_user.username})
    return {"Authorization": f"Bearer {token}"}
```

### Typy testów

#### Testy jednostkowe (Unit Tests)

**Przykład** - `test_user_repo.py`:

```python
def test_get_user_by_username(test_session, test_user):
    user = get_user_by_username(test_session, "testuser")
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"

def test_create_user(test_session):
    user = User(
        username="newuser",
        email="new@example.com",
        first_name="New",
        last_name="User",
        hashed_password="hashed",
        is_active=True
    )
    created_user = create_user(test_session, user)
    assert created_user.id is not None
    assert created_user.username == "newuser"
```

#### Testy routerów (Router Tests)

**Przykład** - `test_auth_router.py`:

```python
def test_login_success(test_client, test_user):
    response = test_client.post(
        "/auth/token",
        data={"username": "testuser", "password": "password"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "testuser"

def test_login_invalid_credentials(test_client, test_user):
    response = test_client.post(
        "/auth/token",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
```

#### Testy integracyjne (Integration Tests)

**Przykład** - `test_integration.py`:

```python
def test_create_post_and_comment_flow(test_client, auth_headers):
    # 1. Utwórz post
    post_response = test_client.post(
        "/posts/",
        json={"content": "Test post"},
        headers=auth_headers
    )
    assert post_response.status_code == 201
    post_id = post_response.json()["id"]
    
    # 2. Dodaj komentarz
    comment_response = test_client.post(
        f"/posts/{post_id}/comments",
        json={"content": "Test comment"},
        headers=auth_headers
    )
    assert comment_response.status_code == 201
    
    # 3. Pobierz komentarze
    comments_response = test_client.get(
        f"/posts/{post_id}/comments",
        headers=auth_headers
    )
    assert comments_response.status_code == 200
    comments = comments_response.json()
    assert len(comments) == 1
    assert comments[0]["content"] == "Test comment"
```

#### Testy bezpieczeństwa (Security Tests)

**Przykład** - `test_security.py`:

```python
def test_password_hashing():
    password = "SecurePassword123!"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword", hashed)

def test_jwt_token_creation_and_verification():
    token = create_access_token({"sub": "testuser"})
    payload = verify_token(token)
    assert payload["sub"] == "testuser"
    assert "exp" in payload
```

#### Testy WebSocket

**Przykład** - `test_websocket.py`:

```python
def test_websocket_connection(test_client, test_user, auth_headers):
    token = auth_headers["Authorization"].split(" ")[1]
    with test_client.websocket_connect(
        f"/ws/1?token={token}"
    ) as websocket:
        # Wyślij wiadomość
        websocket.send_json({"content": "Hello"})
        
        # Odbierz odpowiedź
        data = websocket.receive_json()
        assert data["content"] == "Hello"
        assert data["sender_id"] == test_user.id
```

#### Testy wydajnościowe (Performance Tests)

**Przykład** - `test_performance.py`:

```python
def test_list_posts_performance(test_client, auth_headers, test_session):
    # Utwórz 100 postów
    for i in range(100):
        create_post(test_session, Post(
            content=f"Post {i}",
            author_id=1
        ))
    
    # Zmierz czas odpowiedzi
    import time
    start = time.time()
    response = test_client.get("/posts/", headers=auth_headers)
    end = time.time()
    
    assert response.status_code == 200
    assert end - start < 1.0  # Mniej niż 1 sekunda
```

#### Testy obsługi błędów (Error Handling Tests)

**Przykład** - `test_error_handling.py`:

```python
def test_404_not_found(test_client, auth_headers):
    response = test_client.get("/posts/99999", headers=auth_headers)
    assert response.status_code == 404

def test_unauthorized_access(test_client):
    response = test_client.get("/users/me")
    assert response.status_code == 401

def test_forbidden_access(test_client, auth_headers):
    # Zwykły użytkownik próbuje usunąć cudzy post
    response = test_client.delete("/posts/1", headers=auth_headers)
    assert response.status_code == 403
```

### Uruchomienie testów

```bash
# Wszystkie testy
pytest

# Z pokryciem kodu
pytest --cov=. --cov-report=html

# Konkretny plik
pytest tests/test_auth_router.py

# Konkretna funkcja
pytest tests/test_auth_router.py::test_login_success

# Z verbose output
pytest -v

# Z szczegółami błędów
pytest -vv
```

### Konfiguracja pytest

**Plik**: `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers --tb=short
```

---

## Deployment

### Docker

**Plik**: `Dockerfile`

```dockerfile
FROM python:3.15-slim

WORKDIR /app

COPY pyproject.toml .

RUN pip install --upgrade pip
RUN pip install uv
RUN uv sync

COPY . /app/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose (przykład)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/postgres
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
```

### Budowanie i uruchomienie

```bash
# Budowanie obrazu
docker build -t academic-neighbour-api .

# Uruchomienie kontenera
docker run -p 8000:8000 academic-neighbour-api

# Z Docker Compose
docker-compose up -d
```

### Produkcyjne ustawienia Uvicorn

```bash
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --loop uvloop \
  --http httptools \
  --no-access-log \
  --log-level warning
```

**Parametry**:

- `--workers 4`: Liczba procesów worker (zalecane: 2-4 × liczba rdzeni CPU)
- `--loop uvloop`: Szybsza implementacja event loop
- `--http httptools`: Szybszy parser HTTP
- `--no-access-log`: Wyłączenie logów dostępu (dla wydajności)
- `--log-level warning`: Tylko ważne logi

---

## Konfiguracja środowiska

### Zmienne środowiskowe

Zalecane użycie pliku `.env`:

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres

# Security
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=3000

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Wczytywanie zmiennych

**Plik**: `.env` + `python-dotenv`

```python
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
```

### Konfiguracja CORS

**Plik**: `main.py`

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Inicjalizacja bazy danych

**Lifespan events** w `main.py`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        create_initial_data(session)
    yield
    # Shutdown
    # Cleanup resources if needed

app = FastAPI(lifespan=lifespan)
```

### Logging

**Plik**: `utils/logging.py`

```python
import logging
import sys

logger = logging.getLogger("academic_neighbour")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler("logs/app.log")
file_handler.setLevel(logging.WARNING)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
```

---

## API Documentation

FastAPI automatycznie generuje dokumentację API:

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>
- **OpenAPI Schema**: <http://localhost:8000/openapi.json>

---

## Kontakt i wsparcie

Dla pytań technicznych i zgłaszania błędów:

- Repository: <https://github.com/MIM-univeristy-projects/Python-FastAPI>
- Issues: <https://github.com/MIM-univeristy-projects/Python-FastAPI/issues>

---

**Wersja dokumentacji**: 1.0  
**Data ostatniej aktualizacji**: 22 listopada 2025  
**Autor**: MIM University Projects Team
