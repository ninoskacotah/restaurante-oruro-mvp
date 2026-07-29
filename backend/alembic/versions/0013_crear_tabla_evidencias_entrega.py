"""Crea la tabla de evidencias de entrega.

Revision ID: 0013_evidencias_entrega
Revises: 0012_ubicaciones_trayecto
Create Date: 2026-07-28
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0013_evidencias_entrega"
down_revision: str | Sequence[str] | None = "0012_ubicaciones_trayecto"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Crea referencias de fotografía o código para la entrega."""
    op.create_table(
        "evidencias_entrega",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("asignacion_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column(
            "valor_referencia",
            sa.String(length=500),
            nullable=False,
        ),
        sa.Column("tipo_mime", sa.String(length=100), nullable=True),
        sa.Column("tamanio_bytes", sa.Integer(), nullable=True),
        sa.Column(
            "fecha_registro",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "tamanio_bytes IS NULL OR tamanio_bytes >= 0",
            name=op.f("ck_evidencias_entrega_tamanio_bytes"),
        ),
        sa.ForeignKeyConstraint(
            ["asignacion_id"],
            ["asignaciones.id"],
            name=op.f(
                "fk_evidencias_entrega_asignacion_id_asignaciones"
            ),
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_evidencias_entrega"),
        ),
    )


def downgrade() -> None:
    """Elimina únicamente las evidencias de esta revisión."""
    op.drop_table("evidencias_entrega")
