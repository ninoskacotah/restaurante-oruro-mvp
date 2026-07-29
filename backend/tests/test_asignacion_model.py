"""Pruebas del modelo persistente de asignación."""

import unittest

from sqlalchemy import ForeignKeyConstraint

from app.models import Asignacion


class AsignacionModelTest(unittest.TestCase):
    """Verifica el historial sin ejecutar asignaciones operativas."""

    def test_columns_and_optional_event_dates(self) -> None:
        """Comprueba los siete campos del diseño."""
        columns = Asignacion.__table__.columns
        self.assertEqual(
            list(columns.keys()),
            [
                "id",
                "pedido_id",
                "repartidor_id",
                "activa",
                "fecha_asignacion",
                "fecha_acuse",
                "fecha_cierre",
            ],
        )
        self.assertTrue(columns.id.primary_key)
        self.assertFalse(columns.pedido_id.nullable)
        self.assertFalse(columns.repartidor_id.nullable)
        self.assertFalse(columns.activa.nullable)
        self.assertFalse(columns.fecha_asignacion.nullable)
        self.assertTrue(columns.fecha_acuse.nullable)
        self.assertTrue(columns.fecha_cierre.nullable)

    def test_relations_and_single_active_index(self) -> None:
        """Valida relaciones y el índice único parcial de PostgreSQL."""
        foreign_keys = {
            next(iter(item.elements)).target_fullname
            for item in Asignacion.__table__.constraints
            if isinstance(item, ForeignKeyConstraint)
        }
        indexes = {item.name: item for item in Asignacion.__table__.indexes}
        active_index = indexes["uq_asignaciones_pedido_activa"]

        self.assertEqual(foreign_keys, {"pedidos.id", "repartidores.id"})
        self.assertTrue(active_index.unique)
        self.assertEqual(
            [column.name for column in active_index.columns],
            ["pedido_id"],
        )
        self.assertEqual(
            str(active_index.dialect_options["postgresql"]["where"]),
            "activa",
        )


if __name__ == "__main__":
    unittest.main()
