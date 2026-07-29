"""Pruebas del primer modelo persistente del backend."""

import unittest

from sqlalchemy import DateTime, String

from app.db.base import Base
from app.models import Cliente


class ClienteModelTest(unittest.TestCase):
    """Verifica el modelo sin crear tablas ni abrir conexiones."""

    def test_cliente_is_the_only_registered_table(self) -> None:
        """Mantiene el incremento limitado a la entidad autorizada."""
        self.assertEqual(set(Base.metadata.tables), {"clientes"})
        self.assertIs(Cliente.__table__, Base.metadata.tables["clientes"])

    def test_cliente_has_expected_columns(self) -> None:
        """Comprueba los cinco atributos definidos en el diseño."""
        columns = Cliente.__table__.columns

        self.assertEqual(
            list(columns.keys()),
            ["id", "chat_id", "nombre", "telefono", "fecha_registro"],
        )
        self.assertTrue(columns.id.primary_key)
        self.assertIsInstance(columns.chat_id.type, String)
        self.assertIsInstance(columns.nombre.type, String)
        self.assertIsInstance(columns.telefono.type, String)
        self.assertIsInstance(columns.fecha_registro.type, DateTime)

    def test_required_and_optional_values_are_explicit(self) -> None:
        """Permite completar nombre y teléfono después del reconocimiento."""
        columns = Cliente.__table__.columns

        self.assertFalse(columns.chat_id.nullable)
        self.assertTrue(columns.nombre.nullable)
        self.assertTrue(columns.telefono.nullable)
        self.assertFalse(columns.fecha_registro.nullable)
        self.assertIsNotNone(columns.fecha_registro.server_default)

    def test_constraints_follow_shared_naming_convention(self) -> None:
        """Valida los nombres estables de clave primaria y unicidad."""
        constraints = {
            constraint.name for constraint in Cliente.__table__.constraints
        }

        self.assertIn("pk_clientes", constraints)
        self.assertIn("uq_clientes_chat_id", constraints)


if __name__ == "__main__":
    unittest.main()
