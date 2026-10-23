"""DB-free integration checks for solved tracking and problem filters.

These use an in-memory SQLite database and never touch PostgreSQL, so they are safe
to run without the migration/test-database approval.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.ai.routes as ai_routes
import app.problems.routes as problems_routes
import app.solved.routes as solved_routes
from app.ai import service as ai_service
from app.core.db import get_session
from app.main import app
from app.problems.models import Problem, encode_tags
from app.users.models import User


@pytest.fixture
def sqlite_client() -> Iterator[tuple[TestClient, int]]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        user = User(codeforces_subject="cf-1", handle="tester", rating=1500)
        session.add(user)
        session.add_all(
            [
                Problem(
                    contest_id=4,
                    index="A",
                    name="Watermelon",
                    rating=800,
                    tags_csv=encode_tags(["math", "brute force"]),
                    solved_count=900,
                ),
                Problem(
                    contest_id=1,
                    index="A",
                    name="Theatre Square",
                    rating=1000,
                    tags_csv=encode_tags(["math"]),
                    solved_count=700,
                ),
                Problem(
                    contest_id=466,
                    index="C",
                    name="Number of Ways",
                    rating=1700,
                    tags_csv=encode_tags(["dp"]),
                    solved_count=100,
                ),
            ]
        )
        session.commit()
        user_id = user.id

    def override_session() -> Iterator[Session]:
        with Session(engine) as session:
            yield session

    original_problems_user = problems_routes.session_user_id
    original_solved_user = solved_routes.session_user_id
    original_ai_user = ai_routes.session_user_id
    problems_routes.session_user_id = lambda request: user_id
    solved_routes.session_user_id = lambda request: user_id
    ai_routes.session_user_id = lambda request: user_id
    app.dependency_overrides[get_session] = override_session
    try:
        with TestClient(app) as client:
            yield client, user_id
    finally:
        problems_routes.session_user_id = original_problems_user
        solved_routes.session_user_id = original_solved_user
        ai_routes.session_user_id = original_ai_user
        app.dependency_overrides.pop(get_session, None)


def test_explorer_filters_and_solved_tracking(sqlite_client) -> None:
    client, _ = sqlite_client

    assert client.get("/api/problems").json()["total"] == 3
    assert client.get("/api/problems", params={"q": "water"}).json()["total"] == 1
    assert client.get("/api/problems", params={"tag": "math"}).json()["total"] == 2
    assert (
        client.get("/api/problems", params={"min_rating": 900, "max_rating": 1200}).json()["total"]
        == 1
    )
    names = [
        p["name"]
        for p in client.get("/api/problems", params={"sort": "rating_desc"}).json()["items"]
    ]
    assert names[:2] == ["Number of Ways", "Theatre Square"]

    assert client.get("/api/problems/4/A").json()["name"] == "Watermelon"
    assert client.get("/api/problems/4/A/solved").json() == {"solved": False}
    assert client.post("/api/problems/4/A/solved").json() == {"solved": True}

    assert client.get("/api/users/me/solved").json() == [{"contest_id": 4, "index": "A"}]
    assert client.get("/api/users/me/solved/count").json() == {"count": 1}
    assert client.get("/api/users/me/progress").json() == {
        "solved_count": 1,
        "by_difficulty": [{"rating": 800, "count": 1}],
    }
    assert client.get("/api/problems", params={"solved": "true"}).json()["total"] == 1
    assert client.get("/api/problems", params={"solved": "false"}).json()["total"] == 2

    assert client.delete("/api/problems/4/A/solved").json() == {"solved": False}
    assert client.get("/api/users/me/solved").json() == []
    assert client.post("/api/problems/999/Z/solved").status_code == 404


def test_coach_hint_uses_problem_context(sqlite_client, monkeypatch) -> None:
    client, _ = sqlite_client
    captured: dict[str, object] = {}

    def fake_hint(**kwargs):
        captured.update(kwargs)
        return "Look at the parity of the total."

    monkeypatch.setattr(ai_routes.service, "generate_hint", fake_hint)
    response = client.post(
        "/api/coach/hint",
        params={"contest_id": 4, "index": "A"},
        json={"code": "print(1)", "level": 2},
    )

    assert response.status_code == 200
    assert response.json() == {"hint": "Look at the parity of the total."}
    assert captured["name"] == "Watermelon"
    assert captured["rating"] == 800
    assert captured["tags"] == ["math", "brute force"]
    assert captured["code"] == "print(1)"
    assert captured["level"] == 2


def test_coach_hint_handles_missing_problem_and_config(sqlite_client, monkeypatch) -> None:
    client, _ = sqlite_client
    missing = client.post(
        "/api/coach/hint",
        params={"contest_id": 999, "index": "Z"},
        json={"code": "print(1)"},
    )
    assert missing.status_code == 404

    def unavailable(**kwargs):
        raise ai_service.AiNotConfigured

    monkeypatch.setattr(ai_routes.service, "generate_hint", unavailable)
    response = client.post(
        "/api/coach/hint",
        params={"contest_id": 4, "index": "A"},
        json={"code": "print(1)"},
    )
    assert response.status_code == 503


def test_coach_hint_requires_authentication(sqlite_client, monkeypatch) -> None:
    client, _ = sqlite_client
    monkeypatch.setattr(ai_routes, "session_user_id", lambda request: None)

    response = client.post(
        "/api/coach/hint",
        params={"contest_id": 4, "index": "A"},
        json={"code": "print(1)"},
    )

    assert response.status_code == 401
