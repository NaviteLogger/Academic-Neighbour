from collections.abc import Generator

from sqlalchemy import Engine
from sqlmodel import Session, create_engine

postgres_url: str = "postgresql://postgres:postgres@postgres:5432/postgres"
engine: Engine = create_engine(postgres_url, echo=True)


def get_session() -> Generator[Session, None, None]:
    """Returns (yields) the opened session to interact with the database.

    Yields:
        Session: an open database session
    """
    with Session(engine) as session:
        yield session
