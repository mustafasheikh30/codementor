from pydantic import BaseModel, ConfigDict, Field


class CodeforcesIdentity(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    subject: str = Field(alias="sub")
    handle: str
    rating: int | None = None
    avatar: str | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    handle: str
    rating: int | None
    avatar: str | None
