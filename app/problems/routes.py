from fastapi import APIRouter, HTTPException, Query

from app.core.db import SessionDep
from app.problems import service
from app.problems.schemas import Meta, ProblemPage, ProblemRead, TagCount

router = APIRouter(prefix="/api", tags=["problems"])


# These are plain `def` (not `async def`) on purpose: the DB driver is synchronous, and
# FastAPI runs plain `def` routes in a thread pool so they don't block the event loop.
@router.get("/problems", response_model=ProblemPage)
def list_problems(
    session: SessionDep,
    q: str = "",
    tag: str = "",
    min_rating: int | None = None,
    max_rating: int | None = None,
    sort: str = "newest",
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
) -> ProblemPage:
    items, total = service.list_problems(
        session,
        q=q.strip(),
        tag=tag,
        min_rating=min_rating,
        max_rating=max_rating,
        sort=sort,
        page=page,
        page_size=page_size,
    )
    return ProblemPage(
        total=total,
        page=page,
        page_size=page_size,
        items=[ProblemRead.model_validate(p) for p in items],
    )


@router.get("/problems/tags", response_model=list[TagCount])
def list_tags(session: SessionDep) -> list[TagCount]:
    return [TagCount(tag=t, count=c) for t, c in service.tag_counts(session)]


@router.get("/problems/{contest_id}/{index}", response_model=ProblemRead)
def get_problem(contest_id: int, index: str, session: SessionDep) -> ProblemRead:
    problem = service.get_problem(session, contest_id, index)
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    return ProblemRead.model_validate(problem)


@router.get("/meta", response_model=Meta)
def meta(session: SessionDep) -> Meta:
    return Meta(
        problem_count=service.count_problems(session),
        has_sample_data=service.has_sample_data(session),
    )
