"""create submissions table

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-24 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0004"
down_revision: Union[str, Sequence[str], None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "submissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("contest_id", sa.Integer(), nullable=False),
        sa.Column("index", sa.String(), nullable=False),
        sa.Column("language", sa.String(), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("verdict", sa.String(), nullable=False, server_default="recorded"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_submissions_user_id"), "submissions", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_submissions_contest_id"),
        "submissions",
        ["contest_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_submissions_created_at"),
        "submissions",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_submissions_created_at"), table_name="submissions")
    op.drop_index(op.f("ix_submissions_contest_id"), table_name="submissions")
    op.drop_index(op.f("ix_submissions_user_id"), table_name="submissions")
    op.drop_table("submissions")
