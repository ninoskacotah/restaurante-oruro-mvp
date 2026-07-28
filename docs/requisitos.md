# Requisitos del sistema

## Propósito del documento

Este documento reúne las historias de usuario y los criterios de aceptación del
MVP de pedidos de Restaurant Las Retamas. Su contenido se ampliará de forma
gradual para cubrir los roles cliente, repartidor y administrador.

En este incremento se documenta únicamente el flujo del cliente. Las historias
del repartidor y del administrador se incorporarán en Issues posteriores y no
se presentan todavía como documentación terminada.

## Historias de usuario del cliente

### HU-C01 — Reconocimiento persistente del cliente

**Como cliente,
quiero que el bot reconozca mi cuenta de Telegram,
para conservar mi identificación aunque el sistema se reinicie.**

#### Criterios de aceptación

- El cliente se identifica mediante su `chat_id`.
- El perfil queda almacenado en la base de datos.
- Si el bot se reinicia, vuelve a reconocer al cliente.
- Un mismo `chat_id` no genera perfiles duplicados.

### HU-C02 — Consulta del menú vigente

**Como cliente,
quiero consultar el menú disponible del día,
para elegir platos que realmente puedan pedirse.**

#### Criterios de aceptación

- El menú se obtiene desde la base de datos.
- Solo aparecen platos habilitados para la fecha actual.
- Solo aparecen platos con stock mayor a cero.
- Cada opción muestra el nombre y el precio.
- Los platos se presentan mediante `InlineKeyboardMarkup`.
- Los cambios efectuados en el panel se reflejan en una nueva consulta del
  menú.
- Un plato agotado o no habilitado no puede seleccionarse.

### HU-C03 — Selección de platos y cantidades

**Como cliente,
quiero agregar distintos platos y definir sus cantidades,
para conformar un pedido según mis preferencias.**

#### Criterios de aceptación

- El cliente puede agregar más de un plato diferente.
- Puede indicar una cantidad válida para cada plato.
- No se aceptan cantidades iguales o menores que cero.
- La cantidad no puede superar el stock disponible.
- Una entrada inválida no interrumpe ni elimina el pedido en curso.
- El sistema informa claramente cuando la cantidad solicitada no está
  disponible.

### HU-C04 — Administración del carrito

**Como cliente,
quiero consultar y modificar mi carrito,
para corregir el pedido antes de confirmarlo.**

#### Criterios de aceptación

- El carrito muestra platos, cantidades, precios unitarios y subtotales.
- El total corresponde a la suma de todos los subtotales.
- El cliente puede cambiar la cantidad de un producto.
- La nueva cantidad se valida nuevamente contra el stock.
- El cliente puede eliminar productos.
- Al eliminar el último producto, el carrito queda vacío.
- El total se recalcula después de cada modificación.
- Antes de confirmar se vuelve a validar la disponibilidad.

### HU-C05 — Registro de la ubicación de entrega

**Como cliente,
quiero enviar mi ubicación de entrega mediante Telegram,
para indicar dónde debe entregarse el pedido.**

#### Criterios de aceptación

- El bot solicita una ubicación mediante la capacidad nativa de Telegram.
- Se recibe un objeto `Location`, no solamente una dirección escrita.
- Se almacenan la latitud y longitud asociadas al pedido.
- La ubicación queda visible desde el panel administrativo.
- Un mensaje que no contenga una ubicación válida no hace avanzar el flujo.
- El bot explica cómo volver a enviar la ubicación correctamente.

### HU-C06 — Envío del comprobante de pago

**Como cliente,
quiero recibir el código QR y enviar una fotografía de mi comprobante,
para solicitar la verificación del pago de mi pedido.**

#### Criterios de aceptación

- El QR se envía como imagen mediante `sendPhoto`.
- El bot solicita una fotografía del comprobante.
- Una entrada que no sea una fotografía válida no se registra como
  comprobante.
- La fotografía queda almacenada y asociada al pedido correcto.
- El comprobante puede visualizarse desde el panel.
- El envío del comprobante no marca automáticamente el pedido como pagado.
- El estado pagado solo se establece mediante confirmación manual desde el
  panel.
- El cliente recibe una notificación cuando el pago es confirmado.

### HU-C07 — Seguimiento del pedido

**Como cliente,
quiero recibir un código de seguimiento y conocer el estado de mi pedido,
para saber cómo avanza hasta la entrega.**

#### Criterios de aceptación

- Al confirmarse el pedido se genera un código de seguimiento.
- El código identifica de forma única al pedido.
- El cliente puede consultar el estado de su pedido.
- Recibe una notificación ante cada cambio relevante de estado.
- Las notificaciones diferencian que el pedido está en camino, que el
  repartidor llegó y que fue entregado.
- El estado mostrado coincide con el registrado en la base de datos y el panel.
- Un cliente no puede consultar mediante su flujo pedidos pertenecientes a otro
  cliente.

### HU-C08 — Cancelación y reinicio del flujo

**Como cliente,
quiero cancelar o reiniciar una conversación de pedido,
para abandonar un proceso o comenzar nuevamente de forma controlada.**

#### Criterios de aceptación

- El comando `/cancelar` interrumpe el flujo activo.
- El bot confirma que la operación fue cancelada.
- La cancelación no crea un pedido confirmado.
- El cliente dispone de un mecanismo para iniciar nuevamente.
- El reinicio limpia el estado temporal que corresponda.
- Cancelar cuando no existe un flujo activo produce una respuesta comprensible.
- Las reglas para cancelar un pedido ya confirmado se documentarán cuando se
  defina la máquina de estados; esta historia no anticipa esa transición.

### HU-C09 — Manejo de entradas inesperadas y duplicadas

**Como cliente,
quiero recibir respuestas claras ante acciones inválidas o repetidas,
para continuar el pedido sin errores ni duplicaciones.**

#### Criterios de aceptación

- Un mensaje fuera de contexto recibe una respuesta útil.
- Una entrada inválida no provoca la caída del bot.
- El bot conserva el contexto válido después de un error.
- La doble pulsación de un botón no agrega dos veces el mismo efecto.
- Una actualización de Telegram ya procesada no vuelve a ejecutarse.
- Repetir la confirmación no crea pedidos duplicados.
- El cliente recibe una respuesta coherente para continuar, cancelar o
  reiniciar.
