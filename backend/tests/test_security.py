"""Pruebas del servicio aislado de contraseñas administrativas."""

import unittest

from argon2 import PasswordHasher, Type

from app.core.security import (
    hash_password,
    password_hash_needs_update,
    verify_password,
)


TEST_PASSWORD = "Clave ficticia solo para pruebas"


class PasswordSecurityTest(unittest.TestCase):
    """Comprueba Argon2id sin persistir ni mostrar credenciales."""

    def test_hash_uses_approved_argon2id_parameters(self) -> None:
        """Verifica algoritmo y costo dentro de la cadena PHC."""
        password_hash = hash_password(TEST_PASSWORD)

        self.assertTrue(password_hash.startswith("$argon2id$v=19$"))
        self.assertIn("$m=19456,t=2,p=1$", password_hash)

    def test_hash_uses_a_random_salt(self) -> None:
        """Confirma que la misma entrada no genera cadenas repetidas."""
        first_hash = hash_password(TEST_PASSWORD)
        second_hash = hash_password(TEST_PASSWORD)

        self.assertNotEqual(first_hash, second_hash)

    def test_correct_password_is_verified(self) -> None:
        """Acepta únicamente la contraseña que originó el hash."""
        password_hash = hash_password(TEST_PASSWORD)

        self.assertTrue(verify_password(TEST_PASSWORD, password_hash))

    def test_wrong_password_is_rejected(self) -> None:
        """Convierte la falta de coincidencia en un resultado seguro."""
        password_hash = hash_password(TEST_PASSWORD)

        self.assertFalse(
            verify_password("Otra clave ficticia", password_hash),
        )

    def test_invalid_hash_is_rejected(self) -> None:
        """No propaga detalles internos ante una cadena ilegible."""
        self.assertFalse(verify_password(TEST_PASSWORD, "hash-invalido"))

    def test_current_hash_does_not_need_update(self) -> None:
        """Reconoce la configuración aprobada como vigente."""
        password_hash = hash_password(TEST_PASSWORD)

        self.assertFalse(password_hash_needs_update(password_hash))

    def test_hash_with_old_parameters_needs_update(self) -> None:
        """Detecta una cadena válida creada con un costo diferente."""
        previous_hasher = PasswordHasher(
            memory_cost=1024,
            time_cost=1,
            parallelism=1,
            type=Type.ID,
        )
        previous_hash = previous_hasher.hash(TEST_PASSWORD)

        self.assertTrue(password_hash_needs_update(previous_hash))

    def test_invalid_hash_needs_replacement(self) -> None:
        """Impide tratar una cadena corrupta como configuración vigente."""
        self.assertTrue(password_hash_needs_update("hash-invalido"))


if __name__ == "__main__":
    unittest.main()
