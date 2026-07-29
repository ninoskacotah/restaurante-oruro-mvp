"""Pruebas del modelo persistente de pedido."""

import unittest

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, UniqueConstraint

from app.models import Pedido


class PedidoModelTest(unittest.TestCase):
    """Verifica la cabecera sin anticipar lógica de negocio."""

    def test_columns_and_defaults(self) -> None:
        """Comprueba los diez campos y sus valores iniciales."""
        columns = Pedido.__table__.columns
        self.assertEqual(
            list(columns.keys()),
            [
                "id",
                "cliente_id",
                "menu_id",
                "codigo_seguimiento",
                "estado_actual",
                "total",
                "entrega_latitud",
                "entrega_longitud",
                "referencia_entrega",
                "fecha_creacion",
            ],
        )
        self.assertTrue(columns.id.primary_key)
        self.assertFalse(columns.cliente_id.nullable)
        self.assertTrue(columns.menu_id.nullable)
        self.assertTrue(columns.codigo_seguimiento.nullable)
        self.assertEqual(
            str(columns.estado_actual.server_default.arg),
            "'BORRADOR'",
        )
        self.assertEqual(str(columns.total.server_default.arg), "0")
        self.assertTrue(columns.entrega_latitud.nullable)
        self.assertTrue(columns.entrega_longitud.nullable)
        self.assertTrue(columns.referencia_entrega.nullable)
        self.assertFalse(columns.fecha_creacion.nullable)

    def test_constraints_match_design(self) -> None:
        """Valida relación, código único y total no negativo."""
        constraints = list(Pedido.__table__.constraints)
        foreign_keys = {
            next(iter(item.elements)).target_fullname
            for item in constraints
            if isinstance(item, ForeignKeyConstraint)
        }
        unique_columns = {
            tuple(column.name for column in item.columns)
            for item in constraints
            if isinstance(item, UniqueConstraint)
        }

        self.assertEqual(foreign_keys, {"clientes.id", "menus.id"})
        self.assertIn(("codigo_seguimiento",), unique_columns)
        self.assertTrue(
            any(isinstance(item, CheckConstraint) for item in constraints)
        )


if __name__ == "__main__":
    unittest.main()
