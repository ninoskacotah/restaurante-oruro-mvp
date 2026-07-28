# Registro de uso de asistentes de IA

Herramientas utilizadas: Codex de OpenAI.

## Objetivo

Este documento registra de forma transparente la asistencia de Inteligencia
Artificial utilizada durante el desarrollo académico del MVP de Restaurant Las
Retamas. Cada entrada diferencia el apoyo recibido de la revisión, las
decisiones y las autorizaciones realizadas por la autora.

## Registro

| Fecha | Issue / PR | Para qué se usó | Qué devolvió | Cómo se verificó | Qué se modificó |
|---|---|---|---|---|---|
| 2026-07-28 | Issue #1 / PR #2 | Apoyar la redacción y revisión del flujo de contribución exigido para el proyecto. | Una propuesta de guía de contribución y plantilla de Pull Request, además de la identificación de ambigüedades frente al enunciado. | La autora revisó el contenido completo, solicitó correcciones puntuales y comprobó los cambios con `git diff --check` y `git status`. | Se crearon `CONTRIBUTING.md` y `.github/pull_request_template.md`; las correcciones autorizadas incorporaron la estructura de Issues, el push explícito y controles adicionales de auto-revisión. |
| 2026-07-28 | Issue #3 / PR #4 | Apoyar la redacción y ajuste del contexto académico del MVP para Restaurant Las Retamas. | Borradores del contexto, problema, justificación, objetivos, alcance, limitaciones y sección de tecnologías. | La autora leyó el documento completo, proporcionó el texto definitivo, autorizó ajustes específicos y verificó el formato antes del commit. | Se creó `docs/contexto-proyecto.md` con el contenido aprobado por la autora. |
| 2026-07-28 | Issue #5 / PR #6 | Analizar cómo mantener un registro vivo de IA sin incumplir el flujo obligatorio de Issues y preparar su estructura inicial. | Una propuesta para cerrar el Issue de creación mediante PR y actualizar el registro dentro de cada Issue posterior que utilice IA. | Se contrastó la propuesta con el documento base, el Issue #5, el historial real de Issues y Pull Requests y las reglas de `CONTRIBUTING.md`. | Se creó la estructura inicial de `docs/uso-ia.md` y se registró el uso real de IA efectuado hasta la fecha. |
| 2026-07-28 | Issue #7 / PR #8 | Apoyar la definición de las historias de usuario correspondientes al flujo del cliente. | Una propuesta de nueve historias con criterios de aceptación para identificación, menú, carrito, ubicación, pago, seguimiento, cancelación y manejo de duplicados. | La autora revisó y aprobó las historias antes de incorporarlas; luego se contrastaron con el Bloque C y los criterios del Issue #7. | Se creó `docs/requisitos.md` con las historias del cliente y se actualizó este registro. |
| 2026-07-28 | Issue #9 / PR #10 | Apoyar la definición de las historias de usuario correspondientes al flujo del repartidor. | Una propuesta de ocho historias con criterios de aceptación para autenticación, asignación, acuse, reasignación, seguimiento, pérdida de señal, llegada y entrega. | La autora revisó y aprobó las historias antes de incorporarlas; luego se contrastaron con el Bloque D y los criterios del Issue #9. | Se amplió `docs/requisitos.md` con las historias del repartidor y se actualizó este registro. |
| 2026-07-28 | Issue #11 / PR pendiente | Apoyar la definición de las historias de usuario correspondientes al panel administrativo. | Una propuesta de nueve historias con criterios de aceptación para autenticación, platos, menú, stock, pedidos, pagos, asignaciones, mapa, clientes y reportes. | La autora revisó y aprobó las historias antes de incorporarlas; luego se contrastaron con el Bloque E y los criterios del Issue #11. | Se amplió `docs/requisitos.md` con las historias del administrador y se actualizó este registro. |

## Actualización del registro

Cuando se utilice IA en un Issue posterior, su propio Pull Request deberá incluir
la actualización de este archivo. La entrada se referirá al Issue y al PR
correspondientes y describirá únicamente actividades reales y verificables.

No se crearán fechas, resultados o verificaciones ficticias. Si un Issue no
utiliza IA, no se añadirá una entrada que indique lo contrario.

## Dónde NO se usó IA

A la fecha de creación de este registro no existen módulos funcionales del bot,
del panel o de la base de datos sobre los cuales declarar desarrollo sin IA.

La revisión final del contenido, las decisiones sobre su incorporación y la
autorización de cada etapa del flujo Git/GitHub fueron realizadas por la autora.

## Declaración

Comprendo todo el código y la documentación de este repositorio y puedo
explicarlos, justificarlos y modificarlos sin asistencia.
