from fastapi import FastAPI

from app.core.config import settings
from app.problems.routes import router as problems_router

# Everything lives under /api so one reverse proxy rule (/api -> this app) is enough
# in production, and the Angular app owns every other URL.
app = FastAPI(
    title=settings.app_name,
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)
app.include_router(problems_router)


@app.get("/api/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
