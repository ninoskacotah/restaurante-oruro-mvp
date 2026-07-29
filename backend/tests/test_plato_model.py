"""Pruebas del modelo persistente de platos."""

import unittest

from sqlalchemy import Boolean, CheckConstraint, Numeric, String

from app.models import Plato


class PlatoModelTest(unittest.TestCase):
    """Verifica el catálogo sin implementar operaciones administrativas."""

    def test_columns_match_approved_design(self) -> None:
        """Comprueba nombres, tipos y obligatoriedad."""
        columns = Plato.__table__.columns

        self.assertEqual(
            list(columns.keys()),
            ["id", "nombre", "descripcion", "precio", "activo"],
        )
        self.assertTrue(columns.id.primary_key)
        self.assertIsInstance(columns.nombre.type, String)
        self.assertFalse(columns.nombre.nullable)
        self.assertTrue(columns.descripcion.nullable)
        self.assertIsInstance(columns.precio.type, Numeric)
        self.assertEqual(columns.precio.type.precision, 10)
        self.assertEqual(columns.precio.type.scale, 2)
        self.assertIsInstance(columns.activo.type, Boolean)
        self.assertEqual(str(columns.activo.server_default.arg), "false")

    def test_constraints_have_stable_names(self) -> None:
        """Exige precio no negativo y una clave primaria previsible."""
        constraints = {
            constraint.name: constraint
            for constraint in Plato.__table__.constraints
        }

        self.assertIn("pk_platos", constraints)
        self.assertIsInstance(
            constraints["ck_platos_precio"],
            CheckConstraint,
        )


if __name__ == "__main__":
    unittest.main()
