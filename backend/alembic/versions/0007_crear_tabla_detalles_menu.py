"""Crea la tabla de detalles del menú.

Revision ID: 0007_detalles_menu
Revises: 0006_menus
Create Date: 2026-07-28
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0007_detalles_menu"
down_revision: str | Sequence[str] | None = "0006_menus"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Relaciona platos y menús con stock y disponibilidad."""
    op.create_table(
        "detalles_menu",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("menu_id", sa.Integer(), nullable=False),
        sa.Column("plato_id", sa.Integer(), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
        sa.Column(
            "disponible",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "stock >= 0",
            name=op.f("ck_detalles_menu_stock"),
        ),
        sa.ForeignKeyConstraint(
            ["menu_id"],
            ["menus.id"],
            name=op.f("fk_detalles_menu_menu_id_menus"),
        ),
        sa.ForeignKeyConstraint(
            ["plato_id"],
            ["platos.id"],
            name=op.f("fk_detalles_menu_plato_id_platos"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_detalles_menu")),
        sa.UniqueConstraint(
            "menu_id",
            "plato_id",
            name=op.f("uq_detalles_menu_menu_id"),
        ),
    )


def downgrade() -> None:
    """Elimina la tabla incorporada por esta revisión."""
    op.drop_table("detalles_menu")
