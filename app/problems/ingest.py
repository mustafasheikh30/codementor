"""Load Codeforces problems into the database.

Usage (from the project root):
    uv run python -m app.problems.ingest                    # fetch from the Codeforces API
    uv run python -m app.problems.ingest --from-file x.json # use a saved API response
    uv run python -m app.problems.ingest --seed             # load the small bundled sample set
"""

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

import httpx
from sqlmodel import Session, select

from app.core.db import engine
from app.problems.models import Problem, encode_tags

CF_URL = "https://codeforces.com/api/problemset.problems"
SAMPLE_FILE = Path(__file__).resolve().parents[2] / "data" / "sample_problems.json"


class IngestError(Exception):
    pass


def parse_problemset(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Turn the raw API response into a flat list of problem dicts.

    The API returns two parallel lists: `problems` (metadata) and `problemStatistics`
    (solved counts). We join them on (contestId, index).
    """
    if payload.get("status") != "OK":
        raise IngestError(payload.get("comment", "Codeforces API returned a non-OK status"))

    result = payload["result"]
    solved = {
        (s["contestId"], s["index"]): s.get("solvedCount")
        for s in result.get("problemStatistics", [])
        if "contestId" in s
    }

    rows = []
    for p in result["problems"]:
        if "contestId" not in p:  # a few problems aren't attached to a contest
            continue
        key = (p["contestId"], p["index"])
        rows.append(
            {
                "contest_id": p["contestId"],
                "index": p["index"],
                "name": p["name"],
                "rating": p.get("rating"),
                "tags": p.get("tags", []),
                "solved_count": solved.get(key),
            }
        )
    return rows


async def fetch_problemset() -> dict[str, Any]:
    """One request to the public Codeforces API (it asks for at most 1 request / 2 s)."""
    headers = {"User-Agent": "CodeMentor/0.1 (personal learning project)"}
    async with httpx.AsyncClient(timeout=30, headers=headers) as client:
        response = await client.get(CF_URL)
        response.raise_for_status()
        return response.json()


def upsert_problems(session: Session, rows: list[dict[str, Any]], source: str) -> tuple[int, int]:
    """Insert new problems and update existing ones. Returns (inserted, updated)."""
    existing = {(p.contest_id, p.index): p for p in session.exec(select(Problem)).all()}
    inserted = updated = 0

    for row in rows:
        key = (row["contest_id"], row["index"])
        values = {
            "name": row["name"],
            "rating": row["rating"],
            "tags_csv": encode_tags(row["tags"]),
            "solved_count": row["solved_count"],
            "source": source,
        }
        problem = existing.get(key)
        if problem is None:
            session.add(Problem(contest_id=key[0], index=key[1], **values))
            inserted += 1
        else:
            for field, value in values.items():
                setattr(problem, field, value)
            updated += 1

    session.commit()
    return inserted, updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Load Codeforces problems into the database")
    parser.add_argument("--seed", action="store_true", help="load the bundled sample data")
    parser.add_argument("--from-file", type=Path, help="load a saved API response (JSON)")
    args = parser.parse_args()

    if args.seed:
        data = json.loads(SAMPLE_FILE.read_text())
        rows, source = data["problems"], "sample"
    elif args.from_file:
        rows, source = parse_problemset(json.loads(args.from_file.read_text())), "codeforces"
    else:
        print("Fetching problems from Codeforces...")
        rows, source = parse_problemset(asyncio.run(fetch_problemset())), "codeforces"

    with Session(engine) as session:
        inserted, updated = upsert_problems(session, rows, source)
    print(f"Done: {inserted} inserted, {updated} updated ({len(rows)} problems).")


if __name__ == "__main__":
    main()
