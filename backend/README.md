# Backend de Restaurant Las Retamas

Esta carpeta contiene la aplicación FastAPI inicial del backend del MVP. Incluye
un endpoint técnico de salud, pero todavía no incorpora conexiones externas ni
lógica funcional del restaurante.

## Requisito

- Python 3.12.

Puede comprobarse la versión disponible con:

```bash
python --version
```

## Preparación del entorno

Desde la carpeta `backend/`, crear un entorno virtual:

```bash
python -m venv .venv
```

En PowerShell, activarlo con:

```powershell
.\.venv\Scripts\Activate.ps1
```

En Linux o macOS, activarlo con:

```bash
source .venv/bin/activate
```

Instalar el proyecto junto con las dependencias de prueba:

```bash
python -m pip install -e ".[test]"
```

## Verificación

Desde la carpeta `backend/`, ejecutar:

```bash
python -m unittest discover -s tests -v
```

La prueba confirma que el paquete principal y sus subdivisiones pueden
importarse y comprueba la respuesta del endpoint de salud. No necesita iniciar
un servidor ni conectarse a PostgreSQL.

## Ejecución local

Iniciar el servidor de desarrollo desde `backend/`:

```bash
python -m uvicorn app.main:app --reload
```

El endpoint técnico queda disponible en:

```text
GET http://127.0.0.1:8000/api/health
```

Su respuesta es:

```json
{"status": "ok"}
```

El servidor de recarga es únicamente para desarrollo local.
