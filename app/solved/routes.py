from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import func
from sqlmodel import select

from app.core.db import SessionDep
from app.problems import service as problem_service
from app.problems.models import Problem
from app.solved.models import UserProblemSolved
from app.solved.schemas import (
    DifficultyBucket,
    SolvedCount,
    SolvedProblem,
    SolvedStatus,
    UserProgress,
)
from app.users.routes import session_user_id

router = APIRouter(prefix="/api", tags=["solved"])


def require_user_id(request: Request) -> int:
    user_id = session_user_id(request)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id


@router.get("/users/me/solved", response_model=list[SolvedProblem])
def list_solved(request: Request, session: SessionDep) -> list[SolvedProblem]:
    user_id = require_user_id(request)
    rows = session.exec(
        select(UserProblemSolved.contest_id, UserProblemSolved.index).where(
            UserProblemSolved.user_id == user_id
        )
    ).all()
    return [SolvedProblem(contest_id=c, index=i) for (c, i) in rows]


@router.get("/problems/{contest_id}/{index}/solved", response_model=SolvedStatus)
def solved_status(
    request: Request, session: SessionDep, contest_id: int, index: str
) -> SolvedStatus:
    user_id = session_user_id(request)
    if user_id is None:
        return SolvedStatus(solved=False)
    row = session.get(UserProblemSolved, (user_id, contest_id, index))
    return SolvedStatus(solved=row is not None)


@router.post("/problems/{contest_id}/{index}/solved", response_model=SolvedStatus)
def mark_solved(request: Request, session: SessionDep, contest_id: int, index: str) -> SolvedStatus:
    user_id = require_user_id(request)
    problem = problem_service.get_problem(session, contest_id, index)
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")

    row = session.get(UserProblemSolved, (user_id, contest_id, index))
    if row is None:
        session.add(UserProblemSolved(user_id=user_id, contest_id=contest_id, index=index))
        session.commit()
    return SolvedStatus(solved=True)


@router.delete("/problems/{contest_id}/{index}/solved", response_model=SolvedStatus)
def unmark_solved(
    request: Request, session: SessionDep, contest_id: int, index: str
) -> SolvedStatus:
    user_id = require_user_id(request)
    row = session.get(UserProblemSolved, (user_id, contest_id, index))
    if row is not None:
        session.delete(row)
        session.commit()
    return SolvedStatus(solved=False)


@router.get("/users/me/solved/count", response_model=SolvedCount)
def solved_count(request: Request, session: SessionDep) -> SolvedCount:
    user_id = require_user_id(request)
    count = session.exec(
        select(func.count())
        .select_from(UserProblemSolved)
        .where(UserProblemSolved.user_id == user_id)
    ).one()
    return SolvedCount(count=count)


@router.get("/users/me/progress", response_model=UserProgress)
def progress(request: Request, session: SessionDep) -> UserProgress:
    user_id = require_user_id(request)
    solved_count = session.exec(
        select(func.count())
        .select_from(UserProblemSolved)
        .where(UserProblemSolved.user_id == user_id)
    ).one()
    rows = session.exec(
        select(Problem.rating, func.count())
        .join(
            UserProblemSolved,
            (UserProblemSolved.contest_id == Problem.contest_id)
            & (UserProblemSolved.index == Problem.index),
        )
        .where(UserProblemSolved.user_id == user_id)
        .group_by(Problem.rating)
        .order_by(Problem.rating.nulls_last())
    ).all()
    return UserProgress(
        solved_count=solved_count,
        by_difficulty=[DifficultyBucket(rating=r, count=c) for r, c in rows],
    )
