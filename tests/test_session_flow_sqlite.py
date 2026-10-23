"""DB-free check of the real cookie session across auth, problems, and solved routes."""

from collections.abc import Iterator

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine
from starlette.middleware.sessions import SessionMiddleware

from app.core.db import get_session
from app.problems.models import Problem, encode_tags
from app.problems.routes import router as problems_router
from app.solved.routes import router as solved_router
from app.users.models import User
from app.users.routes import router as users_router


@pytest.fixture
def session_client() -> Iterator[tuple[TestClient, int]]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = User(codeforces_subject="cf-session", handle="session_tester", rating=1400)
        session.add(user)
        session.add(
            Problem(
                contest_id=4,
                index="A",
                name="Watermelon",
                rating=800,
                tags_csv=encode_tags(["math"]),
                solved_count=900,
            )
        )
        session.commit()
        user_id = user.id

    def override_session() -> Iterator[Session]:
        with Session(engine) as session:
            yield session

    test_app = FastAPI()
    test_app.add_middleware(
        SessionMiddleware,
        secret_key="test-only-session-signing-key-32-bytes",
        session_cookie="codementor_session",
        max_age=14 * 24 * 60 * 60,
        same_site="lax",
        https_only=True,
    )
    test_app.include_router(users_router)
    test_app.include_router(problems_router)
    test_app.include_router(solved_router)

    @test_app.get("/test/login")
    def test_login(request: Request) -> dict[str, bool]:
        request.session["user_id"] = user_id
        return {"ok": True}

    test_app.dependency_overrides[get_session] = override_session
    with TestClient(test_app, base_url="https://testserver") as client:
        yield client, user_id


def test_cookie_session_drives_account_solved_and_logout(session_client) -> None:
    client, user_id = session_client

    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/users/me/solved").status_code == 401

    assert client.get("/test/login").json() == {"ok": True}
    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json() == {
        "id": user_id,
        "handle": "session_tester",
        "rating": 1400,
        "avatar": None,
    }

    assert client.post("/api/problems/4/A/solved").json() == {"solved": True}
    assert client.get("/api/users/me/solved").json() == [{"contest_id": 4, "index": "A"}]
    assert client.get("/api/problems", params={"solved": "true"}).json()["total"] == 1

    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/users/me/solved").status_code == 401
