"""Crea la tabla de comprobantes de pago.

Revision ID: 0010_comprobantes_pago
Revises: 0009_detalles_pedido
Create Date: 2026-07-28
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0010_comprobantes_pago"
down_revision: str | Sequence[str] | None = "0009_detalles_pedido"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Crea referencias y metadatos para la revisión de pagos."""
    op.create_table(
        "comprobantes_pago",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pedido_id", sa.Integer(), nullable=False),
        sa.Column("administrador_id", sa.Integer(), nullable=True),
        sa.Column(
            "archivo_referencia",
            sa.String(length=500),
            nullable=False,
        ),
        sa.Column(
            "nombre_generado",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column("tipo_mime", sa.String(length=100), nullable=False),
        sa.Column("tamanio_bytes", sa.Integer(), nullable=False),
        sa.Column(
            "estado_revision",
            sa.String(length=20),
            server_default=sa.text("'PENDIENTE'"),
            nullable=False,
        ),
        sa.Column("observacion", sa.Text(), nullable=True),
        sa.Column(
            "fecha_envio",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "fecha_revision",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.CheckConstraint(
            "tamanio_bytes >= 0",
            name=op.f("ck_comprobantes_pago_tamanio_bytes"),
        ),
        sa.ForeignKeyConstraint(
            ["administrador_id"],
            ["administradores.id"],
            name=op.f(
                "fk_comprobantes_pago_administrador_id_administradores"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["pedido_id"],
            ["pedidos.id"],
            name=op.f("fk_comprobantes_pago_pedido_id_pedidos"),
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_comprobantes_pago"),
        ),
    )


def downgrade() -> None:
    """Elimina únicamente los comprobantes de esta revisión."""
    op.drop_table("comprobantes_pago")
