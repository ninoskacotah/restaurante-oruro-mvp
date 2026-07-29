"""Crea la tabla de ubicaciones del trayecto.

Revision ID: 0012_ubicaciones_trayecto
Revises: 0011_asignaciones
Create Date: 2026-07-28
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0012_ubicaciones_trayecto"
down_revision: str | Sequence[str] | None = "0011_asignaciones"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Crea los puntos ordenables de cada asignación."""
    op.create_table(
        "ubicaciones_trayecto",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("asignacion_id", sa.Integer(), nullable=False),
        sa.Column(
            "latitud",
            sa.Numeric(precision=9, scale=6),
            nullable=False,
        ),
        sa.Column(
            "longitud",
            sa.Numeric(precision=9, scale=6),
            nullable=False,
        ),
        sa.Column(
            "fecha_registro",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["asignacion_id"],
            ["asignaciones.id"],
            name=op.f(
                "fk_ubicaciones_trayecto_asignacion_id_asignaciones"
            ),
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_ubicaciones_trayecto"),
        ),
    )


def downgrade() -> None:
    """Elimina únicamente las ubicaciones de esta revisión."""
    op.drop_table("ubicaciones_trayecto")
