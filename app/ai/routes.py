from fastapi import APIRouter, HTTPException, Request

from app.ai import service
from app.ai.schemas import HintRequest, HintResponse
from app.core.db import SessionDep
from app.problems import service as problem_service
from app.users.routes import session_user_id

router = APIRouter(prefix="/api/coach", tags=["coach"])


@router.post("/hint", response_model=HintResponse)
def hint(
    request: Request,
    session: SessionDep,
    contest_id: int,
    index: str,
    body: HintRequest,
) -> HintResponse:
    user_id = session_user_id(request)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Sign in to use the coach")

    problem = problem_service.get_problem(session, contest_id, index)
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")

    try:
        text = service.generate_hint(
            name=problem.name,
            rating=problem.rating,
            tags=problem.tags,
            code=body.code,
            level=body.level,
        )
    except service.AiNotConfigured as exc:
        raise HTTPException(status_code=503, detail="The coach is not configured") from exc
    except service.AiUpstreamError as exc:
        # Never forward provider response bodies: they can contain account details.
        raise HTTPException(status_code=502, detail="The coach is temporarily unavailable") from exc

    return HintResponse(hint=text)
