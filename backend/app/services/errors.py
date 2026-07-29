"""Errores controlados producidos por las reglas de los servicios."""


class ErrorServicio(Exception):
    """Base para errores que un consumidor podrá traducir posteriormente."""


class ErrorValidacion(ErrorServicio):
    """Indica que los datos recibidos incumplen una regla del dominio."""


class RecursoNoEncontrado(ErrorServicio):
    """Indica que la entidad solicitada no existe."""


class ConflictoServicio(ErrorServicio):
    """Indica que la operación duplicaría o contradice el estado actual."""
