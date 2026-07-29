# Validación integral del MVP

## Propósito

Este documento registra las pruebas ejecutadas sobre el MVP de Restaurant Las
Retamas en el entorno local. Cada resultado se basa en una comprobación real;
los escenarios todavía no ejecutados permanecen identificados como pendientes.

## Entorno validado

- Windows.
- PostgreSQL 15 local.
- API FastAPI en `http://127.0.0.1:8000`.
- Panel Vue en `http://localhost:5173`.
- Bot de Telegram ejecutado mediante long polling.
- QR, comprobantes y evidencias configurados como datos de prueba.

Las contraseñas, el token, los teléfonos, los identificadores de chat y la
ubicación precisa no forman parte de las evidencias versionadas.

## Matriz de resultados

| Escenario | Resultado esperado | Estado | Resultado observado |
|---|---|---|---|
| Inicio de sesión administrativo | Permitir el acceso con una cuenta activa | Aprobado | El administrador de prueba accedió al panel. |
| Catálogo y menú diario | Mostrar únicamente ofertas activas, visibles y con stock | Aprobado | El bot presentó el menú después de activar su cabecera. |
| Carrito | Calcular cantidades, subtotales y total y permitir confirmar | Aprobado | Se completó el carrito y se corrigió la navegación posterior a la cantidad. |
| Confirmación y ubicación | Crear el pedido y conservar su destino | Aprobado | El pedido avanzó a espera de comprobante con ubicación persistida. |
| QR y comprobante | Mostrar el QR y recibir una imagen sin confirmar el pago automáticamente | Aprobado | El comprobante quedó pendiente de revisión manual. |
| Revisión y asignación | Confirmar el pago y asignar un repartidor activo | Aprobado | El panel confirmó el pago y creó la asignación. |
| Operación del repartidor | Confirmar recepción, trayecto, llegada y entrega | Aprobado | La entrega terminó con evidencia fotográfica. |
| Persistencia final | Dejar el pedido entregado y cerrar la asignación | Aprobado | PostgreSQL registró `ENTREGADO`, asignación inactiva y evidencia. |
| Seguimiento | Mostrar el último punto recibido | Aprobado | El panel representó la ubicación de prueba en el mapa. |
| Pérdida y recuperación de señal | Conservar el último punto, advertir después de 30 segundos y reanudar el mismo trayecto | No ejecutado manualmente | La prueba con el celular se omitió por decisión de la autora. El refresco, la advertencia temporal y la conservación persistente tienen cobertura automatizada, pero no se declara evidencia manual. |
| Reportes | Calcular ventas, platos y tiempo desde datos persistidos | Aprobado | El panel contabilizó el pedido entregado. |
| Rechazo de comprobante y reintento | Permitir otro comprobante sin confirmar el pago rechazado | Aprobado | Se rechazaron dos comprobantes, el bot notificó el segundo rechazo y aceptó un nuevo envío que posteriormente fue aprobado. |
| Cancelación y recuperación de stock | Cancelar en un estado permitido, reponer unidades y cerrar la asignación | Aprobado con corrección | El pedido pasó a `CANCELADO` y el stock regresó de 37 a 38. Se detectó y corrigió una asignación que permanecía activa. |
| Stock insuficiente | Rechazar una cantidad mayor al stock sin alterar el carrito | Aprobado automatizado | `test_agregar_rejects_quantity_above_stock` verifica que la operación no modifique el carrito. |
| Repartidor no autorizado | Impedir consultar u operar asignaciones | Aprobado automatizado | `test_unknown_courier_is_rejected` y las pruebas de actor incorrecto verifican el rechazo. |
| Reasignación | Cerrar la asignación anterior y no mezclar el pedido | Aprobado automatizado | `test_reasignar_closes_previous_assignment` comprueba el cierre y la conservación del pedido. |
| Notificaciones administrativas | Informar rechazo, pago confirmado y asignación al cliente | Aprobado | El cliente recibió los tres mensajes durante el segundo pedido. |

## Evidencias sanitizadas

1. [Inicio de sesión](evidencias/validacion-local/01-inicio-sesion.png).
2. [Pedido entregado](evidencias/validacion-local/02-pedido-entregado.png).
3. [Catálogo registrado](evidencias/validacion-local/03-catalogo.png).
4. [Menú con stock](evidencias/validacion-local/04-menu-stock.png).
5. [Seguimiento con ubicación protegida](evidencias/validacion-local/05-seguimiento-protegido.png).
6. [Repartidor con datos protegidos](evidencias/validacion-local/06-repartidor-protegido.png).
7. [Clientes con datos protegidos](evidencias/validacion-local/07-clientes-protegidos.png).
8. [Reportes operativos](evidencias/validacion-local/08-reportes.png).

## Incidencias detectadas durante la integración

- Windows utilizaba un bucle asíncrono incompatible con Psycopg en Alembic,
  el administrador inicial y el bot. Se configuró `SelectorEventLoop`.
- El carrito no mostraba acciones después de registrar una cantidad. Se
  incorporó nuevamente el resumen y su teclado.
- La aprobación del pago y la asignación no ejecutaban las notificaciones ya
  definidas para el cliente. Se conectaron ambos eventos.
- Los archivos locales de QR, comprobantes y entrega no estaban excluidos de
  forma conjunta. Se añadió `backend/var/` a `.gitignore`.
- La cancelación posterior a una asignación recuperaba el stock, pero dejaba
  activo al repartidor. La cancelación ahora cierra la asignación en la misma
  transacción y se reparó el único registro local afectado.

Estas incidencias fueron corregidas y verificadas durante la integración local
del Issue #95. Los escenarios pendientes de esta matriz se actualizarán
únicamente después de ejecutarse.

## Limitación conocida

La entrega mediante `/entrega CODIGO` conserva la referencia escrita por el
repartidor, pero el MVP no genera ni valida un código de un solo uso entregado
previamente al cliente. La evidencia fotográfica es la alternativa comprobada
en el flujo local.

## Auditoría final previa a la versión estable

El 29 de julio de 2026 se repitieron las verificaciones automatizadas sobre
`develop` después de integrar la documentación de entrega:

| Verificación | Resultado |
|---|---|
| Backend: `python -m unittest discover -s tests -v` | 167 pruebas correctas |
| Frontend: `pnpm test` | 10 pruebas correctas en 4 archivos |
| Frontend: `pnpm build` | Compilación de producción correcta |
| Secretos locales | `.env` y `backend/var/` ignorados por Git |

La primera orden intentada con `pytest` no pudo ejecutarse porque esa herramienta
no forma parte de las dependencias del proyecto. Se utilizó el ejecutor real de
la suite, `unittest`, y se corrigió el README para que el procedimiento sea
reproducible.

Esta auditoría no sustituye la captura real del bot requerida para la entrega ni
la finalización personal de la declaración de autoría.
