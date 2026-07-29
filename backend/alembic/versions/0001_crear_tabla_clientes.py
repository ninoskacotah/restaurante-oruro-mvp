"""Crea la tabla de clientes.

Revision ID: 0001_clientes
Revises:
Create Date: 2026-07-28
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0001_clientes"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crea el perfil persistente mínimo del cliente."""
    op.create_table(
        "clientes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("chat_id", sa.String(), nullable=False),
        sa.Column("nombre", sa.String(), nullable=True),
        sa.Column("telefono", sa.String(), nullable=True),
        sa.Column(
            "fecha_registro",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_clientes")),
        sa.UniqueConstraint("chat_id", name=op.f("uq_clientes_chat_id")),
    )


def downgrade() -> None:
    """Elimina la tabla incorporada por esta revisión."""
    op.drop_table("clientes")
