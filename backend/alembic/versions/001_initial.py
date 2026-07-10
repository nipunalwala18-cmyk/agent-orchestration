"""Initial migrations

Revision ID: 001_initial
Revises:
Create Date: 2026-07-10 19:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create health_checks table
    op.create_table(
        "health_checks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_health_checks_id"), "health_checks", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_health_checks_id"), table_name="health_checks")
    op.drop_table("health_checks")
