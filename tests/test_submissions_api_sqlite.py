"""DB-free integration checks for submission recording and retrieval."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.submissions.routes as submissions_routes
from app.core.db import get_session
from app.main import app
from app.problems.models import Problem, encode_tags
from app.users.models import User


@pytest.fixture
def submissions_client() -> Iterator[tuple[TestClient, int, int]]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        owner = User(codeforces_subject="cf-owner", handle="owner", rating=1500)
        other = User(codeforces_subject="cf-other", handle="other", rating=1200)
        session.add_all(
            [
                owner,
                other,
                Problem(
                    contest_id=4,
                    index="A",
                    name="Watermelon",
                    rating=800,
                    tags_csv=encode_tags(["math"]),
                ),
            ]
        )
        session.commit()
        owner_id = owner.id
        other_id = other.id

    def override_session() -> Iterator[Session]:
        with Session(engine) as session:
            yield session

    original_user = submissions_routes.session_user_id
    submissions_routes.session_user_id = lambda request: owner_id
    app.dependency_overrides[get_session] = override_session
    try:
        with TestClient(app) as client:
            yield client, owner_id, other_id
    finally:
        submissions_routes.session_user_id = original_user
        app.dependency_overrides.pop(get_session, None)


def test_record_list_and_read_submission(submissions_client) -> None:
    client, _, _ = submissions_client

    created = client.post(
        "/api/problems/4/A/submissions",
        json={"language": "Python 3", "code": "print('hello')\n"},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["contest_id"] == 4
    assert body["index"] == "A"
    assert body["problem_name"] == "Watermelon"
    assert body["language"] == "Python 3"
    assert body["verdict"] == "recorded"
    assert "code" not in body

    listing = client.get("/api/users/me/submissions")
    assert listing.status_code == 200
    page = listing.json()
    assert page["total"] == 1
    assert page["items"] == [body]

    detail = client.get(f"/api/users/me/submissions/{body['id']}")
    assert detail.status_code == 200
    assert detail.json()["code"] == "print('hello')\n"
    assert detail.json()["problem_name"] == "Watermelon"


def test_submissions_are_private_and_validation_is_enforced(
    submissions_client, monkeypatch
) -> None:
    client, _, other_id = submissions_client
    created = client.post(
        "/api/problems/4/A/submissions",
        json={"language": "C++17", "code": "int main() {}"},
    )
    submission_id = created.json()["id"]

    monkeypatch.setattr(submissions_routes, "session_user_id", lambda request: other_id)
    assert client.get("/api/users/me/submissions").json() == {"total": 0, "items": []}
    assert client.get(f"/api/users/me/submissions/{submission_id}").status_code == 404

    monkeypatch.setattr(submissions_routes, "session_user_id", lambda request: None)
    assert client.get("/api/users/me/submissions").status_code == 401
    assert client.get(f"/api/users/me/submissions/{submission_id}").status_code == 401
    assert (
        client.post(
            "/api/problems/4/A/submissions",
            json={"language": "C++17", "code": "int main() {}"},
        ).status_code
        == 401
    )

    monkeypatch.setattr(submissions_routes, "session_user_id", lambda request: 1)
    assert (
        client.post(
            "/api/problems/4/A/submissions",
            json={"language": "   ", "code": "int main() {}"},
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/problems/4/A/submissions",
            json={"language": "C++17", "code": "   \n"},
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/problems/999/Z/submissions",
            json={"language": "C++17", "code": "int main() {}"},
        ).status_code
        == 404
    )


def test_submission_pagination_and_order(submissions_client) -> None:
    client, _, _ = submissions_client
    for language in ["C++17", "Python 3", "Rust"]:
        response = client.post(
            "/api/problems/4/A/submissions",
            json={"language": language, "code": "attempt"},
        )
        assert response.status_code == 201

    first_page = client.get("/api/users/me/submissions", params={"limit": 2}).json()
    assert first_page["total"] == 3
    assert [item["language"] for item in first_page["items"]] == ["Rust", "Python 3"]

    second_page = client.get("/api/users/me/submissions", params={"limit": 2, "offset": 2}).json()
    assert [item["language"] for item in second_page["items"]] == ["C++17"]
