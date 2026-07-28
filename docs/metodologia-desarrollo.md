# Metodología de desarrollo

## Enfoque seleccionado

El MVP de pedidos de Restaurant Las Retamas utilizará Extreme Programming (XP)
adaptada al desarrollo individual. Esta metodología se adopta como una decisión
del proyecto para organizar el trabajo en incrementos pequeños, verificables y
comprensibles, manteniendo la correspondencia entre la documentación y el
sistema que llegue a implementarse.

La adaptación no modifica las condiciones del documento base ni el flujo
obligatorio del repositorio. XP orienta la forma de planificar, revisar y mejorar
cada incremento; Git y GitHub conservan la evidencia de cómo se realizó.

## Adaptación al trabajo individual

El examen exige autoría individual. Por esta razón, no se aplica programación en
pareja. Las tareas de análisis, implementación, prueba y revisión corresponden a
la autora del proyecto.

La revisión que normalmente podría realizar otra persona se reemplaza por una
auto-revisión formal en cada Pull Request. Esta revisión exige leer el diff
completo, comprobar los criterios de aceptación, registrar las verificaciones y
confirmar que la autora puede explicar y modificar el cambio.

La adaptación mantiene las prácticas de XP que resultan aplicables:

- historias de usuario;
- pequeñas entregas;
- desarrollo incremental;
- diseño simple;
- pruebas frecuentes;
- integración frecuente;
- refactorización.

## Historias de usuario

Las historias expresan una necesidad desde la perspectiva de cliente,
repartidor o administrador y se acompañan de criterios de aceptación
verificables. `docs/requisitos.md` reúne estas historias y constituye una
referencia para dividir el desarrollo funcional.

Una historia no equivale automáticamente a un único Issue. Antes de implementar,
su alcance puede dividirse en varios Issues pequeños si requiere persistencia,
interfaz, integración y pruebas diferenciadas. Cada Issue debe conservar una
relación clara con la historia que contribuye a resolver.

## Pequeñas entregas y desarrollo incremental

El proyecto avanza mediante cambios acotados. Cada Issue define una unidad de
trabajo con contexto, alcance, criterios de aceptación, archivos previstos,
milestone, labels y rama asociada. El Pull Request resultante debe contener solo
lo necesario para resolver ese Issue y mantenerse dentro del tamaño establecido
en `CONTRIBUTING.md`.

El desarrollo incremental permite verificar una parte antes de continuar con la
siguiente. En la fase documental ya se aplicó este criterio al separar el
contexto, el registro de IA y las historias de cada rol en Issues y Pull
Requests distintos.

Para el desarrollo funcional se mantendrá el mismo principio: primero se
definirán las bases necesarias y después se incorporarán capacidades pequeñas
del bot y del panel, sin implementar bloques extensos en un solo cambio.

## Diseño simple

El diseño buscará la solución más sencilla que satisfaga los criterios vigentes
sin anticipar funciones no solicitadas. Las decisiones de arquitectura, modelo
de datos y organización del código deberán justificarse cuando exista
información suficiente y reflejar lo implementado realmente.

Diseño simple no significa omitir requisitos obligatorios. El bot, el panel, la
base de datos compartida y el modelo común de estados deben conservarse como
partes integradas del MVP.

## Pruebas frecuentes

Cada Issue debe definir las verificaciones aplicables antes de comenzar el
trabajo. En los incrementos documentales se utilizan revisiones de contenido,
contraste con el documento base y validaciones como `git diff --check`.

Cuando exista implementación funcional, las pruebas se incorporarán de acuerdo
con el riesgo del cambio. Podrán incluir pruebas automatizadas, validaciones de
la API, comprobaciones de persistencia y recorridos manuales del bot y el panel.
No se considera finalizado un incremento hasta ejecutar y registrar sus
verificaciones.

Este documento describe la práctica prevista; no afirma que ya existan pruebas
automatizadas o módulos funcionales.

## Integración frecuente

Los cambios terminados se integran regularmente en `develop` mediante Pull
Requests pequeños. Esto permite detectar incompatibilidades cerca del momento
en que se introduce cada cambio y mantener una rama de integración actualizada.

`main` permanece como rama estable. El paso de cambios desde `develop` hacia
`main` también requiere un Pull Request y solo debe realizarse cuando el
conjunto que se desea publicar haya sido verificado.

## Refactorización

La refactorización permitirá mejorar la estructura interna sin alterar el
comportamiento esperado. No se realizará como cambio oculto dentro de un Issue
ajeno: debe estar comprendida por el alcance, conservar las pruebas aplicables y
utilizar el prefijo de commit definido para este tipo de trabajo.

Antes y después de refactorizar se comprobará que los criterios de aceptación
continúen cumpliéndose. Si la mejora excede el alcance activo, se planificará en
un Issue independiente.

## Relación entre XP y el flujo Git/GitHub

El flujo operativo de cada incremento es:

```text
Issue
→ rama asociada
→ trabajo
→ pruebas
→ commit
→ push
→ Pull Request
→ auto-revisión
→ squash merge
→ cierre automático del Issue
→ eliminación de la rama
```

La relación con XP se aplica de la siguiente manera:

1. El Issue planifica una entrega pequeña a partir de una historia o necesidad
   verificable.
2. La rama aísla el incremento y evita trabajar directamente en `main` o
   `develop`.
3. El trabajo implementa solamente el alcance aprobado y conserva un diseño
   simple.
4. Las pruebas proporcionan retroalimentación antes de integrar.
5. El Pull Request permite la auto-revisión individual.
6. El squash merge integra un resultado limpio en `develop`.
7. El cierre automático y la eliminación de la rama completan la trazabilidad.

Los Issues no se crean de manera retroactiva ni se cierran manualmente. El orden
de integración debe representar el avance real del proyecto.

## Entorno objetivo de despliegue

El proyecto prevé desplegar el MVP en un servidor VPS de Hetzner. Esta selección
es una decisión del proyecto y no implica que el sistema ya esté desplegado.

El VPS se considera el entorno objetivo para integrar posteriormente el backend,
el bot, el panel web y la base de datos conforme a las decisiones técnicas que
se adopten. Las pequeñas entregas deberán mantener instrucciones reproducibles y
evitar depender de configuraciones manuales no documentadas.

La preparación, seguridad, variables de entorno, servicios, dominio, HTTPS,
copias de respaldo y procedimiento de publicación se definirán cuando se
desarrolle `docs/despliegue.md`. La justificación de Hetzner y las alternativas
evaluadas se registrarán en `docs/decisiones-tecnicas.md`.

## Aplicación actual y prácticas previstas

Hasta el Issue #13 se han aplicado historias de usuario, Issues acotados, ramas
de documentación, verificaciones de formato, Pull Requests, auto-revisión,
squash merge y eliminación de ramas.

Las prácticas relacionadas con código, pruebas funcionales, refactorización y
despliegue en el VPS permanecen previstas. Se documentarán como realizadas
únicamente después de que existan evidencias en el repositorio y en los Pull
Requests correspondientes.
