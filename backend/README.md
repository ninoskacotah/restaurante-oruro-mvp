# Backend de Restaurant Las Retamas

Esta carpeta contiene la estructura inicial del backend del MVP. En este
incremento no se incluyen frameworks, conexiones externas ni lógica funcional.

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

Este incremento no requiere instalar dependencias externas.

## Verificación

Desde la carpeta `backend/`, ejecutar:

```bash
python -m unittest discover -s tests -v
```

La prueba confirma que el paquete principal y sus subdivisiones pueden
importarse. Todavía no inicia un servidor ni se conecta a PostgreSQL.
