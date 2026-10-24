from datetime import UTC, datetime

from sqlalchemy import DateTime, Text
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(UTC)


class Submission(SQLModel, table=True):
    """A recorded code attempt. Code is stored for later analysis and is never executed here."""

    __tablename__ = "submissions"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    contest_id: int = Field(index=True)
    index: str
    language: str = Field(max_length=64)
    code: str = Field(sa_type=Text)
    verdict: str = Field(default="recorded", max_length=32)
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
        index=True,
    )
