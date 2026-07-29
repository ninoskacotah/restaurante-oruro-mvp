# Panel administrativo de Restaurant Las Retamas

Aplicación Vue 3 y Vite que consume la API REST del proyecto. Esta primera
entrega cubre autenticación, platos y programación de menús.

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

## Verificación

```bash
pnpm test
pnpm build
```

La compilación genera `dist/`, que no se versiona. En el VPS, el proxy inverso
deberá servir el panel y dirigir `/api` al backend bajo el mismo dominio.
