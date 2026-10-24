"""DB-free service checks for recorded submissions."""

from collections.abc import Iterator

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.problems.models import Problem, encode_tags
from app.submissions import service
from app.submissions.schemas import SubmissionCreate
from app.users.models import User


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all(
            [
                User(codeforces_subject="cf-one", handle="one", rating=1400),
                User(codeforces_subject="cf-two", handle="two", rating=1500),
                Problem(
                    contest_id=4,
                    index="A",
                    name="Watermelon",
                    rating=800,
                    tags_csv=encode_tags(["math"]),
                ),
            ]
        )
        session.commit()
        yield session


def _ids(session: Session) -> tuple[int, int]:
    one = session.exec(select(User).where(User.handle == "one")).one()
    two = session.exec(select(User).where(User.handle == "two")).one()
    assert one.id is not None and two.id is not None
    return one.id, two.id


def test_create_list_and_get_are_scoped_to_the_owner(session: Session) -> None:
    one_id, two_id = _ids(session)
    payload = SubmissionCreate(language=" Python 3 ", code="print(1)\n")

    first = service.create_submission(
        session,
        user_id=one_id,
        contest_id=4,
        index="A",
        payload=payload,
    )
    second = service.create_submission(
        session,
        user_id=one_id,
        contest_id=4,
        index="A",
        payload=SubmissionCreate(language="C++17", code="int main() {}"),
    )

    assert first.id is not None and second.id is not None
    assert first.language == "Python 3"
    assert first.code == "print(1)\n"
    assert first.verdict == "recorded"

    rows, total = service.list_submissions(session, user_id=one_id, limit=20, offset=0)
    assert total == 2
    assert [submission.id for submission, _ in rows] == [second.id, first.id]
    assert all(name == "Watermelon" for _, name in rows)

    found = service.get_submission(session, user_id=one_id, submission_id=first.id)
    assert found is not None
    assert found[0].code == "print(1)\n"
    assert found[1] == "Watermelon"

    assert service.get_submission(session, user_id=two_id, submission_id=first.id) is None
    other_rows, other_total = service.list_submissions(session, user_id=two_id, limit=20, offset=0)
    assert other_total == 0
    assert other_rows == []
