# Ejecución local del MVP

## Propósito

Esta guía permite preparar y probar en Windows la API REST, el bot de Telegram
y el panel administrativo del MVP de Restaurant Las Retamas. Las credenciales
se solicitan de manera interactiva y se guardan únicamente en
`backend/.env`, archivo excluido del control de versiones.

## Requisitos previos

- Git.
- Python 3.12.
- PostgreSQL 15 con el servicio local iniciado.
- Node.js y pnpm.
- Una cuenta de Telegram para crear y probar el bot.

Los comandos siguientes parten de la raíz del repositorio.

## Preparar el backend y PostgreSQL

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
python -m app.cli.bootstrap_local
```

El asistente solicita la contraseña del usuario local `postgres`, crea o
actualiza el rol `restaurant_user`, crea la base
`restaurant_las_retamas`, genera `backend/.env` y aplica las migraciones
Alembic. Si `.env` ya existe, pide confirmación antes de reemplazarlo.

La contraseña de `postgres` solo se utiliza durante la conexión inicial y no
se escribe en el repositorio ni en el archivo de entorno.

## Crear el administrador de prueba

```powershell
python -m app.cli.create_admin --username admin_prueba
```

La contraseña se solicita dos veces sin mostrarse. El comando crea el usuario
si no existe o actualiza su credencial y lo deja activo. Esa contraseña no
debe incluirse en commits, capturas ni documentación.

## Configurar el código QR de pago

Guardar la imagen QR autorizada por el restaurante en:

```text
backend/var/payment-qr.png
```

La ruta puede cambiarse mediante `PAYMENT_QR_PATH` en `backend/.env`. Sin una
imagen válida, el flujo de pago no podrá mostrar el QR.

## Crear el bot con BotFather

1. Abrir Telegram y buscar la cuenta verificada `@BotFather`.
2. Enviar `/newbot`.
3. Escribir el nombre visible del bot.
4. Elegir un nombre de usuario disponible que termine en `bot`.
5. Copiar el token entregado por BotFather.
6. Sustituir `replace-after-botfather` en `backend/.env`, sin comillas.
7. No publicar el token en Issues, commits, Pull Requests o capturas.

Si un token queda expuesto, debe revocarse con BotFather y reemplazarse.

## Iniciar el sistema

Abrir tres terminales. En la primera:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

En la segunda:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m app.bot.run
```

En la tercera:

```powershell
cd frontend
pnpm install
pnpm dev
```

El panel queda normalmente en `http://localhost:5173`. La API responde en
`http://127.0.0.1:8000` y su estado se comprueba en
`http://127.0.0.1:8000/api/health`.

## Preparar un repartidor de prueba

1. Iniciar sesión en el panel con `admin_prueba`.
2. Abrir **Repartidores**.
3. Registrar el identificador de chat de Telegram, nombre y teléfono.
4. Mantener la cuenta activa para que el bot reconozca sus comandos.

Deshabilitar un repartidor conserva el historial de pedidos y evita su acceso
operativo.

## Verificación recomendada

1. Confirmar que `/api/health` responde correctamente.
2. Iniciar sesión en el panel.
3. Registrar y editar un repartidor.
4. Configurar catálogo y menú disponible.
5. Crear un pedido desde una conversación de cliente con el bot.
6. Revisarlo y asignarlo desde el panel.
7. Confirmar los estados desde la cuenta del repartidor.
8. Comprobar las notificaciones recibidas por el cliente.

Esta ejecución permite validar el sistema aunque el despliegue en el VPS de
Hetzner se realice posteriormente. No reemplaza la validación ni la
documentación final del despliegue.
