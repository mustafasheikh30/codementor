from urllib.parse import urlsplit

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.ai.routes import router as ai_router
from app.core.config import settings
from app.problems.routes import router as problems_router
from app.solved.routes import router as solved_router
from app.users.routes import router as users_router

# Everything lives under /api so one reverse proxy rule (/api -> this app) is enough
# in production, and the Angular app owns every other URL.
app = FastAPI(
    title=settings.app_name,
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)
app.include_router(problems_router)
app.include_router(users_router)
app.include_router(solved_router)
app.include_router(ai_router)

# Authlib keeps temporary OIDC state/nonce values in a signed session cookie.
# Install the middleware only when sign-in is configured; otherwise /api/auth/*
# returns 503 without requiring a session secret at startup.
_oidc_redirect = urlsplit(settings.codeforces_oidc_redirect_uri)
if (
    settings.codeforces_oidc_state_secret.get_secret_value()
    and _oidc_redirect.scheme in {"http", "https"}
    and _oidc_redirect.netloc
):
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.codeforces_oidc_state_secret.get_secret_value(),
        session_cookie="codementor_session",
        max_age=14 * 24 * 60 * 60,
        same_site="lax",
        https_only=_oidc_redirect.scheme == "https",
    )


@app.get("/api/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
