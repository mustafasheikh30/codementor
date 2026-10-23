from pydantic import BaseModel


class SolvedProblem(BaseModel):
    contest_id: int
    index: str


class SolvedStatus(BaseModel):
    solved: bool


class SolvedCount(BaseModel):
    count: int


class DifficultyBucket(BaseModel):
    rating: int | None
    count: int


class UserProgress(BaseModel):
    solved_count: int
    by_difficulty: list[DifficultyBucket]
