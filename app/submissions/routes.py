from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request

from app.core.db import SessionDep
from app.problems import service as problem_service
from app.submissions import service
from app.submissions.models import Submission
from app.submissions.schemas import (
    SubmissionCreate,
    SubmissionDetail,
    SubmissionPage,
    SubmissionRead,
)
from app.users.routes import session_user_id

router = APIRouter(prefix="/api", tags=["submissions"])


def require_user_id(request: Request) -> int:
    user_id = session_user_id(request)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id


def _read(submission: Submission, problem_name: str | None) -> SubmissionRead:
    if submission.id is None:
        raise HTTPException(status_code=500, detail="Submission was not persisted")
    return SubmissionRead(
        id=submission.id,
        contest_id=submission.contest_id,
        index=submission.index,
        problem_name=problem_name,
        language=submission.language,
        verdict=submission.verdict,
        created_at=submission.created_at,
    )


@router.post(
    "/problems/{contest_id}/{index}/submissions",
    response_model=SubmissionRead,
    status_code=201,
)
def create_submission(
    request: Request,
    session: SessionDep,
    contest_id: int,
    index: str,
    payload: SubmissionCreate,
) -> SubmissionRead:
    user_id = require_user_id(request)
    problem = problem_service.get_problem(session, contest_id, index)
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")

    submission = service.create_submission(
        session,
        user_id=user_id,
        contest_id=contest_id,
        index=index,
        payload=payload,
    )
    return _read(submission, problem.name)


@router.get("/users/me/submissions", response_model=SubmissionPage)
def list_submissions(
    request: Request,
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> SubmissionPage:
    user_id = require_user_id(request)
    rows, total = service.list_submissions(
        session,
        user_id=user_id,
        limit=limit,
        offset=offset,
    )
    return SubmissionPage(total=total, items=[_read(submission, name) for submission, name in rows])


@router.get("/users/me/submissions/{submission_id}", response_model=SubmissionDetail)
def get_submission(
    request: Request,
    session: SessionDep,
    submission_id: int,
) -> SubmissionDetail:
    user_id = require_user_id(request)
    found = service.get_submission(session, user_id=user_id, submission_id=submission_id)
    if found is None:
        raise HTTPException(status_code=404, detail="Submission not found")

    submission, problem_name = found
    read = _read(submission, problem_name)
    return SubmissionDetail(**read.model_dump(), code=submission.code)
