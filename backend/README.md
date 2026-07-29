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

## Acceso a PostgreSQL

La capa `app.db.session` prepara el acceso asíncrono mediante SQLAlchemy 2 y
Psycopg 3. Proporciona operaciones explícitas para:

- construir el motor desde `DATABASE_URL`;
- crear la factoría de sesiones;
- confirmar o revertir una unidad de trabajo;
- cerrar siempre la sesión;
- liberar los recursos del motor.

La construcción del motor no abre por sí sola una conexión. En este incremento
las pruebas verifican la configuración y el ciclo transaccional sin un servidor
PostgreSQL activo.

Los modelos persistentes actuales representan al cliente identificado mediante
Telegram, al repartidor registrado y al administrador del panel. Repartidores y
administradores permanecen inactivos por defecto hasta que una función
posterior los habilite. El campo `credencial_hash` del administrador no admite
un valor predeterminado: deberá recibir exclusivamente una credencial procesada
por el servicio de seguridad que se implemente después. Todavía no existe
lógica funcional que consulte o escriba estos datos, y no se utiliza
`Base.metadata.create_all()`. La conexión contra una base real se incorporará
en un Issue posterior.

## Base declarativa

La capa `app.db.base` expone una sola clase `Base` y metadatos compartidos para
los futuros modelos. Las convenciones producen nombres previsibles para
índices, restricciones únicas, restricciones `CHECK`, claves foráneas y claves
primarias.

Estos metadatos permiten que Alembic compare los modelos con el esquema.
Actualmente contienen únicamente las tablas `clientes`, `repartidores` y
`administradores`; importar los modelos no ejecuta SQL ni crea el esquema.

## Migraciones

Alembic está configurado para utilizar `Base.metadata` y obtener
`DATABASE_URL` desde el entorno. `alembic.ini` no contiene credenciales.

Inspeccionar las cabezas del historial desde `backend/`:

```bash
python -m alembic -c alembic.ini heads
```

La cabeza actual corresponde a la tercera revisión, que crea
`administradores` después de `repartidores`. Generar la representación SQL del
historial completo sin abrir una conexión:

```bash
python -m alembic -c alembic.ini upgrade head --sql
```

También puede inspeccionarse únicamente la reversión de la tercera revisión:

```bash
python -m alembic -c alembic.ini downgrade 0003_administradores:0002_repartidores --sql
```

Estos comandos solo imprimen SQL. No debe ejecutarse `upgrade` o `downgrade` en
modo online ni otro comando que modifique una base hasta trabajar el Issue
específico correspondiente. Toda nueva revisión deberá inspeccionarse antes del
commit.

## Protección de contraseñas

La capa `app.core.security` utiliza Argon2id para generar y verificar las
credenciales administrativas. Su configuración inicial corresponde a la
decisión DT-015:

- memoria: `19456` KiB;
- iteraciones: `2`;
- paralelismo: `1`.

Cada hash incorpora una sal aleatoria generada por la biblioteca y conserva el
formato PHC completo. El servicio también permite detectar hashes que necesitan
actualizarse cuando cambien los parámetros.

Esta capa no crea administradores, no persiste contraseñas, no emite JWT y no
implementa el inicio de sesión. Los parámetros todavía deben medirse en el VPS
de Hetzner antes del despliegue.

## Tokens administrativos

La capa `app.core.tokens` emite y valida tokens de acceso firmados únicamente
con `HS256`. Cada token dura 15 minutos, recibe un `jti` único y contiene las
ocho claims establecidas en DT-014. La validación exige firma, algoritmo,
emisor, audiencia, vigencia, identidad y rol, con una tolerancia temporal
máxima de 30 segundos.

`JWT_SECRET` puede cargarse de forma aislada sin exigir PostgreSQL ni Telegram.
Debe tener al menos 32 caracteres y nunca se incorpora al repositorio. Esta
validación de longitud no reemplaza la generación aleatoria de al menos 256 bits
requerida para los entornos reales.

El servicio todavía no autentica credenciales, no consulta administradores, no
registra revocaciones y no protege endpoints FastAPI. Tampoco emite refresh
tokens.

La persistencia dispone de la tabla `tokens_revocados` para conservar un `jti`,
el administrador relacionado, la fecha de revocación y el vencimiento. El JWT
completo no forma parte del modelo. La cabeza actual de Alembic es
`0004_tokens_revocados`; puede inspeccionarse su reversión sin conexión con:

```bash
python -m alembic -c alembic.ini downgrade 0004_tokens_revocados:0003_administradores --sql
```

Todavía no existe lógica para registrar, consultar o eliminar revocaciones.

## Catálogo de platos

El modelo `Plato` inicia el catálogo persistente con nombre, descripción,
precio decimal y estado. Los platos permanecen inactivos por defecto y el
precio no puede ser negativo. La cabeza de Alembic es `0005_platos`.

Este incremento todavía no incorpora CRUD, imágenes, menús, stock, endpoints
ni integración con el bot o el panel.

## Programación de menús

El modelo `Menu` representa una oferta diaria mediante una fecha única y un
estado inactivo por defecto. La cabeza de Alembic es `0006_menus`.

Todavía no se asocian platos, stock o disponibilidad y no existen menús reales
registrados.

El modelo `DetalleMenu` relaciona cada menú con sus platos, conserva el stock
no negativo y comienza como no disponible. La combinación de menú y plato es
única. La cabeza de Alembic es `0007_detalles_menu`.

Todavía no existen operaciones que registren ofertas o descuenten stock.

El modelo `Pedido` conserva la cabecera vinculada con un cliente, el estado
inicial `BORRADOR`, el total, el destino fijo y un código de seguimiento
opcional mientras se prepara el pedido. El total no puede ser negativo y la
cabeza de Alembic es `0008_pedidos`.

Todavía no se incorporan detalles, cálculos, transiciones, servicios ni
interfaces para gestionar pedidos.

El modelo `DetallePedido` conserva el nombre, el precio unitario, la cantidad y
el subtotal utilizados en un pedido. Sus importes no pueden ser negativos y la
cantidad debe ser mayor que cero. La cabeza de Alembic es
`0009_detalles_pedido`.

Todavía no existen operaciones que creen detalles, calculen importes o
modifiquen stock.

## Verificación

Desde la carpeta `backend/`, ejecutar:

```bash
python -m unittest discover -s tests -v
```

Las pruebas confirman que los paquetes pueden importarse, comprueban el endpoint
de salud y verifican la configuración y las sesiones con valores ficticios. No
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
