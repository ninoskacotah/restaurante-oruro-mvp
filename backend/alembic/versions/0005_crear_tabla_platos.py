"""Crea la tabla de platos.

Revision ID: 0005_platos
Revises: 0004_tokens_revocados
Create Date: 2026-07-28
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0005_platos"
down_revision: str | Sequence[str] | None = "0004_tokens_revocados"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crea el catálogo persistente de platos."""
    op.create_table(
        "platos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(), nullable=False),
        sa.Column("descripcion", sa.String(), nullable=True),
        sa.Column("precio", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "activo",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "precio >= 0",
            name=op.f("ck_platos_precio"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_platos")),
    )


def downgrade() -> None:
    """Elimina la tabla incorporada por esta revisión."""
    op.drop_table("platos")
