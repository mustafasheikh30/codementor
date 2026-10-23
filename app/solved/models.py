from sqlmodel import Field, SQLModel


class UserProblemSolved(SQLModel, table=True):
    __tablename__ = "user_problem_solved"

    user_id: int = Field(foreign_key="users.id", primary_key=True)
    contest_id: int = Field(primary_key=True)
    index: str = Field(primary_key=True)
