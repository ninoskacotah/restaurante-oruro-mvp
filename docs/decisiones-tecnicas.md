# Bitácora de decisiones técnicas

## Propósito

Este documento registra las decisiones técnicas adoptadas durante el desarrollo
del MVP de Restaurant Las Retamas. Su finalidad es conservar el contexto, las
alternativas consideradas y las razones de cada elección para que puedan
revisarse, explicarse y actualizarse durante la evolución del proyecto.

La bitácora es un documento vivo. Una decisión posterior no borrará la anterior:
si una elección cambia, el registro original pasará a estado `Reemplazada` y se
creará una nueva entrada que explique el cambio.

## Estados utilizados

- `Aprobada`: forma parte del diseño vigente.
- `Pendiente`: requiere análisis y aprobación en un Issue posterior.
- `Reemplazada`: dejó de estar vigente y señala la decisión que la sustituyó.

Cada registro contiene un identificador, estado, contexto, alternativas,
decisión, justificación y consecuencias. Las comparaciones expresan criterios de
diseño; no representan pruebas de rendimiento si estas no se indican de forma
explícita.

## DT-001 — Lenguaje principal del backend y del bot

**Estado:** Aprobada.

### Contexto

El bot de Telegram y la API requieren un lenguaje con soporte para programación
asíncrona, servicios web, acceso a PostgreSQL y automatización.

### Alternativas consideradas

- Python 3.12.
- Node.js con JavaScript.

### Decisión

Utilizar Python 3.12 para el bot y el backend.

### Justificación

Python ofrece una sintaxis legible y un ecosistema compatible con Aiogram,
FastAPI y SQLAlchemy. Emplear el mismo lenguaje en el bot y la API reduce la
cantidad de entornos que deben mantenerse y facilita compartir criterios de
validación y modelos conceptuales.

### Consecuencias

El bot y la API compartirán versión de Python y prácticas de calidad. El panel
continuará utilizando JavaScript porque se ejecutará como aplicación web en el
navegador.

## DT-002 — Framework del bot de Telegram

**Estado:** Aprobada.

### Contexto

El canal conversacional debe utilizar Telegram Bot API y sus capacidades nativas
para botones, fotografías, ubicaciones y `live location`.

### Alternativas consideradas

- Aiogram.
- python-telegram-bot.
- Consumo directo de Telegram Bot API.

### Decisión

Utilizar Aiogram para desarrollar el bot.

### Justificación

Aiogram está orientado a la programación asíncrona y proporciona abstracciones
para actualizaciones, comandos, filtros, botones y estados conversacionales.
Frente al consumo directo de la API, evita implementar manualmente tareas de
enrutamiento y deserialización. python-telegram-bot también cubre el dominio,
pero Aiogram mantiene coherencia con el enfoque asíncrono aprobado para este
proyecto.

### Consecuencias

Los handlers deberán evitar operaciones bloqueantes. El estado persistente del
negocio no dependerá únicamente de memoria interna de Aiogram y las reglas
seguirán centralizadas en la API.

## DT-003 — Framework de la API REST

**Estado:** Aprobada.

### Contexto

El bot y el panel necesitan una interfaz común para ejecutar las reglas del
negocio y acceder a la persistencia.

### Alternativas consideradas

- FastAPI.
- Flask.
- Django con Django REST Framework.

### Decisión

Utilizar FastAPI para la API REST.

### Justificación

FastAPI permite declarar validaciones y contratos de entrada y salida de forma
explícita, genera documentación de la API y se integra con el modelo asíncrono
de Python. Flask requiere seleccionar e integrar más componentes por separado.
Django ofrece una plataforma más amplia, pero el MVP ya separa el panel Vue del
backend y no requiere su sistema de plantillas.

### Consecuencias

Las reglas se expondrán mediante endpoints con esquemas definidos. La
autenticación, el manejo uniforme de errores y la organización de dependencias
deberán concretarse antes de implementar los módulos funcionales.

## DT-004 — Sistema gestor de base de datos

**Estado:** Aprobada.

### Contexto

El sistema necesita persistir información relacionada sobre clientes, catálogo,
pedidos, pagos, asignaciones, ubicaciones y estados, y conservarla después de
reinicios.

### Alternativas consideradas

- PostgreSQL.
- MySQL.
- SQLite.

### Decisión

Utilizar PostgreSQL como base de datos relacional compartida.

### Justificación

PostgreSQL permite expresar relaciones, restricciones, transacciones e índices
adecuados para el modelo definido. SQLite simplifica entornos pequeños, pero no
es la opción elegida para el servicio concurrente previsto en el VPS. MySQL
también es relacional y viable, aunque PostgreSQL se alinea con el stack
aprobado y ofrece las capacidades necesarias sin incorporar otro componente.

### Consecuencias

Los entornos de desarrollo y despliegue deberán disponer de PostgreSQL. Los
cambios del esquema requerirán migraciones reproducibles y las operaciones de
stock y transición de estados deberán respetar límites transaccionales.

## DT-005 — Acceso a datos desde Python

**Estado:** Aprobada.

### Contexto

FastAPI necesita representar las entidades y ejecutar operaciones contra
PostgreSQL sin trasladar consultas a los componentes de Telegram o del panel.

### Alternativas consideradas

- SQLAlchemy.
- Consultas SQL directas mediante un controlador de PostgreSQL.
- Django ORM.

### Decisión

Utilizar SQLAlchemy como ORM y capa de acceso a datos.

### Justificación

SQLAlchemy permite representar relaciones y transacciones desde Python sin
ocultar la necesidad de comprender el modelo relacional. Las consultas directas
ofrecen control, pero aumentarían el trabajo repetitivo para mapear resultados y
mantener operaciones. Django ORM está integrado principalmente con el
ecosistema de Django, que no fue seleccionado para la API.

### Consecuencias

Los modelos de persistencia se concentrarán en el backend. La implementación
deberá prevenir cargas innecesarias, definir correctamente las relaciones y
mantener migraciones separadas de los modelos.

## DT-006 — Framework del panel administrativo

**Estado:** Aprobada.

### Contexto

El administrador necesita una interfaz web reactiva para gestionar el catálogo,
revisar pedidos y pagos, asignar repartidores y consultar el seguimiento.

### Alternativas consideradas

- Vue 3.
- React.
- Svelte.

### Decisión

Utilizar Vue 3 con una arquitectura basada en componentes.

### Justificación

Vue 3 permite organizar la interfaz en componentes y gestionar estado reactivo
con una curva de adopción adecuada para el alcance del panel. React y Svelte
también permiten construir una aplicación de este tipo, pero no aportan un
requisito exclusivo que justifique cambiar el stack ya aprobado.

### Consecuencias

El panel será una aplicación separada que consumirá la API. Será necesario
definir rutas, manejo de sesión, componentes reutilizables y estados de carga y
error.

## DT-007 — Herramienta de desarrollo del frontend

**Estado:** Aprobada.

### Contexto

El proyecto requiere iniciar el entorno del panel, transformar sus módulos y
generar una versión optimizada para despliegue.

### Alternativas consideradas

- Vite.
- Configuración manual con Webpack.

### Decisión

Utilizar Vite para el desarrollo y la compilación del panel Vue.

### Justificación

Vite ofrece una configuración inicial compatible con Vue 3 y evita mantener
desde el comienzo una configuración manual de empaquetado. Webpack es flexible,
pero esa flexibilidad no constituye una necesidad específica del MVP.

### Consecuencias

Los comandos del frontend dependerán de la configuración de Vite. Las variables
de entorno públicas deberán seguir su convención y no podrán contener secretos.

## DT-008 — Lenguaje del panel

**Estado:** Aprobada.

### Contexto

La interfaz necesita implementar componentes, validaciones de presentación y
comunicación con la API.

### Alternativas consideradas

- JavaScript.
- TypeScript.

### Decisión

Utilizar JavaScript en el panel administrativo.

### Justificación

JavaScript satisface el alcance aprobado y evita incorporar en esta etapa una
capa adicional de tipado y configuración. TypeScript podría aportar controles
estáticos en un proyecto de mayor tamaño, pero no es obligatorio para cumplir
los flujos definidos.

### Consecuencias

Los contratos con la API deberán mantenerse claros mediante esquemas,
validaciones y pruebas. Si el crecimiento del panel justifica TypeScript, el
cambio necesitará una nueva decisión y un Issue propio.

## DT-009 — Autenticación del panel

**Estado:** Aprobada.

### Contexto

Las funciones administrativas no pueden quedar disponibles para usuarios sin
autorización y el panel separado necesita acreditar su sesión ante la API.

### Alternativas consideradas

- Tokens JSON Web Token.
- Sesiones almacenadas en el servidor con una cookie de sesión.

### Decisión

Utilizar JWT como mecanismo previsto para proteger las solicitudes
administrativas.

### Justificación

JWT permite que el panel presente un token firmado a la API sin introducir una
segunda aplicación de sesiones. Esta elección no elimina la necesidad de
proteger credenciales, validar permisos y reducir la exposición del token.

### Consecuencias

La firma, duración, almacenamiento, renovación y revocación todavía deben
definirse. Hasta resolver esas reglas en un Issue específico, esta decisión no
se considera una implementación completa de seguridad.

## DT-010 — Control de versiones y gestión del trabajo

**Estado:** Aprobada.

### Contexto

El proyecto académico exige trazabilidad mediante Issues, ramas, commits, Pull
Requests, Projects y cierre gradual del trabajo.

### Alternativas consideradas

No existe una alternativa de plataforma dentro de las restricciones del
proyecto: Git y GitHub forman parte del flujo exigido. La decisión consiste en
aplicarlos conforme a `CONTRIBUTING.md`.

### Decisión

Utilizar Git como sistema de control de versiones y GitHub para alojar el
repositorio y gestionar el flujo de contribución.

### Justificación

La elección satisface las condiciones académicas y proporciona la trazabilidad
requerida entre Issue, rama, commits y Pull Request.

### Consecuencias

`main` y `develop` permanecerán protegidas. Cada incremento utilizará una rama
asociada a su Issue, auto-revisión y squash merge; la rama se eliminará después
de la integración.

## DT-011 — Proveedor objetivo del VPS

**Estado:** Aprobada.

### Contexto

El sistema deberá ejecutarse en un entorno accesible que aloje los componentes
necesarios para la demostración y permita una configuración reproducible.

### Alternativas consideradas

- VPS de Hetzner.
- VPS de DigitalOcean.
- Servicio equivalente en AWS.

### Decisión

Utilizar un VPS de Hetzner como entorno objetivo de despliegue.

### Justificación

La autora seleccionó Hetzner para disponer de un servidor administrable donde
puedan desplegarse el backend, el bot, el panel y PostgreSQL conforme al diseño
que se apruebe. Las otras alternativas ofrecen capacidades equivalentes para
este alcance, pero incorporar otro proveedor no genera una ventaja necesaria
para el proyecto.

### Consecuencias

La elección del proveedor no define por sí sola la arquitectura física. El
sistema todavía no se considera desplegado y quedan pendientes la preparación
del servidor, procesos, proxy, dominio, certificados, variables de entorno,
respaldos y procedimiento reproducible.

## DT-012 — Almacenamiento de comprobantes y evidencias

**Estado:** Aprobada.

### Contexto

El cliente envía una fotografía del comprobante de pago y el repartidor puede
usar una fotografía como evidencia de entrega. Estos archivos deben persistir,
quedar asociados con el registro correcto y poder consultarse desde funciones
autorizadas del panel.

### Alternativas consideradas

- Archivos persistentes en el sistema de archivos del VPS de Hetzner.
- Identificadores `file_id` de Telegram como referencia permanente.
- Almacenamiento externo de objetos.
- Combinación de una referencia de Telegram y una copia persistente propia.

### Decisión

Descargar las fotografías recibidas mediante Telegram y conservarlas en un
directorio persistente y configurable del VPS. PostgreSQL almacenará los
metadatos y una ruta relativa, no el contenido binario.

### Justificación

El directorio persistente aprovecha el VPS ya previsto y evita añadir para el
MVP otro servicio con configuración, credenciales y costos propios. Una copia
controlada por la aplicación evita usar Telegram como único repositorio. El
almacenamiento de objetos ofrece mejores opciones de crecimiento y
disponibilidad, pero no resulta necesario para el volumen aún no determinado de
este MVP.

La alternativa combinada conservaría dos referencias y exigiría definir cuál es
la fuente principal. Para el alcance inicial se prefiere una sola copia
persistente administrada por la aplicación.

### Consecuencias

Los archivos se guardarán fuera de los recursos públicos del panel. Sus nombres
serán generados por el sistema y las rutas almacenadas serán relativas. Antes de
aceptarlos se validarán el formato y un límite de tamaño configurable. El acceso
deberá pasar por operaciones autenticadas y autorizadas.

La base de datos conservará, según el tipo de registro, el pedido o la
asignación relacionados, la ruta, el nombre generado, el tipo MIME, el tamaño y
la fecha. La eliminación deberá coordinar el registro y el archivo para evitar
referencias rotas o archivos sin relación.

Esta estrategia depende del disco de un solo VPS. Los respaldos deberán incluir
PostgreSQL y el directorio persistente de forma coordinada. Si el volumen, la
disponibilidad o la distribución del sistema aumentan, se evaluará el cambio a
almacenamiento de objetos mediante una nueva decisión.

El directorio, los límites concretos, las operaciones de carga y consulta y la
automatización de los respaldos todavía no están implementados.

## DT-013 — Tecnología del mapa administrativo

**Estado:** Aprobada.

### Contexto

El panel debe representar el destino, la última posición del repartidor y el
trayecto cronológico de una entrega. El alcance requiere un mapa interactivo 2D,
pero no navegación, cálculo de rutas, geocodificación ni visualizaciones
vectoriales avanzadas.

### Alternativas consideradas

- Leaflet con OpenStreetMap como fuente cartográfica inicial.
- MapLibre GL JS.
- Google Maps.
- Mapbox.

### Decisión

Utilizar Leaflet en el panel Vue 3 y OpenStreetMap como fuente cartográfica
inicial. La URL del proveedor de teselas permanecerá configurable.

### Justificación

Leaflet proporciona mapas, marcadores, líneas, capas y controles suficientes
para representar el seguimiento 2D del MVP. MapLibre GL JS permite trabajar con
teselas vectoriales y estilos más avanzados, capacidades que no son necesarias
para el alcance vigente.

Google Maps y Mapbox también permiten construir la visualización, pero añaden la
gestión de cuentas, credenciales y condiciones de servicio específicas. La
combinación de Leaflet y OpenStreetMap permite comenzar con una solución acorde
al diseño simple, siempre que se respeten la atribución y la política del
servicio de teselas.

### Consecuencias

El mapa mostrará marcadores diferenciados para el destino y la posición actual,
una línea formada por las ubicaciones ordenadas de la asignación activa y la
fecha de la última actualización. También deberá advertir cuando el último punto
supere el intervalo que posteriormente se defina como desactualizado.

La atribución a OpenStreetMap permanecerá visible. No se implementarán descarga
masiva, precarga de áreas ni uso sin conexión de sus teselas públicas, y se
respetarán las directivas de caché. El servicio público funciona sin garantía de
disponibilidad, de modo que la aplicación deberá permitir cambiar la URL del
proveedor mediante configuración.

Las referencias consultadas para esta decisión son:

- documentación de Leaflet: <https://leafletjs.com/reference>;
- documentación de MapLibre GL JS:
  <https://maplibre.org/maplibre-gl-js/docs>;
- política de teselas de OpenStreetMap:
  <https://operations.osmfoundation.org/policies/tiles/>.

La instalación de Leaflet, el componente Vue, la consulta de ubicaciones y la
actualización de la vista se implementarán en Issues posteriores.

## DT-014 — Seguridad de autenticación JWT

**Estado:** Aprobada.

### Contexto

El panel necesita autenticar al administrador ante una sola API FastAPI. La
decisión inicial de utilizar JWT debe completarse con reglas de firma, duración,
claims, almacenamiento, validación y cierre de sesión.

### Alternativas consideradas

- `HS256`, con un secreto compartido por el único servicio que emite y valida.
- `RS256`, con una clave privada de firma y una clave pública de verificación.
- Token de acceso con refresh token.
- Token de acceso de corta duración sin refresh token.
- Persistencia del token en almacenamiento web.
- Conservación del token únicamente en memoria.

### Decisión

Utilizar tokens de acceso firmados exclusivamente con `HS256`, con una duración
de 15 minutos y una tolerancia temporal máxima de 30 segundos. El secreto tendrá
al menos 256 bits aleatorios, se obtendrá desde el entorno y nunca se almacenará
en Git.

El MVP no utilizará refresh token. El panel conservará el token únicamente en
memoria y lo enviará mediante `Authorization: Bearer`. Al expirar el token,
recargar la página o cerrar el navegador, el administrador deberá autenticarse
de nuevo.

Las claims obligatorias serán `sub`, `role`, `iss`, `aud`, `iat`, `nbf`, `exp`
y `jti`. `role` tendrá el valor `admin`, `iss` será
`restaurant-las-retamas-api` y `aud` será
`restaurant-las-retamas-panel`.

### Justificación

`HS256` resulta proporcional a una arquitectura donde una sola API controla la
emisión y validación. `RS256` sería apropiado si varios servicios necesitaran
verificar tokens sin compartir la capacidad de firmarlos, situación que no
forma parte del MVP.

La duración corta limita el tiempo de uso de un token comprometido. Omitir el
refresh token evita incorporar almacenamiento, rotación y detección de
reutilización antes de que exista esa necesidad. Mantener el token en memoria
evita dejarlo persistente en `localStorage` o `sessionStorage`, a cambio de que
una recarga requiera iniciar sesión nuevamente.

### Consecuencias

La API fijará `HS256` en su configuración y no confiará en el encabezado del JWT
para elegir el algoritmo. Rechazará `alg: none` y validará firma, emisor,
audiencia, vigencia, identidad, rol y revocación en cada endpoint
administrativo. También comprobará que el administrador continúe activo.

El cierre de sesión eliminará el token de la memoria del panel y registrará su
`jti` en una lista de revocación persistente hasta `exp`. Se conservarán el
identificador, el administrador, la fecha de revocación y la expiración, pero no
el token completo.

Las credenciales y tokens solo circularán mediante HTTPS. Las respuestas de
error serán genéricas y los registros no expondrán contraseñas, secretos ni
tokens completos. El JWT no contendrá información sensible innecesaria.

Las referencias utilizadas son:

- RFC 8725: <https://datatracker.ietf.org/doc/rfc8725/>;
- OWASP REST Security Cheat Sheet:
  <https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html>;
- OWASP Secrets Management Cheat Sheet:
  <https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html>.

La implementación de endpoints, la lista de revocación, el panel y la
protección de contraseñas corresponden a Issues posteriores.

## Decisiones pendientes

Las siguientes decisiones requieren Issues separados:

| Tema | Motivo para mantenerlo pendiente |
|---|---|
| Migraciones de base de datos | Debe seleccionarse y preparar el mecanismo junto con la estructura del backend |
| Arquitectura física del VPS | Deben definirse procesos, red, proxy, dominio, HTTPS y respaldos |

Ninguna opción pendiente se presentará como seleccionada o implementada hasta
que su Issue sea analizado, aprobado e integrado.
