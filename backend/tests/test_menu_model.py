"""Pruebas del modelo de menú."""

import unittest
from sqlalchemy import Boolean, Date
from app.models import Menu


class MenuModelTest(unittest.TestCase):
    """Verifica el menú sin platos asociados."""

    def test_columns_and_constraints(self) -> None:
        columns = Menu.__table__.columns
        self.assertEqual(list(columns.keys()), ["id", "fecha", "activo"])
        self.assertTrue(columns.id.primary_key)
        self.assertIsInstance(columns.fecha.type, Date)
        self.assertFalse(columns.fecha.nullable)
        self.assertIsInstance(columns.activo.type, Boolean)
        self.assertEqual(str(columns.activo.server_default.arg), "false")
        names = {constraint.name for constraint in Menu.__table__.constraints}
        self.assertIn("pk_menus", names)
        self.assertIn("uq_menus_fecha", names)


if __name__ == "__main__":
    unittest.main()
