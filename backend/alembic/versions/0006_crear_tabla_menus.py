"""Crea la tabla de menús.

Revision ID: 0006_menus
Revises: 0005_platos
Create Date: 2026-07-28
"""

from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = "0006_menus"
down_revision: str | Sequence[str] | None = "0005_platos"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Crea la programación diaria de menús."""
    op.create_table(
        "menus",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column(
            "activo",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_menus")),
        sa.UniqueConstraint("fecha", name=op.f("uq_menus_fecha")),
    )


def downgrade() -> None:
    """Elimina la tabla incorporada."""
    op.drop_table("menus")
