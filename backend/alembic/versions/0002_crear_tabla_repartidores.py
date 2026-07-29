"""Crea la tabla de repartidores.

Revision ID: 0002_repartidores
Revises: 0001_clientes
Create Date: 2026-07-28
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0002_repartidores"
down_revision: str | Sequence[str] | None = "0001_clientes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crea el perfil persistente del repartidor."""
    op.create_table(
        "repartidores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("chat_id", sa.String(), nullable=False),
        sa.Column("nombre", sa.String(), nullable=True),
        sa.Column("telefono", sa.String(), nullable=True),
        sa.Column(
            "activo",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        sa.Column(
            "fecha_registro",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_repartidores")),
        sa.UniqueConstraint(
            "chat_id",
            name=op.f("uq_repartidores_chat_id"),
        ),
    )


def downgrade() -> None:
    """Elimina la tabla incorporada por esta revisión."""
    op.drop_table("repartidores")
