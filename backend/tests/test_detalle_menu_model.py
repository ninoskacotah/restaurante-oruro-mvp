"""Pruebas del detalle persistente del menú."""

import unittest

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, UniqueConstraint

from app.models import DetalleMenu


class DetalleMenuModelTest(unittest.TestCase):
    """Verifica relaciones y reglas sin gestionar stock."""

    def test_columns_and_defaults(self) -> None:
        """Comprueba los cinco campos aprobados."""
        columns = DetalleMenu.__table__.columns
        self.assertEqual(
            list(columns.keys()),
            ["id", "menu_id", "plato_id", "stock", "disponible"],
        )
        self.assertTrue(columns.id.primary_key)
        self.assertFalse(columns.menu_id.nullable)
        self.assertFalse(columns.plato_id.nullable)
        self.assertFalse(columns.stock.nullable)
        self.assertEqual(str(columns.disponible.server_default.arg), "false")

    def test_constraints_match_design(self) -> None:
        """Valida claves foráneas, unicidad y stock no negativo."""
        constraints = list(DetalleMenu.__table__.constraints)
        foreign_keys = {
            next(iter(item.elements)).target_fullname
            for item in constraints
            if isinstance(item, ForeignKeyConstraint)
        }
        self.assertEqual(foreign_keys, {"menus.id", "platos.id"})
        self.assertTrue(
            any(isinstance(item, UniqueConstraint) for item in constraints)
        )
        self.assertTrue(
            any(isinstance(item, CheckConstraint) for item in constraints)
        )


if __name__ == "__main__":
    unittest.main()
