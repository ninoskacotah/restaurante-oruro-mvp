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

## Historias de usuario del repartidor

### HU-R01 — Autenticación del repartidor

**Como repartidor, quiero autenticarme en el bot de Telegram, para acceder
únicamente a las funciones correspondientes a mi rol.**

#### Criterios de aceptación

- El bot distingue al repartidor del cliente.
- El repartidor debe autenticarse antes de consultar asignaciones.
- La autenticación utiliza un mecanismo permitido: código, registro previo
  desde el panel o lista blanca.
- Un usuario no autorizado no puede acceder a pedidos ni datos de clientes.
- Los comandos disponibles se presentan según el rol autenticado.
- Una autenticación inválida recibe una respuesta comprensible y no inicia una
  sesión de repartidor.
- La identidad autenticada queda vinculada al repartidor registrado.

### HU-R02 — Recepción de un pedido asignado

**Como repartidor, quiero recibir la información completa de un pedido que me
fue asignado, para preparar y realizar la entrega correctamente.**

#### Criterios de aceptación

- La asignación la realiza el administrador desde el panel.
- No existe una cola ni competencia entre repartidores.
- Solo el repartidor seleccionado recibe la asignación.
- La notificación incluye el número del pedido.
- Muestra los platos y cantidades.
- Muestra el importe total y el estado del pago.
- Muestra la dirección y referencia de entrega.
- Incluye el destino como objeto `Location` de Telegram.
- Muestra el nombre y contacto del cliente.
- La información coincide con el pedido registrado en la base de datos.

### HU-R03 — Acuse de recibo de la asignación

**Como repartidor, quiero confirmar que recibí una asignación, para informar al
administrador que conozco el pedido que debo entregar.**

#### Criterios de aceptación

- La notificación incluye un botón de acuse de recibo.
- Solo el repartidor asignado puede confirmar la recepción.
- El acuse queda asociado al pedido y al repartidor.
- Se registra la fecha y hora de la confirmación.
- El resultado se refleja en el panel administrativo.
- Pulsar repetidamente el botón no genera varios acuses.
- Un repartidor no puede acusar recibo de un pedido que ya no le pertenece.

### HU-R04 — Reasignación consistente del pedido

**Como repartidor, quiero que mis pedidos asignados se actualicen cuando exista
una reasignación, para trabajar únicamente con las entregas que continúan bajo
mi responsabilidad.**

#### Criterios de aceptación

- La reasignación se realiza desde el panel administrativo.
- El repartidor anterior deja de ver el pedido como una asignación activa.
- El nuevo repartidor recibe toda la información del pedido.
- El repartidor anterior no puede registrar nuevos eventos sobre el pedido
  reasignado.
- El nuevo repartidor debe realizar su propio acuse de recibo.
- El historial conserva quién estuvo asignado y cuándo ocurrió la reasignación.
- Las ubicaciones de ambos repartidores no se mezclan en un mismo rastro.
- La reasignación no duplica el pedido.

### HU-R05 — Seguimiento mediante ubicación en tiempo real

**Como repartidor, quiero compartir mi ubicación en tiempo real durante el
trayecto, para que el administrador pueda seguir el avance de la entrega.**

#### Criterios de aceptación

- El seguimiento utiliza `live location` de Telegram.
- Una ubicación estática aislada no se considera seguimiento en tiempo real.
- Solo se aceptan actualizaciones del repartidor actualmente asignado.
- Cada actualización almacena latitud, longitud y marca temporal.
- Las ubicaciones quedan vinculadas al pedido y al repartidor correcto.
- El panel muestra la posición del repartidor y el destino.
- El rastro conserva el orden cronológico de las actualizaciones.
- El intervalo de actualización deberá quedar definido antes de implementar el
  seguimiento.
- Finalizada la entrega, las nuevas ubicaciones no se agregan al trayecto
  cerrado.

### HU-R06 — Manejo de pérdida de señal

**Como repartidor, quiero que el sistema gestione una interrupción de mi
ubicación en tiempo real, para continuar la entrega sin perder el rastro ya
registrado.**

#### Criterios de aceptación

- Las ubicaciones recibidas antes de la interrupción permanecen almacenadas.
- La falta de nuevas actualizaciones no elimina ni sustituye el último punto
  válido.
- El panel permite reconocer que la ubicación dejó de actualizarse.
- Se conserva la fecha y hora de la última ubicación recibida.
- Cuando se recupera la señal, las nuevas actualizaciones continúan asociadas al
  mismo pedido y repartidor.
- La recuperación no duplica puntos ya procesados.
- Una pérdida de señal no marca automáticamente la llegada o la entrega.

### HU-R07 — Registro de llegada al destino

**Como repartidor, quiero registrar mi llegada al destino, para informar que me
encuentro en el lugar de entrega.**

#### Criterios de aceptación

- Solo el repartidor actualmente asignado puede registrar la llegada.
- La llegada se registra como un evento diferente de la entrega.
- El evento conserva fecha y hora.
- El estado se refleja en el panel administrativo.
- El cliente recibe una notificación diferenciada de llegada.
- Registrar la llegada varias veces no crea eventos duplicados.
- No se puede registrar una llegada sobre un pedido reasignado a otro
  repartidor.

### HU-R08 — Confirmación de entrega con evidencia

**Como repartidor, quiero confirmar la entrega e incorporar una evidencia, para
dejar constancia de que el pedido fue recibido por el cliente.**

#### Criterios de aceptación

- Solo el repartidor actualmente asignado puede confirmar la entrega.
- La entrega se registra después de la llegada.
- La confirmación exige una evidencia admitida: fotografía o código
  proporcionado por el cliente.
- La evidencia queda asociada al pedido.
- Se registra la fecha y hora de entrega.
- El panel refleja la entrega y permite consultar la evidencia.
- El cliente recibe una notificación diferenciada de pedido entregado.
- Repetir la confirmación no duplica el evento ni la evidencia.
- Un pedido entregado deja de aparecer como asignación activa.

Las notificaciones al cliente se producen en momentos diferentes: cuando el
pedido inicia el trayecto, cuando el repartidor registra su llegada y cuando
confirma la entrega.
