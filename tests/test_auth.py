from collections.abc import Iterator
from urllib.parse import parse_qs, urlsplit

import pytest
from authlib.integrations.base_client.errors import OAuthError
from fastapi.testclient import TestClient
from joserfc.errors import JoseError
from pydantic import SecretStr
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.core.config import settings
from app.core.db import get_session
from app.main import app
from app.users import routes
from app.users.schemas import CodeforcesIdentity

# Authlib stores temporary state/nonce data in Starlette's signed session cookie.
# This test-only middleware key is deliberately unrelated to any real credential.
if not any(middleware.cls is SessionMiddleware for middleware in app.user_middleware):
    app.add_middleware(
        SessionMiddleware,
        secret_key="test-only-oidc-state-signing-key-32-bytes",
        session_cookie="codementor_session",
        max_age=14 * 24 * 60 * 60,
        same_site="lax",
        https_only=True,
    )


class FakeUser:
    id = 1
    handle = "test_handle"
    rating = 1500
    avatar = "https://codeforces.org/avatar.png"


class MockCodeforcesClient:
    async def authorize_redirect(self, request: Request, redirect_uri: str) -> RedirectResponse:
        request.session["_state_test"] = {"nonce": "test-nonce"}
        request.session["_authlib_state_test"] = {"redirect_uri": redirect_uri}
        return RedirectResponse(
            "https://codeforces.com/oauth/authorize?state=test-state&nonce=test-nonce"
        )

    async def authorize_access_token(self, request: Request) -> dict[str, object]:
        if request.query_params.get("state") != "test-state":
            raise OAuthError(error="mismatching_state")
        if request.query_params.get("code") == "bad-token":
            raise InvalidIdentityToken
        if request.query_params.get("code") == "missing-handle":
            return {"userinfo": {"sub": "cf-subject-123"}}
        return {
            "userinfo": {
                "sub": "cf-subject-123",
                "handle": "test_handle",
                "rating": 1500,
                "avatar": "https://codeforces.org/avatar.png",
            }
        }


class InvalidIdentityToken(JoseError):
    pass


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setattr(settings, "codeforces_oidc_client_id", "test-client-id")
    monkeypatch.setattr(settings, "codeforces_oidc_client_secret", SecretStr("test-client-secret"))
    monkeypatch.setattr(
        settings,
        "codeforces_oidc_state_secret",
        SecretStr("test-state-secret-with-more-than-32-chars"),
    )
    monkeypatch.setattr(
        settings,
        "codeforces_oidc_redirect_uri",
        "https://testserver/api/auth/callback",
    )

    fake_user = FakeUser()

    def fake_upsert(session: object, identity: CodeforcesIdentity) -> FakeUser:
        assert identity.subject == "cf-subject-123"
        return fake_user

    def fake_get_user(session: object, user_id: int) -> FakeUser | None:
        return fake_user if user_id == fake_user.id else None

    monkeypatch.setattr(routes, "codeforces_client", lambda: MockCodeforcesClient())
    monkeypatch.setattr(routes.service, "upsert_user", fake_upsert)
    monkeypatch.setattr(routes.service, "get_user_by_id", fake_get_user)
    app.dependency_overrides[get_session] = lambda: object()

    try:
        with TestClient(app, base_url="https://testserver") as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_session, None)


def test_auth_routes_are_registered() -> None:
    paths = app.openapi()["paths"]
    assert "/api/auth/login" in paths
    assert "/api/auth/callback" in paths
    assert "/api/auth/me" in paths
    assert "/api/auth/logout" in paths


def test_login_redirect_uses_fixed_callback_and_safe_return_path(client: TestClient) -> None:
    response = client.get(
        "/api/auth/login",
        params={"return_to": "//evil.example"},
        follow_redirects=False,
    )

    assert response.status_code == 307
    params = parse_qs(urlsplit(response.headers["location"]).query)
    assert params["state"] == ["test-state"]
    assert params["nonce"] == ["test-nonce"]
    # The fake provider client sees the single callback value configured above.
    assert settings.codeforces_oidc_redirect_uri == "https://testserver/api/auth/callback"


def test_callback_persists_session_and_does_not_expose_tokens(client: TestClient) -> None:
    client.get("/api/auth/login")
    response = client.get(
        "/api/auth/callback",
        params={"code": "valid-code", "state": "test-state"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert urlsplit(response.headers["location"]).path == "/problemset"
    cookie = response.headers["set-cookie"]
    assert "codementor_session=" in cookie
    assert "httponly" in cookie.lower()
    assert "samesite=lax" in cookie.lower()
    assert "Max-Age=1209600" in cookie
    assert "secure" in cookie.lower()

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json() == {
        "id": 1,
        "handle": "test_handle",
        "rating": 1500,
        "avatar": "https://codeforces.org/avatar.png",
    }
    assert "access_token" not in me.text
    assert "id_token" not in me.text


def test_me_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_logout_clears_the_session(client: TestClient) -> None:
    client.get("/api/auth/login")
    client.get(
        "/api/auth/callback",
        params={"code": "valid-code", "state": "test-state"},
    )
    assert client.get("/api/auth/me").status_code == 200

    logout = client.post("/api/auth/logout")

    assert logout.status_code == 204
    assert client.get("/api/auth/me").status_code == 401


def test_callback_rejects_invalid_state(client: TestClient) -> None:
    client.get("/api/auth/login")
    response = client.get(
        "/api/auth/callback",
        params={"code": "valid-code", "state": "attacker-state"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Codeforces authorization failed"


def test_callback_rejects_invalid_identity_token(client: TestClient) -> None:
    client.get("/api/auth/login")
    response = client.get(
        "/api/auth/callback",
        params={"code": "bad-token", "state": "test-state"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Codeforces identity token is invalid"


def test_callback_rejects_identity_without_required_claims(client: TestClient) -> None:
    client.get("/api/auth/login")
    response = client.get(
        "/api/auth/callback",
        params={"code": "missing-handle", "state": "test-state"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Codeforces identity token is missing required claims"


def test_login_is_unavailable_without_provider_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "codeforces_oidc_client_secret", SecretStr(""))
    with TestClient(app, base_url="https://testserver") as test_client:
        response = test_client.get("/api/auth/login")

    assert response.status_code == 503


def test_login_is_unavailable_without_redirect_uri(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "codeforces_oidc_redirect_uri", "")

    assert client.get("/api/auth/login").status_code == 503


@pytest.mark.parametrize(
    "return_to",
    ["https://evil.example", "//evil.example", "\\\\evil.example", "", "\n/problemset"],
)
def test_unsafe_return_path_falls_back_to_problemset(client: TestClient, return_to: str) -> None:
    client.get("/api/auth/login", params={"return_to": return_to})
    response = client.get(
        "/api/auth/callback",
        params={"code": "valid-code", "state": "test-state"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert urlsplit(response.headers["location"]).path == "/problemset"


def test_safe_return_path_is_preserved(client: TestClient) -> None:
    client.get("/api/auth/login", params={"return_to": "/problemset?tag=dp"})
    response = client.get(
        "/api/auth/callback",
        params={"code": "valid-code", "state": "test-state"},
        follow_redirects=False,
    )

    location = urlsplit(response.headers["location"])
    assert location.path == "/problemset"
    assert parse_qs(location.query) == {"tag": ["dp"]}
