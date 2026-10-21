from sqlmodel import Field, SQLModel, UniqueConstraint


def encode_tags(tags: list[str]) -> str:
    """['dp', 'math'] -> ',dp,math,'  (the outer commas make exact-tag LIKE matches easy)."""
    return "," + ",".join(tags) + "," if tags else ","


class Problem(SQLModel, table=True):
    """A Codeforces problem (metadata only; the API does not return statements)."""

    __table_args__ = (UniqueConstraint("contest_id", "index"),)

    id: int | None = Field(default=None, primary_key=True)
    contest_id: int = Field(index=True)
    index: str  # "A", "B1", ...
    name: str = Field(index=True)
    rating: int | None = Field(default=None, index=True)
    tags_csv: str = ","
    solved_count: int | None = None
    source: str = "codeforces"  # "sample" for the bundled demo data

    @property
    def tags(self) -> list[str]:
        return [t for t in self.tags_csv.split(",") if t]

    @property
    def code(self) -> str:
        return f"{self.contest_id}{self.index}"

    @property
    def url(self) -> str:
        return f"https://codeforces.com/problemset/problem/{self.contest_id}/{self.index}"
