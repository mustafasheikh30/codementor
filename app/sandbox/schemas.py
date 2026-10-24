from pydantic import BaseModel, Field, field_validator


class ExecutionRequest(BaseModel):
    language: str = Field(min_length=1, max_length=64)
    code: str = Field(min_length=1, max_length=200_000)
    stdin: str = ""
    time_limit_seconds: float = Field(default=2.0, ge=0.1, le=10.0)
    memory_limit_mb: int = Field(default=256, ge=32, le=1024)

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


class ExecutionResult(BaseModel):
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    time_ms: int | None = None
    memory_kb: int | None = None
    status: str = "ok"  # ok, timeout, memory, compile_error, runtime_error, disabled
    message: str | None = None
