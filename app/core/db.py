from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine

from app.core.config import settings

# pool_pre_ping drops dead connections (e.g. after a DB restart) instead of erroring.
engine = create_engine(settings.database_url, pool_pre_ping=True)


def get_session() -> Iterator[Session]:
    """FastAPI dependency: one DB session per request, closed afterwards.

    The `yield` splits this into setup (before) and cleanup (after the response).
    Schema changes are handled by Alembic migrations (`uv run alembic upgrade head`).
    """
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
