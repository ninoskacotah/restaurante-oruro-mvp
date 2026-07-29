"""Pruebas del modelo persistente del repartidor."""

import unittest

from sqlalchemy import Boolean, DateTime, String

from app.db.base import Base
from app.models import Repartidor


class RepartidorModelTest(unittest.TestCase):
    """Verifica el modelo sin crear tablas ni abrir conexiones."""

    def test_repartidor_is_registered_in_shared_metadata(self) -> None:
        """Comprueba que la tabla utiliza los metadatos comunes."""
        self.assertIn("repartidores", Base.metadata.tables)
        self.assertIs(
            Repartidor.__table__,
            Base.metadata.tables["repartidores"],
        )

    def test_repartidor_has_expected_columns(self) -> None:
        """Comprueba los seis atributos definidos en el diseño."""
        columns = Repartidor.__table__.columns

        self.assertEqual(
            list(columns.keys()),
            [
                "id",
                "chat_id",
                "nombre",
                "telefono",
                "activo",
                "fecha_registro",
            ],
        )
        self.assertTrue(columns.id.primary_key)
        self.assertIsInstance(columns.chat_id.type, String)
        self.assertIsInstance(columns.nombre.type, String)
        self.assertIsInstance(columns.telefono.type, String)
        self.assertIsInstance(columns.activo.type, Boolean)
        self.assertIsInstance(columns.fecha_registro.type, DateTime)

    def test_operational_defaults_are_explicit(self) -> None:
        """Evita habilitar implícitamente un registro nuevo."""
        columns = Repartidor.__table__.columns

        self.assertFalse(columns.chat_id.nullable)
        self.assertTrue(columns.nombre.nullable)
        self.assertTrue(columns.telefono.nullable)
        self.assertFalse(columns.activo.nullable)
        self.assertIsNotNone(columns.activo.server_default)
        self.assertEqual(str(columns.activo.server_default.arg), "false")
        self.assertFalse(columns.fecha_registro.nullable)
        self.assertIsNotNone(columns.fecha_registro.server_default)

    def test_constraints_follow_shared_naming_convention(self) -> None:
        """Valida los nombres estables de clave primaria y unicidad."""
        constraints = {
            constraint.name
            for constraint in Repartidor.__table__.constraints
        }

        self.assertIn("pk_repartidores", constraints)
        self.assertIn("uq_repartidores_chat_id", constraints)


if __name__ == "__main__":
    unittest.main()
