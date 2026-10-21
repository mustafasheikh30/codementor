import pytest
from sqlmodel import Session, select

from app.problems.ingest import IngestError, parse_problemset, upsert_problems
from app.problems.models import Problem

PAYLOAD = {
    "status": "OK",
    "result": {
        "problems": [
            {
                "contestId": 4,
                "index": "A",
                "name": "Watermelon",
                "rating": 800,
                "tags": ["brute force", "math"],
            },
            {"contestId": 5, "index": "B", "name": "No Rating Yet", "tags": []},
            {"index": "X", "name": "Orphan problem without a contest"},
        ],
        "problemStatistics": [
            {"contestId": 4, "index": "A", "solvedCount": 12345},
            {"contestId": 5, "index": "B", "solvedCount": 7},
        ],
    },
}


def test_parse_joins_statistics_and_skips_orphans():
    rows = parse_problemset(PAYLOAD)
    assert len(rows) == 2
    watermelon = rows[0]
    assert watermelon["solved_count"] == 12345
    assert watermelon["tags"] == ["brute force", "math"]
    assert rows[1]["rating"] is None


def test_parse_rejects_failed_status():
    with pytest.raises(IngestError, match="limit exceeded"):
        parse_problemset({"status": "FAILED", "comment": "limit exceeded"})


def test_upsert_is_idempotent_and_updates(session: Session):
    rows = parse_problemset(PAYLOAD)
    assert upsert_problems(session, rows, "codeforces") == (2, 0)
    assert upsert_problems(session, rows, "codeforces") == (0, 2)  # same data: no duplicates

    rows[0]["solved_count"] = 99999
    upsert_problems(session, rows, "codeforces")
    session.expire_all()
    problems = session.exec(select(Problem)).all()
    assert len(problems) == 2
    assert next(p for p in problems if p.contest_id == 4).solved_count == 99999
