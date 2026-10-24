from datetime import datetime

from pydantic import BaseModel, Field, field_validator

MAX_CODE_LENGTH = 200_000
MAX_LANGUAGE_LENGTH = 64


class SubmissionCreate(BaseModel):
    language: str = Field(min_length=1, max_length=MAX_LANGUAGE_LENGTH)
    code: str = Field(min_length=1, max_length=MAX_CODE_LENGTH)

    @field_validator("language")
    @classmethod
    def clean_language(cls, value: str) -> str:
        language = value.strip()
        if not language:
            raise ValueError("language must not be blank")
        return language

    @field_validator("code")
    @classmethod
    def code_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("code must not be blank")
        return value


class SubmissionRead(BaseModel):
    id: int
    contest_id: int
    index: str
    problem_name: str | None
    language: str
    verdict: str
    created_at: datetime


class SubmissionDetail(SubmissionRead):
    code: str


class SubmissionPage(BaseModel):
    total: int
    items: list[SubmissionRead]
