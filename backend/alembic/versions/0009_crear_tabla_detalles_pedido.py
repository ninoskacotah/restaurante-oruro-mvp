"""Crea la tabla de detalles del pedido.

Revision ID: 0009_detalles_pedido
Revises: 0008_pedidos
Create Date: 2026-07-28
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0009_detalles_pedido"
down_revision: str | Sequence[str] | None = "0008_pedidos"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Crea los renglones históricos asociados con cada pedido."""
    op.create_table(
        "detalles_pedido",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pedido_id", sa.Integer(), nullable=False),
        sa.Column("plato_id", sa.Integer(), nullable=False),
        sa.Column(
            "nombre_plato",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "precio_unitario",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
        ),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column(
            "subtotal",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
        ),
        sa.CheckConstraint(
            "precio_unitario >= 0",
            name=op.f("ck_detalles_pedido_precio_unitario"),
        ),
        sa.CheckConstraint(
            "cantidad > 0",
            name=op.f("ck_detalles_pedido_cantidad"),
        ),
        sa.CheckConstraint(
            "subtotal >= 0",
            name=op.f("ck_detalles_pedido_subtotal"),
        ),
        sa.ForeignKeyConstraint(
            ["pedido_id"],
            ["pedidos.id"],
            name=op.f("fk_detalles_pedido_pedido_id_pedidos"),
        ),
        sa.ForeignKeyConstraint(
            ["plato_id"],
            ["platos.id"],
            name=op.f("fk_detalles_pedido_plato_id_platos"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_detalles_pedido")),
    )


def downgrade() -> None:
    """Elimina únicamente los detalles creados por esta revisión."""
    op.drop_table("detalles_pedido")
