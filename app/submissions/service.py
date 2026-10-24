from sqlalchemy import and_, func
from sqlmodel import Session, select

from app.problems.models import Problem
from app.submissions.models import Submission
from app.submissions.schemas import SubmissionCreate


def create_submission(
    session: Session,
    *,
    user_id: int,
    contest_id: int,
    index: str,
    payload: SubmissionCreate,
) -> Submission:
    submission = Submission(
        user_id=user_id,
        contest_id=contest_id,
        index=index,
        language=payload.language,
        code=payload.code,
    )
    session.add(submission)
    session.commit()
    session.refresh(submission)
    return submission


def list_submissions(
    session: Session,
    *,
    user_id: int,
    limit: int,
    offset: int,
) -> tuple[list[tuple[Submission, str | None]], int]:
    problem_join = and_(
        Submission.contest_id == Problem.contest_id,
        Submission.index == Problem.index,
    )
    total = session.exec(
        select(func.count()).select_from(Submission).where(Submission.user_id == user_id)
    ).one()
    rows = session.exec(
        select(Submission, Problem.name)
        .outerjoin(Problem, problem_join)
        .where(Submission.user_id == user_id)
        .order_by(Submission.created_at.desc(), Submission.id.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return [(submission, name) for submission, name in rows], total


def get_submission(
    session: Session,
    *,
    user_id: int,
    submission_id: int,
) -> tuple[Submission, str | None] | None:
    problem_join = and_(
        Submission.contest_id == Problem.contest_id,
        Submission.index == Problem.index,
    )
    row = session.exec(
        select(Submission, Problem.name)
        .outerjoin(Problem, problem_join)
        .where(Submission.id == submission_id, Submission.user_id == user_id)
    ).first()
    return (row[0], row[1]) if row is not None else None
