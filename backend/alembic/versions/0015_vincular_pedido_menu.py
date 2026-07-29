"""Vincula cada pedido confirmado con su menú de origen.

Revision ID: 0015_pedido_menu
Revises: 0014_historial_estados
Create Date: 2026-07-29
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0015_pedido_menu"
down_revision: str | Sequence[str] | None = "0014_historial_estados"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Añade una relación opcional para borradores previos a confirmar."""
    op.add_column(
        "pedidos",
        sa.Column("menu_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_pedidos_menu_id_menus"),
        "pedidos",
        "menus",
        ["menu_id"],
        ["id"],
    )


def downgrade() -> None:
    """Retira únicamente la relación incorporada por esta revisión."""
    op.drop_constraint(
        op.f("fk_pedidos_menu_id_menus"),
        "pedidos",
        type_="foreignkey",
    )
    op.drop_column("pedidos", "menu_id")
