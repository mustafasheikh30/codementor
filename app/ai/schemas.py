from pydantic import BaseModel, Field


class HintRequest(BaseModel):
    code: str = Field(min_length=1, max_length=20_000)
    level: int = Field(default=1, ge=1, le=3)


class HintResponse(BaseModel):
    hint: str
