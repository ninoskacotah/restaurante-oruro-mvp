# Manual de usuario — Repartidor

## Propósito

Este manual describe el uso del bot de Telegram por parte del repartidor de
Restaurant Las Retamas, desde su registro administrativo hasta la confirmación
de una entrega.

## Registro y acceso

Antes de utilizar el bot, el administrador debe registrar en el panel:

- el `chat_id` de Telegram;
- el nombre;
- el teléfono;
- el acceso habilitado.

El repartidor inicia la conversación con `/start`. El bot comprueba el
`chat_id` y solo presenta las acciones del rol cuando el registro está activo.
No se comparten códigos ni cuentas entre repartidores.

## Recibir una asignación

Cuando el administrador asigna un pedido, el bot envía:

- número del pedido;
- platos y cantidades;
- importe total y estado del pago;
- datos de entrega y referencia;
- ubicación del destino como objeto de Telegram;
- nombre y contacto del cliente;
- botón de acuse de recibo.

El repartidor debe revisar los datos y pulsar el acuse. Si el pedido fue
reasignado antes de la confirmación, el bot informará que la asignación ya no
está vigente.

## Iniciar el trayecto

1. Confirmar la recepción del pedido.
2. Utilizar la opción para iniciar el recorrido.
3. Compartir una ubicación en tiempo real desde Telegram.
4. Mantener Telegram y la conexión disponibles durante el trayecto.

El sistema almacena las actualizaciones con fecha, hora y coordenadas. El panel
refresca el seguimiento y advierte cuando la última ubicación supera el umbral
definido de 30 segundos.

## Pérdida de señal

Si dejan de recibirse actualizaciones:

1. comprobar la conexión móvil y los permisos de ubicación;
2. abrir nuevamente Telegram;
3. reanudar o volver a compartir la ubicación en tiempo real;
4. informar al administrador si el seguimiento no se recupera.

La falta temporal de señal no debe registrarse como llegada ni entrega.

## Confirmar la llegada

Al llegar a la ubicación indicada, utilizar la acción de llegada. Este evento es
distinto de la entrega y permite que el panel y el cliente sepan que el
repartidor se encuentra en destino.

## Confirmar la entrega

La entrega requiere evidencia. Según el flujo disponible:

- enviar una fotografía solicitada por el bot; o
- utilizar `/entrega CODIGO`, reemplazando `CODIGO` por el código entregado por
  el cliente.

No debe confirmarse una entrega antes de entregar efectivamente el pedido. Una
vez aceptada la evidencia, el pedido pasa al estado final y el cliente recibe la
notificación correspondiente.

## Reasignación

Cuando el administrador reasigna un pedido:

- la asignación anterior deja de estar activa;
- el repartidor anterior no debe continuar operando el pedido;
- el nuevo repartidor recibe el detalle completo;
- las ubicaciones posteriores quedan asociadas a la nueva asignación.

## Situaciones frecuentes

- **El bot no reconoce al repartidor:** verificar con el administrador el
  `chat_id` y que el acceso esté habilitado.
- **No llega una asignación:** comprobar que el bot esté iniciado y que el
  administrador haya seleccionado el repartidor correcto.
- **No se acepta el acuse:** el pedido puede haber sido reasignado o cancelado.
- **No se acepta la ubicación:** compartir una ubicación en tiempo real desde
  Telegram, no un texto ni una captura del mapa.
- **No se acepta el código:** comprobarlo con el cliente y respetar mayúsculas,
  números y formato indicado.

## Protección de datos

La información del pedido se utiliza únicamente para realizar la entrega. No
debe copiarse, publicarse ni conservarse fuera del sistema.
