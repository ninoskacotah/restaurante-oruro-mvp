"""Almacenamiento local y no público de fotografías recibidas por Telegram."""

from pathlib import Path
from uuid import uuid4


ALLOWED_PHOTO_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


def payment_receipt_path(media_root: Path, mime_type: str) -> Path:
    """Genera una ruta relativa impredecible dentro del directorio autorizado."""
    if mime_type not in ALLOWED_PHOTO_MIME_TYPES:
        raise ValueError("El comprobante debe ser una imagen admitida.")
    extension = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }[mime_type]
    return Path("comprobantes") / f"{uuid4().hex}{extension}"


def resolve_media_path(media_root: Path, relative_path: Path) -> Path:
    """Resuelve una referencia y evita que salga del directorio configurado."""
    root = media_root.resolve()
    target = (root / relative_path).resolve()
    if root not in target.parents:
        raise ValueError("La ruta del archivo no es segura.")
    target.parent.mkdir(parents=True, exist_ok=True)
    return target
