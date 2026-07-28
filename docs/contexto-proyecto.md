# Contexto y definición del proyecto

## Introducción

El presente proyecto académico plantea el desarrollo de un producto mínimo viable para la gestión de pedidos de Restaurant Las Retamas, establecimiento gastronómico de la ciudad de Oruro. La solución estará compuesta por un bot de Telegram y un panel web de administración que funcionarán de manera integrada sobre una única base de datos y un único modelo de estados del pedido.

El sistema utilizará como catálogo inicial los platos identificados públicamente como parte de la oferta gastronómica de Restaurant Las Retamas. Entre ellos se consideran pique macho, trucha al limón, trucha a la plancha, paiche, colita de cordero, costillar de cordero, pollo al grill, filet mignon, cazuelas, escabeche, huminta y tostadita de cordero. Estos platos deberán registrarse en la base de datos y administrarse desde el panel web, donde podrán definirse sus precios, disponibilidad, stock y programación dentro del menú por fecha.

El proyecto comprende no solo la implementación funcional del sistema, sino también su documentación, trazabilidad mediante GitHub y la capacidad de explicar y modificar cada componente durante la defensa.

## Contexto del proyecto

Restaurant Las Retamas constituye el caso de estudio real sobre el cual se implementará el MVP. Su oferta gastronómica incluye platos nacionales, preparaciones con carne de cordero, pescados, carnes, aves y otras especialidades.

El sistema deberá permitir que esta oferta sea representada mediante un catálogo digital administrable. Los platos no estarán escritos directamente en el código del bot. Serán almacenados en la base de datos y configurados desde el panel de administración, de manera que el personal autorizado pueda crear, consultar, editar y eliminar platos, asignar precios, controlar el stock y definir cuáles estarán disponibles en una fecha determinada.

El bot de Telegram constituirá el canal de interacción para clientes y repartidores. El cliente podrá consultar el menú vigente de Restaurant Las Retamas, seleccionar uno o varios platos, indicar cantidades, revisar su carrito, proporcionar la ubicación de entrega, recibir el código QR de pago, remitir el comprobante y realizar el seguimiento del pedido.

El repartidor recibirá los pedidos que le sean asignados desde el panel, visualizará el detalle de platos y cantidades, compartirá su ubicación en tiempo real y registrará los eventos de llegada y entrega.

El administrador contará con un panel web protegido para gestionar los platos de Restaurant Las Retamas, programar el menú por fecha, controlar la disponibilidad, revisar pedidos, verificar comprobantes, confirmar pagos, asignar repartidores y consultar información operativa.

No se dispone de información interna comprobada sobre volúmenes de pedidos, tiempos reales de atención, estructura organizacional, dificultades administrativas, ingresos o pérdidas económicas del restaurante. Por esa razón, esos aspectos no se presentan como hechos ni se utilizan para justificar el proyecto.

## Planteamiento del problema

El proyecto requiere implementar un mecanismo integrado que permita administrar digitalmente el ciclo completo de los pedidos de Restaurant Las Retamas, desde la consulta del menú hasta la entrega al cliente.

La solución debe coordinar tres roles principales. El cliente necesita conocer los platos disponibles, seleccionar productos y cantidades, enviar su ubicación, realizar el pago y consultar el avance de su pedido. El repartidor necesita recibir la asignación, conocer el detalle del pedido y la ubicación del cliente, compartir su recorrido y confirmar la llegada y la entrega. El administrador necesita mantener actualizada la oferta gastronómica, controlar el stock, revisar los pedidos, confirmar los pagos y asignar al repartidor correspondiente.

El problema técnico consiste en mantener sincronizadas estas operaciones entre el bot de Telegram y el panel web. Si ambos componentes utilizaran información independiente, podrían producirse diferencias en los platos disponibles, el stock, el pago, la asignación o el estado del pedido.

Por ello, el MVP debe utilizar una única base de datos y un único modelo de estados, garantizando que las acciones realizadas desde Telegram se reflejen en el panel y que las decisiones administrativas produzcan el efecto correspondiente en el bot.

Este planteamiento no afirma que Restaurant Las Retamas presente actualmente deficiencias internas específicas, debido a que no se cuenta con evidencia institucional que permita realizar dicho diagnóstico.

## Justificación

La implementación del MVP permitirá representar digitalmente la oferta gastronómica real de Restaurant Las Retamas y verificar el funcionamiento completo de un pedido mediante Telegram y un panel web integrado.

La utilización de los platos del restaurante como catálogo inicial proporciona coherencia al caso de estudio y evita trabajar con productos genéricos que no correspondan al establecimiento seleccionado. Al mismo tiempo, el panel permitirá modificar esa información cuando cambien los precios, el stock, la disponibilidad o la programación del menú.

Desde el punto de vista técnico, una base de datos compartida permitirá mantener consistencia entre el catálogo, el carrito, los pedidos, los pagos, las asignaciones y el seguimiento de las entregas. El modelo de estados permitirá conservar la trazabilidad desde la creación del pedido hasta su entrega.

Desde el punto de vista operativo del MVP, la separación de funciones entre cliente, repartidor y administrador permitirá verificar cada etapa mediante acciones concretas y observables.

La justificación se limita al valor académico y funcional de la solución. No se atribuyen beneficios económicos, incrementos de productividad ni mejoras estadísticas al restaurante porque no existen datos internos comprobados que permitan demostrar esos resultados.

## Objetivo general

Desarrollar un MVP integrado para Restaurant Las Retamas que gestione el catálogo real de platos y el ciclo completo de pedidos mediante un bot de Telegram y un panel web de administración, utilizando una única base de datos y un único modelo de estados.

## Objetivos específicos

1. Registrar en la base de datos el catálogo inicial de platos de Restaurant Las Retamas, incluyendo pique macho, trucha al limón, trucha a la plancha, paiche, colita de cordero, costillar de cordero, pollo al grill, filet mignon, cazuelas, escabeche, huminta y tostadita de cordero.

2. Permitir que el administrador cree, consulte, modifique y elimine platos, además de configurar sus precios, disponibilidad, stock y programación por fecha.

3. Permitir que el cliente consulte mediante Telegram únicamente los platos habilitados para la fecha actual y con disponibilidad mayor a cero.

4. Permitir que el cliente seleccione varios platos, indique cantidades, consulte el detalle del carrito, modifique cantidades, elimine productos y obtenga el total calculado correctamente.

5. Registrar la ubicación de entrega, enviar el código QR de pago, almacenar el comprobante remitido por el cliente y mantener la verificación manual del pago desde el panel.

6. Permitir que el administrador controle los pedidos, confirme los pagos y asigne uno de los repartidores registrados.

7. Permitir que el repartidor reciba el detalle completo del pedido asignado, comparta su ubicación en tiempo real y registre por separado la llegada y la entrega.

8. Mantener sincronizados el bot y el panel mediante la persistencia compartida de los platos, clientes, pedidos, pagos, estados, repartidores y ubicaciones.

9. Conservar la trazabilidad necesaria para consultar el historial de pedidos de cada cliente y generar los reportes básicos exigidos para el MVP.

10. Documentar el sistema de manera consistente con su implementación, de modo que pueda instalarse, probarse, desplegarse y explicarse durante la defensa.

## Alcance inicial del MVP

El alcance comprende dos componentes obligatorios e integrados.

### Bot de Telegram

El bot atenderá al cliente durante las siguientes operaciones:

- identificación mediante su chat_id;
- consulta del menú vigente;
- visualización de platos habilitados con sus precios;
- selección de varios platos;
- definición y modificación de cantidades;
- eliminación de productos del carrito;
- cálculo del total;
- envío de la ubicación de entrega;
- recepción del código QR de pago;
- envío del comprobante;
- recepción del código de seguimiento;
- consulta y notificación del estado del pedido;
- cancelación o reinicio controlado del flujo.

El menú deberá provenir de la base de datos y utilizar como catálogo inicial los platos identificados de Restaurant Las Retamas. Un cambio realizado desde el panel deberá reflejarse en el bot.

El bot también atenderá al repartidor autenticado para:

- recibir el pedido asignado;
- visualizar el detalle de platos, cantidades, importe y estado del pago;
- visualizar los datos y la ubicación del cliente;
- confirmar la recepción de la asignación;
- compartir su ubicación en tiempo real;
- registrar la llegada;
- registrar la entrega y su evidencia.

### Panel web de administración

El panel permitirá:

- autenticar al administrador;
- crear, consultar, editar y eliminar platos;
- administrar los platos iniciales de Restaurant Las Retamas;
- definir precios;
- programar el menú por fecha;
- controlar disponibilidad y stock;
- revisar el tablero de pedidos;
- visualizar comprobantes;
- confirmar manualmente los pagos;
- asignar y reasignar repartidores;
- visualizar la ubicación del repartidor y el destino;
- verificar la llegada y la entrega;
- consultar la ficha y el historial de cada cliente;
- generar reportes de ventas del día, platos más pedidos y tiempo promedio de entrega.

El sistema utilizará una sola base de datos y un único modelo de estados. La información deberá persistir ante reinicios y los cambios relevantes deberán reflejarse entre el bot y el panel.

El alcance también comprende la documentación necesaria para instalar, utilizar, probar, desplegar y explicar el sistema.

Este documento define las funciones previstas para el MVP y no afirma que ya se encuentren implementadas.

## Tecnologías seleccionadas para el desarrollo del MVP

### Python 3.12

Python 3.12 será el lenguaje principal para el desarrollo del backend y del bot de Telegram. Se selecciona por su estabilidad, legibilidad y amplio ecosistema para el desarrollo de aplicaciones web, APIs y automatización.

### Aiogram

Aiogram será el framework utilizado para desarrollar el bot de Telegram. Permitirá implementar los flujos conversacionales del cliente y del repartidor, administrar comandos, botones interactivos, recepción de ubicaciones, comprobantes de pago y notificaciones del estado de los pedidos mediante programación asíncrona.

### FastAPI

FastAPI será el framework encargado de desarrollar la API REST del sistema. Centralizará la lógica del negocio y permitirá la comunicación entre el bot de Telegram, el panel web y la base de datos.

### PostgreSQL

PostgreSQL será el sistema gestor de base de datos relacional donde se almacenará toda la información del sistema, incluyendo platos, menús, clientes, pedidos, pagos, repartidores, ubicaciones y estados del pedido.

### SQLAlchemy

SQLAlchemy será el ORM encargado de gestionar la comunicación entre FastAPI y PostgreSQL, permitiendo representar las tablas mediante modelos orientados a objetos y simplificando las operaciones de persistencia de datos.

### Vue 3

Vue 3 será el framework JavaScript utilizado para desarrollar el panel web administrativo mediante una arquitectura basada en componentes reutilizables e interfaces reactivas.

### Vite

Vite será la herramienta de desarrollo y compilación del frontend. Permitirá acelerar el desarrollo del panel web y generar la versión optimizada para su ejecución.

### JavaScript

JavaScript será el lenguaje utilizado para desarrollar la lógica del panel web, implementar la interacción con la API REST y proporcionar dinamismo a la interfaz de usuario.

### JSON Web Token (JWT)

JWT será el mecanismo de autenticación utilizado para proteger el acceso al panel administrativo mediante tokens firmados, garantizando que únicamente los usuarios autorizados accedan a las funciones administrativas.

### Git

Git será el sistema de control de versiones utilizado durante el desarrollo del proyecto para administrar el historial de cambios, las ramas de trabajo y la evolución del software.

### GitHub

GitHub será la plataforma donde se alojará el repositorio del proyecto y se gestionarán los Issues, ramas, Pull Requests y Projects conforme al flujo de trabajo definido para el desarrollo del MVP.

## Limitaciones del MVP

- El sistema corresponde a un proyecto académico y no constituye todavía una solución validada mediante una implementación real dentro de Restaurant Las Retamas.
- No se dispone de información interna comprobada sobre procedimientos, volumen de pedidos, tiempos de atención, ingresos, pérdidas o necesidades institucionales específicas.
- El catálogo inicial se basa en platos públicamente asociados al restaurante, pero los precios, stock y fechas de disponibilidad deberán definirse como datos configurables desde el panel y no deben inventarse en la documentación.
- Telegram es el canal conversacional obligatorio; el alcance inicial no incluye WhatsApp, Messenger u otros canales.
- La operación contempla uno o dos repartidores.
- No existe una cola ni competencia entre repartidores; la asignación la realiza el administrador.
- La comprobación del pago es manual y el estado pagado debe ser confirmado por una persona desde el panel.
- El proyecto se limita a las funciones exigidas para el bot, el reparto y el panel de administración.
