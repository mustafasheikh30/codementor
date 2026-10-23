from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    codeforces_subject: str = Field(index=True, unique=True)
    handle: str = Field(index=True)
    rating: int | None = None
    avatar: str | None = None
