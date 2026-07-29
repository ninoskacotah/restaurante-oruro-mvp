"""Pruebas del modelo persistente de tokens revocados."""

import unittest

from sqlalchemy import DateTime, ForeignKeyConstraint, String

from app.db.base import Base
from app.models import TokenRevocado


class TokenRevocadoModelTest(unittest.TestCase):
    """Verifica la lista de revocación sin guardar tokens reales."""

    def test_model_has_only_approved_columns(self) -> None:
        """Impide incorporar el JWT completo al esquema."""
        columns = TokenRevocado.__table__.columns

        self.assertEqual(
            list(columns.keys()),
            [
                "id",
                "administrador_id",
                "jti",
                "fecha_revocacion",
                "fecha_expiracion",
            ],
        )
        self.assertTrue(columns.id.primary_key)
        self.assertIsInstance(columns.jti.type, String)
        self.assertIsInstance(columns.fecha_revocacion.type, DateTime)
        self.assertIsInstance(columns.fecha_expiracion.type, DateTime)

    def test_required_values_and_defaults_are_explicit(self) -> None:
        """Genera la revocación, pero exige el vencimiento del JWT."""
        columns = TokenRevocado.__table__.columns

        self.assertFalse(columns.administrador_id.nullable)
        self.assertFalse(columns.jti.nullable)
        self.assertFalse(columns.fecha_revocacion.nullable)
        self.assertIsNotNone(columns.fecha_revocacion.server_default)
        self.assertFalse(columns.fecha_expiracion.nullable)
        self.assertIsNone(columns.fecha_expiracion.server_default)

    def test_constraints_follow_approved_design(self) -> None:
        """Comprueba unicidad, autoría administrativa y nombres."""
        constraints = {
            constraint.name: constraint
            for constraint in TokenRevocado.__table__.constraints
        }

        self.assertIn("pk_tokens_revocados", constraints)
        self.assertIn("uq_tokens_revocados_jti", constraints)
        foreign_key_name = (
            "fk_tokens_revocados_administrador_id_administradores"
        )
        self.assertIn(foreign_key_name, constraints)
        foreign_key = constraints[foreign_key_name]
        self.assertIsInstance(foreign_key, ForeignKeyConstraint)
        self.assertEqual(
            next(iter(foreign_key.elements)).target_fullname,
            "administradores.id",
        )


if __name__ == "__main__":
    unittest.main()
