# Panel administrativo de Restaurant Las Retamas

Aplicación Vue 3 y Vite que consume la API REST del proyecto. Cubre
autenticación, platos, programación de menús, pedidos, clientes, repartidores
y reportes.

La segunda parte añade el tablero de pedidos, revisión manual de comprobantes,
asignación y reasignación, seguimiento con OpenStreetMap/Leaflet, fichas de
clientes y reportes calculados por la API. El mapa conserva el último punto y
advierte cuando supera 30 segundos sin actualización.

## Desarrollo local

Desde `frontend/`:

```bash
pnpm install
pnpm dev
```

Vite publica el panel local y redirige `/api` hacia FastAPI en
`http://127.0.0.1:8000`. Las credenciales y tokens no se escriben en archivos.
El JWT permanece en `sessionStorage`, desaparece al cerrar la pestaña o al
cerrar sesión y nunca se envía por URL.

La preparación integral de PostgreSQL, el administrador de prueba y el bot se
explica en [`docs/ejecucion-local.md`](../docs/ejecucion-local.md).

## Verificación

```bash
pnpm test
pnpm build
```

La compilación genera `dist/`, que no se versiona. En el VPS, el proxy inverso
deberá servir el panel y dirigir `/api` al backend bajo el mismo dominio.
