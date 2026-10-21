from pydantic import BaseModel, ConfigDict


class ProblemRead(BaseModel):
    """What the JSON API returns for one problem."""

    model_config = ConfigDict(from_attributes=True)  # lets us build it from a DB object

    contest_id: int
    index: str
    name: str
    rating: int | None
    tags: list[str]
    solved_count: int | None
    url: str


class ProblemPage(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ProblemRead]


class TagCount(BaseModel):
    tag: str
    count: int


class Meta(BaseModel):
    problem_count: int
    has_sample_data: bool
