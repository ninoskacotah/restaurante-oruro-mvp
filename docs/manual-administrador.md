# Manual de usuario — Administrador

## Propósito

Este manual explica la operación del panel web de Restaurant Las Retamas. El
administrador gestiona la oferta diaria y coordina pedidos, pagos y repartos
desde una cuenta protegida.

## Iniciar y cerrar sesión

1. Abrir `http://localhost:5173` en el entorno local.
2. Escribir el usuario administrativo y su contraseña.
3. Pulsar **Ingresar**.
4. Al finalizar, utilizar **Cerrar sesión**.

Las rutas internas requieren un token vigente. Las credenciales deben crearse
mediante el comando administrativo y nunca publicarse en el repositorio.

## Gestionar platos

En **Platos** se puede:

1. registrar nombre, descripción y precio;
2. consultar el catálogo existente;
3. editar la información;
4. desactivar un plato que no deba utilizarse.

La desactivación conserva la trazabilidad histórica. Antes de guardar, deben
revisarse especialmente el precio y el estado activo.

## Programar el menú

En **Menús**:

1. seleccionar la fecha de vigencia;
2. incorporar platos del catálogo;
3. indicar el stock inicial;
4. marcar su disponibilidad;
5. actualizar stock o visibilidad cuando corresponda.

El bot consulta esta información. Un plato sin disponibilidad o con stock cero
no se presenta al cliente. El stock se descuenta cuando el pedido se confirma.

## Administrar pedidos y pagos

En **Pedidos**:

1. seleccionar un pedido del tablero;
2. revisar su detalle, total, ubicación e historial de estados;
3. abrir el comprobante de pago;
4. confirmar o rechazar manualmente el pago;
5. verificar el efecto del cambio en el estado y en la notificación al cliente.

La verificación de pago no es automática. Solo debe confirmarse cuando la
evidencia corresponda al pedido y sea legible. Si se rechaza, el cliente puede
enviar un nuevo comprobante.

## Registrar y asignar repartidores

En **Repartidores**:

1. registrar el `chat_id`, nombre y teléfono;
2. mantener habilitado el acceso operativo;
3. editar o deshabilitar el registro cuando sea necesario.

Desde el detalle de un pedido con pago confirmado, seleccionar un repartidor y
pulsar **Asignar**. El bot enviará la información al destinatario elegido. En
una reasignación debe comprobarse que la asignación anterior quedó cerrada y la
nueva figura como activa.

## Seguir el reparto

El detalle del pedido presenta el mapa de seguimiento:

- destino del cliente;
- última posición recibida del repartidor;
- momento de actualización;
- advertencia si la ubicación lleva más de 30 segundos sin actualizarse;
- historial de estados, incluida la llegada y la entrega.

La advertencia indica ausencia de actualizaciones recientes; no demuestra por sí
sola que el dispositivo esté apagado.

## Consultar clientes

En **Clientes** se selecciona una ficha para revisar el historial de pedidos y
la frecuencia calculada a partir de pedidos persistidos. Estos datos son de uso
interno y no deben incluirse sin protección en capturas o documentos.

## Consultar reportes

En **Reportes**:

1. seleccionar la fecha;
2. pulsar **Consultar**;
3. revisar ventas del día;
4. revisar platos más pedidos;
5. revisar el tiempo promedio desde `EN_CAMINO` hasta `ENTREGADO`.

Los valores proceden de los pedidos almacenados. Para una revisión académica,
pueden contrastarse con el detalle de los pedidos de la misma fecha.

## Orden recomendado de preparación

Antes de una demostración:

1. iniciar API, bot y panel;
2. comprobar `/api/health`;
3. iniciar sesión;
4. registrar los platos necesarios;
5. programar el menú del día con stock;
6. registrar y habilitar al repartidor;
7. confirmar que el QR de pago existe;
8. realizar un pedido de prueba completo.

## Seguridad y resolución de problemas

- No mostrar contraseñas, tokens, chat IDs, teléfonos, ubicaciones ni
  comprobantes en capturas públicas.
- Si la sesión expira, volver a iniciar sesión.
- Si el bot no muestra el menú, comprobar fecha, visibilidad y stock.
- Si el repartidor no recibe la asignación, comprobar su `chat_id`, acceso y
  ejecución del bot.
- Si el mapa no cambia, revisar la hora de la última ubicación y la conexión del
  repartidor.
- No modificar directamente la base de datos durante la demostración.
