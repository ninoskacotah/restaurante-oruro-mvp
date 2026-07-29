"""Contratos públicos de la API administrativa."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    """Base que permite serializar modelos de SQLAlchemy sin exponerlos."""

    model_config = ConfigDict(from_attributes=True)


class LoginInput(BaseModel):
    """Credenciales recibidas por el inicio de sesión."""

    nombre_usuario: str = Field(min_length=1, max_length=150)
    contrasena: str = Field(min_length=1, max_length=200)


class TokenOutput(BaseModel):
    """Bearer token de corta duración."""

    access_token: str
    token_type: str = "bearer"


class AdministradorOutput(ApiModel):
    """Identidad administrativa sin hash ni datos sensibles."""

    id: int
    nombre_usuario: str
    activo: bool


class PlatoInput(BaseModel):
    """Datos editables del catálogo."""

    nombre: str = Field(min_length=1, max_length=150)
    descripcion: str | None = Field(default=None, max_length=500)
    precio: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    activo: bool = False


class PlatoOutput(ApiModel):
    """Representación segura de un plato."""

    id: int
    nombre: str
    descripcion: str | None
    precio: Decimal
    activo: bool


class MenuCreate(BaseModel):
    """Fecha que identifica una oferta diaria."""

    fecha: date


class MenuState(BaseModel):
    """Estado administrable del menú."""

    activo: bool


class MenuOutput(ApiModel):
    """Menú programado."""

    id: int
    fecha: date
    activo: bool


class DetalleMenuInput(BaseModel):
    """Plato y existencias que se incorporan a un menú."""

    plato_id: int = Field(gt=0)
    stock: int = Field(ge=0)
    disponible: bool = False


class OfertaInput(BaseModel):
    """Cambios de stock y visibilidad."""

    stock: int = Field(ge=0)
    disponible: bool


class DetalleMenuOutput(ApiModel):
    """Detalle persistente de la oferta."""

    id: int
    menu_id: int
    plato_id: int
    stock: int
    disponible: bool


class PedidoOutput(ApiModel):
    """Resumen administrativo del pedido."""

    id: int
    cliente_id: int
    menu_id: int | None
    codigo_seguimiento: str | None
    estado_actual: str
    total: Decimal
    entrega_latitud: Decimal | None
    entrega_longitud: Decimal | None
    referencia_entrega: str | None
    fecha_creacion: datetime


class DetallePedidoOutput(ApiModel):
    """Línea histórica de un pedido."""

    id: int
    plato_id: int
    nombre_plato: str
    precio_unitario: Decimal
    cantidad: int
    subtotal: Decimal


class ComprobanteOutput(ApiModel):
    """Metadatos y revisión sin contenido binario."""

    id: int
    archivo_referencia: str
    nombre_generado: str
    tipo_mime: str
    tamanio_bytes: int
    estado_revision: str
    observacion: str | None
    fecha_envio: datetime
    fecha_revision: datetime | None


class PedidoDetailOutput(BaseModel):
    """Vista administrativa compuesta del pedido."""

    pedido: PedidoOutput
    detalles: list[DetallePedidoOutput]
    comprobantes: list[ComprobanteOutput]
    asignaciones: list["AsignacionOutput"]


class RevisionComprobanteInput(BaseModel):
    """Decisión manual sobre un comprobante."""

    aprobado: bool
    observacion: str | None = Field(default=None, max_length=500)


class AsignacionInput(BaseModel):
    """Repartidor elegido por el administrador."""

    repartidor_id: int = Field(gt=0)


class AsignacionOutput(ApiModel):
    """Asignación observable sin datos internos."""

    id: int
    pedido_id: int
    repartidor_id: int
    activa: bool
    fecha_asignacion: datetime
    fecha_acuse: datetime | None
    fecha_cierre: datetime | None


class RepartidorOutput(ApiModel):
    """Perfil operativo visible para asignación."""

    id: int
    chat_id: str
    nombre: str | None
    telefono: str | None
    activo: bool


class RepartidorInput(BaseModel):
    """Datos administrables de un repartidor registrado."""

    chat_id: str = Field(min_length=1, max_length=100)
    nombre: str | None = Field(default=None, max_length=150)
    telefono: str | None = Field(default=None, max_length=50)
    activo: bool = True


class HistorialOutput(ApiModel):
    """Evento observable del ciclo del pedido."""

    id: int
    estado_anterior: str | None
    estado_nuevo: str
    evento: str
    origen: str
    fecha_registro: datetime


class SeguimientoOutput(BaseModel):
    """Última posición conocida para el panel."""

    pedido_id: int
    asignacion_id: int | None
    repartidor_id: int | None
    latitud: Decimal | None
    longitud: Decimal | None
    fecha_registro: datetime | None


class ClienteOutput(ApiModel):
    """Perfil del cliente para su ficha administrativa."""

    id: int
    chat_id: str
    nombre: str | None
    telefono: str | None
    fecha_registro: datetime


class ClienteDetailOutput(BaseModel):
    """Ficha con historial y frecuencia calculados."""

    cliente: ClienteOutput
    pedidos: list[PedidoOutput]
    frecuencia_pedidos: int


class PlatoPopularOutput(BaseModel):
    """Cantidad vendida de un plato dentro del periodo."""

    plato_id: int
    nombre: str
    cantidad: int


class ReportesOutput(BaseModel):
    """Tres indicadores calculados a partir de pedidos persistidos."""

    fecha: date
    ventas_dia: Decimal
    pedidos_contabilizados: int
    platos_mas_pedidos: list[PlatoPopularOutput]
    tiempo_promedio_entrega_minutos: Decimal | None
