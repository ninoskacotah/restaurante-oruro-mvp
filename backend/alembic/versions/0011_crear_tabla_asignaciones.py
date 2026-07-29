"""Crea la tabla de asignaciones.

Revision ID: 0011_asignaciones
Revises: 0010_comprobantes_pago
Create Date: 2026-07-28
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0011_asignaciones"
down_revision: str | Sequence[str] | None = "0010_comprobantes_pago"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Crea el historial de repartidores asignados a pedidos."""
    op.create_table(
        "asignaciones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pedido_id", sa.Integer(), nullable=False),
        sa.Column("repartidor_id", sa.Integer(), nullable=False),
        sa.Column("activa", sa.Boolean(), nullable=False),
        sa.Column(
            "fecha_asignacion",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "fecha_acuse",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "fecha_cierre",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["pedido_id"],
            ["pedidos.id"],
            name=op.f("fk_asignaciones_pedido_id_pedidos"),
        ),
        sa.ForeignKeyConstraint(
            ["repartidor_id"],
            ["repartidores.id"],
            name=op.f(
                "fk_asignaciones_repartidor_id_repartidores"
            ),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_asignaciones")),
    )
    op.create_index(
        "uq_asignaciones_pedido_activa",
        "asignaciones",
        ["pedido_id"],
        unique=True,
        postgresql_where=sa.text("activa"),
    )


def downgrade() -> None:
    """Elimina únicamente las asignaciones de esta revisión."""
    op.drop_index(
        "uq_asignaciones_pedido_activa",
        table_name="asignaciones",
        postgresql_where=sa.text("activa"),
    )
    op.drop_table("asignaciones")
