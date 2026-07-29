"""Pruebas del modelo persistente de ubicación del trayecto."""

import unittest

from sqlalchemy import ForeignKeyConstraint

from app.models import UbicacionTrayecto


class UbicacionTrayectoModelTest(unittest.TestCase):
    """Verifica puntos de ubicación sin recibirlos en tiempo real."""

    def test_fields_and_assignment_relation(self) -> None:
        """Comprueba los cinco campos y su vínculo con la asignación."""
        columns = UbicacionTrayecto.__table__.columns
        self.assertEqual(
            list(columns.keys()),
            [
                "id",
                "asignacion_id",
                "latitud",
                "longitud",
                "fecha_registro",
            ],
        )
        self.assertTrue(columns.id.primary_key)
        for column_name in list(columns.keys())[1:]:
            self.assertFalse(columns[column_name].nullable)

        foreign_keys = {
            next(iter(item.elements)).target_fullname
            for item in UbicacionTrayecto.__table__.constraints
            if isinstance(item, ForeignKeyConstraint)
        }
        self.assertEqual(foreign_keys, {"asignaciones.id"})


if __name__ == "__main__":
    unittest.main()
