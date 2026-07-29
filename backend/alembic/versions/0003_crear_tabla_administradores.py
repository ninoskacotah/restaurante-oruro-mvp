"""Crea la tabla de administradores.

Revision ID: 0003_administradores
Revises: 0002_repartidores
Create Date: 2026-07-28
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0003_administradores"
down_revision: str | Sequence[str] | None = "0002_repartidores"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crea la identidad persistente del administrador."""
    op.create_table(
        "administradores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre_usuario", sa.String(), nullable=False),
        sa.Column("credencial_hash", sa.String(), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_administradores")),
        sa.UniqueConstraint(
            "nombre_usuario",
            name=op.f("uq_administradores_nombre_usuario"),
        ),
    )


def downgrade() -> None:
    """Elimina la tabla incorporada por esta revisión."""
    op.drop_table("administradores")
