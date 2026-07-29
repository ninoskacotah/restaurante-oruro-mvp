# Manual de usuario — Cliente

## Propósito

Este manual explica cómo realizar y seguir un pedido desde el bot de Telegram
de Restaurant Las Retamas. El cliente se identifica mediante su cuenta de
Telegram y no necesita acceder al panel administrativo.

## Requisitos

- Disponer de Telegram con acceso a Internet.
- Abrir el bot autorizado del restaurante.
- Permitir el envío de ubicación cuando Telegram lo solicite.
- Tener una imagen legible del comprobante de pago.

## Iniciar la atención

1. Abrir la conversación con el bot.
2. Enviar `/start`.
3. Seguir las opciones mostradas por el bot.

El perfil queda relacionado con el `chat_id` de Telegram para reconocer al
cliente en futuras interacciones.

## Consultar el menú y preparar el carrito

1. Solicitar el menú disponible.
2. Elegir un plato mediante los botones interactivos.
3. Indicar una cantidad válida.
4. Repetir la selección para agregar platos diferentes.
5. Revisar el detalle y el total del carrito.
6. Modificar cantidades o eliminar un elemento si es necesario.

El bot muestra únicamente platos habilitados para la fecha actual y con stock.
Si una cantidad supera la disponibilidad, debe elegirse una cantidad menor.

## Confirmar el pedido

1. Revisar platos, cantidades y total.
2. Pulsar la opción de confirmación.
3. Compartir la ubicación mediante el botón nativo de Telegram.
4. Añadir la referencia de entrega solicitada por el bot.

La ubicación se almacena vinculada al pedido y queda visible para la operación
administrativa.

## Enviar el pago

1. Recibir el QR de pago como imagen.
2. Realizar el pago fuera del bot.
3. Enviar una fotografía legible del comprobante.
4. Esperar la revisión del administrador.

La validación del comprobante es manual. El envío de la fotografía no significa
que el pago haya sido aceptado. El bot notificará si fue rechazado o confirmado.
Ante un rechazo, debe enviarse un nuevo comprobante válido.

## Seguir el pedido

Después de confirmar el pago, el cliente recibe el código de seguimiento y
notificaciones cuando:

- el pedido es asignado;
- el repartidor inicia el trayecto;
- el repartidor llega al destino;
- la entrega queda confirmada;
- el pedido es cancelado cuando la transición todavía está permitida.

El código de entrega debe comunicarse únicamente al repartidor que llegó con el
pedido.

## Cancelar o reiniciar

- `/cancelar` detiene el flujo en curso o solicita la cancelación cuando el
  estado lo permite.
- `/reiniciar` limpia el contexto conversacional y vuelve a presentar las
  opciones iniciales.
- `/start` permite volver al inicio de la atención.

Después de la confirmación del pago, la cancelación queda restringida para
proteger la consistencia de la preparación y el reparto.

## Situaciones frecuentes

- **No aparece un plato:** no está habilitado para hoy o no tiene stock.
- **La cantidad es rechazada:** supera el stock o no tiene un formato válido.
- **El bot pide ubicación:** debe utilizarse el objeto de ubicación de Telegram,
  no una dirección escrita como sustituto.
- **El comprobante es rechazado:** revisar que la fotografía sea legible y
  volver a enviarla.
- **Un botón fue pulsado dos veces:** el sistema verifica el estado vigente para
  evitar duplicar el efecto.
- **Mensaje fuera de contexto:** utilizar `/start` o `/reiniciar`.

## Protección de datos

No enviar contraseñas, tokens ni información bancaria adicional. La fotografía
debe mostrar solamente la evidencia necesaria para revisar el pago.
