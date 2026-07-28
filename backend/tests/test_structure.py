"""Verificación de la estructura importable del backend."""

import importlib
import unittest


PACKAGES = (
    "app",
    "app.api",
    "app.core",
    "app.db",
    "app.models",
    "app.schemas",
    "app.services",
)


class BackendStructureTest(unittest.TestCase):
    """Comprueba que los paquetes base estén disponibles."""

    def test_base_packages_can_be_imported(self) -> None:
        """Importa cada paquete previsto por la estructura inicial."""
        for package_name in PACKAGES:
            with self.subTest(package=package_name):
                module = importlib.import_module(package_name)
                self.assertIsNotNone(module)


if __name__ == "__main__":
    unittest.main()
