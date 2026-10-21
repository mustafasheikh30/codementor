from collections import Counter

from sqlalchemy import String, cast, func, or_
from sqlmodel import Session, select

from app.problems.models import Problem, encode_tags

SORTS = {
    "newest": (Problem.contest_id.desc(), Problem.index.asc()),
    # Unrated / unknown values always sort last (Postgres would put NULLs first on DESC).
    "rating_asc": (Problem.rating.asc().nulls_last(), Problem.contest_id.desc()),
    "rating_desc": (Problem.rating.desc().nulls_last(), Problem.contest_id.desc()),
    "solved": (Problem.solved_count.desc().nulls_last(), Problem.contest_id.desc()),
}


def list_problems(
    session: Session,
    *,
    q: str = "",
    tag: str = "",
    min_rating: int | None = None,
    max_rating: int | None = None,
    sort: str = "newest",
    page: int = 1,
    page_size: int = 50,
) -> tuple[list[Problem], int]:
    """Return (problems on this page, total matching problems)."""
    stmt = select(Problem)

    if q:
        code = cast(Problem.contest_id, String).concat(Problem.index)  # e.g. "4A"
        stmt = stmt.where(
            or_(Problem.name.icontains(q, autoescape=True), code.icontains(q, autoescape=True))
        )
    if tag:
        stmt = stmt.where(Problem.tags_csv.contains(encode_tags([tag]), autoescape=True))
    if min_rating is not None:
        stmt = stmt.where(Problem.rating >= min_rating)
    if max_rating is not None:
        stmt = stmt.where(Problem.rating <= max_rating)

    total = session.exec(select(func.count()).select_from(stmt.subquery())).one()

    order = SORTS.get(sort, SORTS["newest"])
    stmt = stmt.order_by(*order).offset((page - 1) * page_size).limit(page_size)
    return list(session.exec(stmt).all()), total


def get_problem(session: Session, contest_id: int, index: str) -> Problem | None:
    stmt = select(Problem).where(Problem.contest_id == contest_id, Problem.index == index)
    return session.exec(stmt).first()


def tag_counts(session: Session) -> list[tuple[str, int]]:
    """All tags with how many problems use each, alphabetical."""
    counter: Counter[str] = Counter()
    for csv in session.exec(select(Problem.tags_csv)).all():
        counter.update(t for t in csv.split(",") if t)
    return sorted(counter.items())


def count_problems(session: Session) -> int:
    return session.exec(select(func.count()).select_from(Problem)).one()


def has_sample_data(session: Session) -> bool:
    stmt = select(func.count()).select_from(Problem).where(Problem.source == "sample")
    return session.exec(stmt).one() > 0
