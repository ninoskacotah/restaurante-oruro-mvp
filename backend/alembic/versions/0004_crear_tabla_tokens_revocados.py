"""Crea la tabla de tokens revocados.

Revision ID: 0004_tokens_revocados
Revises: 0003_administradores
Create Date: 2026-07-28
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0004_tokens_revocados"
down_revision: str | Sequence[str] | None = "0003_administradores"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crea el registro persistente de identificadores revocados."""
    op.create_table(
        "tokens_revocados",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("administrador_id", sa.Integer(), nullable=False),
        sa.Column("jti", sa.String(), nullable=False),
        sa.Column(
            "fecha_revocacion",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "fecha_expiracion",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["administrador_id"],
            ["administradores.id"],
            name=op.f(
                "fk_tokens_revocados_administrador_id_administradores"
            ),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tokens_revocados")),
        sa.UniqueConstraint("jti", name=op.f("uq_tokens_revocados_jti")),
    )


def downgrade() -> None:
    """Elimina la tabla incorporada por esta revisión."""
    op.drop_table("tokens_revocados")
