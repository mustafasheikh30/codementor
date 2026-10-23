"""create users table

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-23 20:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, Sequence[str], None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "codeforces_subject",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        ),
        sa.Column("handle", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("avatar", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_users_codeforces_subject"),
        "users",
        ["codeforces_subject"],
        unique=True,
    )
    op.create_index(op.f("ix_users_handle"), "users", ["handle"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_users_handle"), table_name="users")
    op.drop_index(op.f("ix_users_codeforces_subject"), table_name="users")
    op.drop_table("users")
