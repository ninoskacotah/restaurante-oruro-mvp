"""Crea la tabla del historial de estados.

Revision ID: 0014_historial_estados
Revises: 0013_evidencias_entrega
Create Date: 2026-07-28
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0014_historial_estados"
down_revision: str | Sequence[str] | None = "0013_evidencias_entrega"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Crea el registro acumulativo de eventos de cada pedido."""
    op.create_table(
        "historial_estados",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pedido_id", sa.Integer(), nullable=False),
        sa.Column("cliente_id", sa.Integer(), nullable=True),
        sa.Column("repartidor_id", sa.Integer(), nullable=True),
        sa.Column("administrador_id", sa.Integer(), nullable=True),
        sa.Column(
            "estado_anterior",
            sa.String(length=30),
            nullable=True,
        ),
        sa.Column(
            "estado_nuevo",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column("evento", sa.String(length=50), nullable=False),
        sa.Column("origen", sa.String(length=20), nullable=False),
        sa.Column(
            "fecha_registro",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "num_nonnulls(cliente_id, repartidor_id, administrador_id) <= 1",
            name=op.f("ck_historial_estados_un_actor"),
        ),
        sa.ForeignKeyConstraint(
            ["administrador_id"],
            ["administradores.id"],
            name=op.f(
                "fk_historial_estados_administrador_id_administradores"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["cliente_id"],
            ["clientes.id"],
            name=op.f("fk_historial_estados_cliente_id_clientes"),
        ),
        sa.ForeignKeyConstraint(
            ["pedido_id"],
            ["pedidos.id"],
            name=op.f("fk_historial_estados_pedido_id_pedidos"),
        ),
        sa.ForeignKeyConstraint(
            ["repartidor_id"],
            ["repartidores.id"],
            name=op.f(
                "fk_historial_estados_repartidor_id_repartidores"
            ),
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_historial_estados"),
        ),
    )


def downgrade() -> None:
    """Elimina únicamente el historial de esta revisión."""
    op.drop_table("historial_estados")
