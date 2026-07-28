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

## Configuración local

Crear el archivo local de variables a partir del ejemplo:

En PowerShell:

```powershell
Copy-Item .env.example .env
```

En Linux o macOS:

```bash
cp .env.example .env
```

Después, sustituir en `.env` todos los valores ilustrativos. Este archivo
contiene información sensible y no debe incorporarse a Git.

| Variable | Propósito |
|---|---|
| `APP_ENV` | Identifica el entorno: `development`, `test` o `production`. |
| `DATABASE_URL` | Define la conexión futura con PostgreSQL. |
| `TELEGRAM_BOT_TOKEN` | Contiene el token privado entregado por BotFather. |
| `JWT_SECRET` | Contiene el secreto utilizado posteriormente para firmar JWT. |

Las variables definidas directamente en el sistema tienen prioridad sobre las
escritas en `.env`. La configuración solo se carga cuando una operación llama a
`get_settings()`; importar la aplicación no exige secretos ni abre conexiones.

## Verificación

Desde la carpeta `backend/`, ejecutar:

```bash
python -m unittest discover -s tests -v
```

Las pruebas confirman que los paquetes pueden importarse, comprueban el endpoint
de salud y verifican la carga de configuración con valores ficticios. No
necesitan iniciar un servidor ni conectarse a PostgreSQL o Telegram.

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
