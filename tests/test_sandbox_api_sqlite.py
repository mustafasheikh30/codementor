"""DB-free API checks for sandbox endpoint (disabled by default)."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.sandbox.routes as sandbox_routes
from app.core.db import get_session
from app.main import app
from app.users.models import User


@pytest.fixture
def sandbox_client() -> Iterator[tuple[TestClient, int]]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = User(codeforces_subject="cf-sb", handle="sandboxer", rating=1200)
        session.add(user)
        session.commit()
        user_id = user.id

    def override_session() -> Iterator[Session]:
        with Session(engine) as session:
            yield session

    original_user = sandbox_routes.session_user_id
    sandbox_routes.session_user_id = lambda request: user_id
    app.dependency_overrides[get_session] = override_session
    try:
        with TestClient(app) as client:
            yield client, user_id
    finally:
        sandbox_routes.session_user_id = original_user
        app.dependency_overrides.pop(get_session, None)


def test_sandbox_requires_auth() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/sandbox/execute", json={"language": "python", "code": "print(1)"}
        )
        assert response.status_code == 401


def test_sandbox_returns_disabled_by_default(sandbox_client) -> None:
    client, _ = sandbox_client
    response = client.post(
        "/api/sandbox/execute",
        json={"language": "python", "code": "print(1)", "time_limit_seconds": 1.0},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "disabled"
    assert body["stdout"] == ""
    assert body["exit_code"] is None


def test_sandbox_validates_input(sandbox_client) -> None:
    client, _ = sandbox_client
    assert (
        client.post("/api/sandbox/execute", json={"language": "", "code": "x"}).status_code == 422
    )
    assert (
        client.post("/api/sandbox/execute", json={"language": "py", "code": "   "}).status_code
        == 422
    )
    assert (
        client.post(
            "/api/sandbox/execute",
            json={"language": "py", "code": "x", "time_limit_seconds": 0.01},
        ).status_code
        == 422
    )
