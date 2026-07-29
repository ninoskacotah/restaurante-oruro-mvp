"""Crea la tabla de pedidos.

Revision ID: 0008_pedidos
Revises: 0007_detalles_menu
Create Date: 2026-07-28
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0008_pedidos"
down_revision: str | Sequence[str] | None = "0007_detalles_menu"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Crea la cabecera persistente vinculada con el cliente."""
    op.create_table(
        "pedidos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cliente_id", sa.Integer(), nullable=False),
        sa.Column("codigo_seguimiento", sa.String(length=32), nullable=True),
        sa.Column(
            "estado_actual",
            sa.String(length=30),
            server_default=sa.text("'BORRADOR'"),
            nullable=False,
        ),
        sa.Column(
            "total",
            sa.Numeric(precision=10, scale=2),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "entrega_latitud",
            sa.Numeric(precision=9, scale=6),
            nullable=True,
        ),
        sa.Column(
            "entrega_longitud",
            sa.Numeric(precision=9, scale=6),
            nullable=True,
        ),
        sa.Column(
            "referencia_entrega",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("total >= 0", name=op.f("ck_pedidos_total")),
        sa.ForeignKeyConstraint(
            ["cliente_id"],
            ["clientes.id"],
            name=op.f("fk_pedidos_cliente_id_clientes"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_pedidos")),
        sa.UniqueConstraint(
            "codigo_seguimiento",
            name=op.f("uq_pedidos_codigo_seguimiento"),
        ),
    )


def downgrade() -> None:
    """Elimina únicamente la tabla creada por esta revisión."""
    op.drop_table("pedidos")
