import os
from collections.abc import Iterator
from pathlib import Path

# Point the app at the TEST database before anything imports app settings.
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://codementor:codementor@localhost:5432/codementor_test",
)

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session

from app.core.db import engine
from app.main import app
from app.problems.models import Problem, encode_tags

ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"


@pytest.fixture(scope="session", autouse=True)
def _migrated_database() -> Iterator[None]:
    """Build the schema with the real migrations (so they are tested too), then tear down."""
    config = Config(str(ALEMBIC_INI))
    command.upgrade(config, "head")
    yield
    command.downgrade(config, "base")


@pytest.fixture
def session() -> Iterator[Session]:
    with Session(engine) as s:
        s.execute(text("TRUNCATE TABLE problem RESTART IDENTITY"))
        s.commit()
        yield s


@pytest.fixture
def client(session: Session) -> TestClient:  # depends on `session` to start from an empty table
    return TestClient(app)


def make_problem(contest_id: int, index: str, name: str, rating: int | None, tags: list[str], **kw):
    return Problem(
        contest_id=contest_id,
        index=index,
        name=name,
        rating=rating,
        tags_csv=encode_tags(tags),
        **kw,
    )


@pytest.fixture
def seeded(session: Session) -> Session:
    session.add_all(
        [
            make_problem(4, "A", "Watermelon", 800, ["math", "brute force"], solved_count=900),
            make_problem(1, "A", "Theatre Square", 1000, ["math"], solved_count=700),
            make_problem(71, "A", "Way Too Long Words", 800, ["strings"], solved_count=800),
            make_problem(466, "C", "Number of Ways", 1700, ["dp", "binary search"]),
            make_problem(9999, "Z", "Unrated Puzzle", None, ["constructive algorithms"]),
        ]
    )
    session.commit()
    return session
