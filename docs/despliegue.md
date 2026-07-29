# Manual de despliegue

## Propósito y estado

Este manual describe cómo ejecutar y desplegar el MVP de Restaurant Las
Retamas. La ejecución local en Windows fue probada durante la validación
integral. El VPS de Hetzner es el entorno objetivo seleccionado, pero los pasos
de producción de este documento deben marcarse como realizados únicamente
después de ejecutarlos y verificarlos en el servidor.

El sistema utiliza tres procesos integrados:

- API FastAPI;
- bot Aiogram mediante *long polling*;
- panel Vue compilado como archivos estáticos.

Los tres comparten PostgreSQL y el backend conserva comprobantes, evidencias y
el QR en un directorio persistente.

## Ejecución local validada

Para Windows, seguir
[ejecucion-local.md](ejecucion-local.md). Esa guía prepara PostgreSQL, aplica
las migraciones, crea el administrador y levanta API, bot y panel en tres
terminales.

La validación y sus resultados están registrados en
[validacion-integral.md](validacion-integral.md).

## Arquitectura prevista en Hetzner

```mermaid
flowchart LR
    T["Telegram Bot API"] --> B["Bot Aiogram"]
    C["Navegador del administrador"] --> N["Nginx + HTTPS"]
    N --> F["Panel Vue compilado"]
    N --> A["API FastAPI"]
    B --> A
    A --> P[("PostgreSQL")]
    A --> M["Archivos persistentes"]
```

Nginx publica el panel y redirige `/api/` a FastAPI. La API y PostgreSQL
escuchan solamente en interfaces internas. El bot establece conexiones
salientes hacia Telegram; esta versión no utiliza *webhook*.

## Requisitos del VPS

- VPS de Hetzner con Ubuntu 24.04 LTS.
- Usuario administrativo con `sudo`.
- Dominio apuntando a la IP pública del VPS.
- Puertos 22, 80 y 443 permitidos.
- Git, Python 3.12, PostgreSQL 15 o posterior, Nginx y Node.js 22.
- Token vigente del bot y QR de pago autorizado.

Las versiones definitivas deben comprobarse con:

```bash
python3.12 --version
psql --version
node --version
nginx -v
```

## Preparar el servidor

Actualizar el sistema e instalar dependencias:

```bash
sudo apt update
sudo apt upgrade
sudo apt install git python3.12 python3.12-venv postgresql nginx certbot python3-certbot-nginx
```

Instalar Node.js 22 mediante una fuente oficial o un repositorio mantenido para
Ubuntu y habilitar pnpm con Corepack:

```bash
sudo corepack enable
corepack prepare pnpm@11.9.0 --activate
```

Crear un usuario de servicio sin privilegios administrativos:

```bash
sudo adduser --system --group --home /opt/restaurante-oruro-mvp restaurante
```

El código y los archivos persistentes pertenecerán a este usuario. No se
ejecutan la API ni el bot como `root`.

## Obtener una versión

La versión de producción debe proceder de `main` después de su Pull Request:

```bash
sudo -u restaurante git clone --branch main https://github.com/ninoskacotah/restaurante-oruro-mvp.git /opt/restaurante-oruro-mvp
cd /opt/restaurante-oruro-mvp
git rev-parse HEAD
```

Registrar el hash obtenido en la evidencia del despliegue.

## Configurar PostgreSQL

Ingresar a PostgreSQL:

```bash
sudo -u postgres psql
```

Crear un usuario y una base con una contraseña exclusiva:

```sql
CREATE ROLE restaurant_user WITH LOGIN PASSWORD 'REEMPLAZAR_CON_SECRETO';
CREATE DATABASE restaurant_las_retamas OWNER restaurant_user;
\q
```

La contraseña real no debe escribirse en Issues, commits, capturas ni este
documento. PostgreSQL debe mantenerse sin acceso público; solo la API necesita
conectarse desde el propio servidor.

## Preparar el backend

```bash
cd /opt/restaurante-oruro-mvp/backend
sudo -u restaurante python3.12 -m venv .venv
sudo -u restaurante .venv/bin/python -m pip install --upgrade pip
sudo -u restaurante .venv/bin/python -m pip install .
sudo -u restaurante mkdir -p var/media
```

Crear `/opt/restaurante-oruro-mvp/backend/.env` con permisos restringidos:

```dotenv
APP_ENV=production
DATABASE_URL=postgresql+psycopg://restaurant_user:REEMPLAZAR@localhost:5432/restaurant_las_retamas
TELEGRAM_BOT_TOKEN=REEMPLAZAR
JWT_SECRET=REEMPLAZAR_CON_UN_SECRETO_ALEATORIO_DE_32_O_MAS_CARACTERES
MEDIA_ROOT=var/media
PAYMENT_QR_PATH=var/payment-qr.png
```

```bash
sudo chown restaurante:restaurante /opt/restaurante-oruro-mvp/backend/.env
sudo chmod 600 /opt/restaurante-oruro-mvp/backend/.env
```

Copiar el QR autorizado a `backend/var/payment-qr.png`, sin incorporarlo a Git.
El directorio `backend/var` debe incluirse en los respaldos.

Aplicar migraciones y crear el administrador:

```bash
cd /opt/restaurante-oruro-mvp/backend
sudo -u restaurante .venv/bin/alembic upgrade head
sudo -u restaurante .venv/bin/python -m app.cli.create_admin --username admin_prueba
```

En producción conviene reemplazar `admin_prueba` por un nombre no predecible. La
contraseña se ingresa de forma interactiva y no se registra en texto plano.

## Compilar el panel

```bash
cd /opt/restaurante-oruro-mvp/frontend
sudo -u restaurante pnpm install --frozen-lockfile
sudo -u restaurante pnpm build
```

El resultado queda en `frontend/dist`. No se debe ejecutar el servidor de
desarrollo de Vite como servicio de producción.

## Crear los servicios

Crear `/etc/systemd/system/restaurant-api.service`:

```ini
[Unit]
Description=Restaurant Las Retamas API
After=network.target postgresql.service

[Service]
User=restaurante
Group=restaurante
WorkingDirectory=/opt/restaurante-oruro-mvp/backend
ExecStart=/opt/restaurante-oruro-mvp/backend/.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=on-failure
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Crear `/etc/systemd/system/restaurant-bot.service`:

```ini
[Unit]
Description=Restaurant Las Retamas Telegram Bot
After=network.target postgresql.service restaurant-api.service

[Service]
User=restaurante
Group=restaurante
WorkingDirectory=/opt/restaurante-oruro-mvp/backend
ExecStart=/opt/restaurante-oruro-mvp/backend/.venv/bin/python -m app.bot.run
Restart=on-failure
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Habilitar los servicios:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now restaurant-api restaurant-bot
sudo systemctl status restaurant-api restaurant-bot
```

## Configurar Nginx

Crear `/etc/nginx/sites-available/restaurante` y reemplazar
`restaurante.ejemplo.com` por el dominio real:

```nginx
server {
    listen 80;
    server_name restaurante.ejemplo.com;

    root /opt/restaurante-oruro-mvp/frontend/dist;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Habilitar el sitio y comprobar la configuración:

```bash
sudo ln -s /etc/nginx/sites-available/restaurante /etc/nginx/sites-enabled/restaurante
sudo nginx -t
sudo systemctl reload nginx
```

Cuando el dominio resuelva correctamente, habilitar HTTPS:

```bash
sudo certbot --nginx -d restaurante.ejemplo.com
sudo certbot renew --dry-run
```

No deben publicarse el panel ni credenciales administrativas mediante HTTP sin
cifrado.

## Verificación posterior

1. Consultar `https://DOMINIO/api/health`.
2. Iniciar sesión en el panel desde una ventana privada.
3. Confirmar que una ruta interna rechaza una sesión no autenticada.
4. Verificar que el bot responde a `/start`.
5. Registrar un menú de prueba con stock.
6. Ejecutar un pedido completo con datos de prueba.
7. Comprobar pago, asignación, seguimiento, llegada y entrega.
8. Contrastar stock, historial y reportes.
9. Revisar los servicios:

```bash
sudo journalctl -u restaurant-api -u restaurant-bot --since "15 minutes ago"
```

No deben copiarse tokens, datos personales ni comprobantes desde los registros
hacia la evidencia académica.

## Actualizar una versión

Antes de actualizar, registrar el hash actual y realizar un respaldo:

```bash
cd /opt/restaurante-oruro-mvp
git rev-parse HEAD
sudo systemctl stop restaurant-bot restaurant-api
sudo -u restaurante git fetch origin
sudo -u restaurante git checkout main
sudo -u restaurante git pull --ff-only origin main
```

Actualizar dependencias, migraciones y panel:

```bash
cd backend
sudo -u restaurante .venv/bin/python -m pip install .
sudo -u restaurante .venv/bin/alembic upgrade head
cd ../frontend
sudo -u restaurante pnpm install --frozen-lockfile
sudo -u restaurante pnpm build
sudo systemctl start restaurant-api restaurant-bot
sudo systemctl reload nginx
```

Repetir la verificación posterior.

## Respaldo

El respaldo mínimo incluye:

- volcado de PostgreSQL;
- `backend/var/media`;
- QR de pago autorizado;
- referencia del hash desplegado;
- configuración de Nginx y servicios, sin divulgar secretos.

Ejemplo de respaldo de la base:

```bash
sudo -u postgres pg_dump -Fc restaurant_las_retamas > /ruta/segura/restaurant_las_retamas.dump
```

Los respaldos deben almacenarse fuera del directorio público del panel y
probarse periódicamente mediante una restauración en un entorno aislado.

## Reversión básica

Si una actualización falla:

1. detener API y bot;
2. volver al hash estable previamente registrado;
3. restaurar la base si una migración incompatible ya fue aplicada;
4. reinstalar dependencias y recompilar el panel;
5. iniciar servicios;
6. ejecutar nuevamente la verificación.

No debe ejecutarse `alembic downgrade` sin revisar primero la migración y el
respaldo disponible, porque una reversión puede eliminar datos.

## Lista de comprobación del despliegue real

- [ ] Dominio apuntado al VPS.
- [ ] Firewall limitado a los puertos necesarios.
- [ ] PostgreSQL sin exposición pública.
- [ ] `.env` con permisos `600`.
- [ ] Token y secreto JWT diferentes a los valores de ejemplo.
- [ ] Migraciones aplicadas.
- [ ] Administrador creado con credencial segura.
- [ ] QR y directorio de medios persistentes.
- [ ] API y bot activos mediante systemd.
- [ ] Panel compilado y servido por Nginx.
- [ ] HTTPS válido y renovación comprobada.
- [ ] Flujo integral probado en el VPS.
- [ ] Respaldo creado y restauración ensayada.

Mientras esta lista no se complete con evidencia real, el estado correcto del
proyecto es **validado localmente y con despliegue en VPS pendiente**.
