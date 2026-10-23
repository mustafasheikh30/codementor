from typing import Annotated
from urllib.parse import urlsplit

from authlib.integrations.base_client.errors import OAuthError
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from joserfc.errors import JoseError
from pydantic import ValidationError
from starlette.responses import Response

from app.core.config import settings
from app.core.db import SessionDep
from app.users import service
from app.users.oidc import codeforces_client
from app.users.schemas import CodeforcesIdentity, UserRead

router = APIRouter(prefix="/api/auth", tags=["authentication"])


def safe_return_path(path: str) -> str:
    """Accept only a same-site absolute path; reject host and scheme redirects."""
    parsed = urlsplit(path)
    if (
        not path.startswith("/")
        or path.startswith("//")
        or parsed.scheme
        or parsed.netloc
        or "\\" in path
        or len(path) > 2048
        or any(ord(char) < 32 or ord(char) == 127 for char in path)
    ):
        return "/problemset"
    return path


def ensure_oidc_is_configured(request: Request) -> None:
    redirect = urlsplit(settings.codeforces_oidc_redirect_uri)
    if not (
        settings.codeforces_oidc_client_id
        and settings.codeforces_oidc_client_secret.get_secret_value()
        and settings.codeforces_oidc_state_secret.get_secret_value()
        and redirect.scheme in {"http", "https"}
        and redirect.netloc
        and "session" in request.scope
    ):
        raise HTTPException(status_code=503, detail="Codeforces sign-in is not configured")


def session_user_id(request: Request) -> int | None:
    if "session" not in request.scope:
        return None
    user_id = request.session.get("user_id")
    return user_id if type(user_id) is int else None


@router.get("/login", name="codeforces_login")
async def login(
    request: Request,
    return_to: Annotated[str, Query()] = "/problemset",
) -> Response:
    ensure_oidc_is_configured(request)
    request.session["return_to"] = safe_return_path(return_to)
    client = codeforces_client()
    return await client.authorize_redirect(
        request,
        redirect_uri=settings.codeforces_oidc_redirect_uri,
    )


@router.get("/callback", name="codeforces_callback")
async def callback(request: Request, session: SessionDep) -> Response:
    ensure_oidc_is_configured(request)
    client = codeforces_client()

    try:
        token = await client.authorize_access_token(request)
    except OAuthError as exc:
        raise HTTPException(status_code=400, detail="Codeforces authorization failed") from exc
    except JoseError as exc:
        # Do not return token details or weaken signature and claim checks.
        raise HTTPException(status_code=400, detail="Codeforces identity token is invalid") from exc

    try:
        identity = CodeforcesIdentity.model_validate(token.get("userinfo"))
    except ValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail="Codeforces identity token is missing required claims",
        ) from exc

    user = service.upsert_user(session, identity)
    if user.id is None:
        raise HTTPException(status_code=500, detail="Could not create the Codeforces account")

    request.session["user_id"] = user.id
    raw_return_to = request.session.pop("return_to", "/problemset")
    return_to = safe_return_path(raw_return_to if isinstance(raw_return_to, str) else "/problemset")
    return RedirectResponse(return_to, status_code=303)


@router.get("/me", response_model=UserRead)
def me(request: Request, session: SessionDep) -> UserRead:
    user_id = session_user_id(request)
    user = service.get_user_by_id(session, user_id) if user_id is not None else None
    if user is None:
        if "session" in request.scope:
            request.session.pop("user_id", None)
        raise HTTPException(status_code=401, detail="Not authenticated")
    return UserRead.model_validate(user)


@router.post("/logout", status_code=204)
def logout(request: Request) -> Response:
    if "session" in request.scope:
        request.session.clear()
    return Response(status_code=204)
