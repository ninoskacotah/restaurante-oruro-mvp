"""Pruebas del modelo persistente del historial de estados."""

import unittest

from sqlalchemy import CheckConstraint, ForeignKeyConstraint

from app.models import HistorialEstado


class HistorialEstadoModelTest(unittest.TestCase):
    """Verifica eventos acumulativos sin ejecutar transiciones."""

    def test_fields_and_optional_actor_values(self) -> None:
        """Comprueba los diez campos del historial."""
        columns = HistorialEstado.__table__.columns
        self.assertEqual(
            list(columns.keys()),
            [
                "id",
                "pedido_id",
                "cliente_id",
                "repartidor_id",
                "administrador_id",
                "estado_anterior",
                "estado_nuevo",
                "evento",
                "origen",
                "fecha_registro",
            ],
        )
        self.assertTrue(columns.cliente_id.nullable)
        self.assertTrue(columns.repartidor_id.nullable)
        self.assertTrue(columns.administrador_id.nullable)
        self.assertTrue(columns.estado_anterior.nullable)
        self.assertFalse(columns.estado_nuevo.nullable)

    def test_relations_and_single_actor_constraint(self) -> None:
        """Valida el pedido, los posibles actores y su exclusión."""
        constraints = list(HistorialEstado.__table__.constraints)
        foreign_keys = {
            next(iter(item.elements)).target_fullname
            for item in constraints
            if isinstance(item, ForeignKeyConstraint)
        }
        checks = {
            item.name
            for item in constraints
            if isinstance(item, CheckConstraint)
        }

        self.assertEqual(
            foreign_keys,
            {
                "pedidos.id",
                "clientes.id",
                "repartidores.id",
                "administradores.id",
            },
        )
        self.assertEqual(checks, {"ck_historial_estados_un_actor"})


if __name__ == "__main__":
    unittest.main()
