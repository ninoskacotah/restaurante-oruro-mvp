# Guía de contribución

Este documento establece el flujo de trabajo individual para construir el MVP de
pedidos de Restaurant Las Retamas. Su propósito es que cada cambio pueda
rastrearse desde su planificación hasta su integración.

## Modelo de ramas

El proyecto aplica el esquema denominado por el docente **Forking Workflow**.
En este repositorio el nombre describe la separación del trabajo mediante ramas;
no implica crear un fork de un repositorio externo.

- `main` es la rama estable. Solo recibe cambios integrados y listos para una
  versión estable mediante Pull Request.
- `develop` es la rama de integración. Recibe los cambios terminados de las
  ramas de trabajo mediante Pull Request.
- `feature/` se utiliza para incorporar una funcionalidad.
- `fix/` se utiliza para corregir un defecto.
- `docs/` se utiliza para crear o actualizar documentación.

Toda rama de trabajo se crea desde `develop` y sigue el patrón:

```text
tipo/NN-descripcion-corta
```

`NN` es el número del Issue y la descripción usa palabras breves separadas por
guiones. Por ejemplo: `feature/12-carrito-pedidos`.

Está prohibido desarrollar o realizar push directamente sobre `main` o
`develop`. Tampoco se crean ramas al final de un trabajo para reconstruir una
trazabilidad que no existió durante su desarrollo.

## Estructura obligatoria de los Issues

Cada Issue representa una unidad de planificación real del proyecto y debe
incluir:

- un título accionable, redactado como verbo más objeto;
- una descripción que explique el contexto y delimite el alcance;
- criterios de aceptación verificables sobre el resultado;
- un label de tipo (`feat`, `bug` o `docs`) y un label de parte (`parte:bot` o
  `parte:panel`);
- el milestone correspondiente al avance;
- la rama asociada con el patrón `tipo/NN-descripcion-corta`;
- un Pull Request vinculado mediante `Closes #NN`.

El Issue permanece abierto durante el trabajo y su cierre debe producirse
automáticamente al integrar el Pull Request relacionado. No se permite cerrarlo
manualmente, ni crear o cerrar grupos de Issues al final para reconstruir un
avance que no ocurrió. El orden de cierre debe mostrar la evolución real y
gradual del MVP de Restaurant Las Retamas.

## Flujo obligatorio de un cambio

Cada incremento se trabaja de forma gradual y en este orden:

1. Crear un Issue antes de implementar y definir allí el alcance y los criterios
   de aceptación.
2. Crear desde `develop` la rama asociada al Issue.
3. Realizar únicamente el trabajo comprendido en ese Issue.
4. Ejecutar las pruebas o verificaciones aplicables.
5. Registrar commits comprensibles y relacionados con el cambio.
6. Realizar push de la rama de trabajo al repositorio remoto.
7. Abrir un Pull Request hacia `develop`, vinculado al Issue.
8. Completar la auto-revisión y corregir los problemas encontrados.
9. Integrar mediante **squash merge**.
10. Permitir que el merge cierre automáticamente el Issue.
11. Eliminar la rama de trabajo después de la integración.

El paso de una versión integrada desde `develop` hacia `main` también se realiza
mediante Pull Request. No se permite el push directo entre estas ramas.

## Convención de commits

El mensaje debe describir una unidad de trabajo concreta y comenzar con uno de
estos prefijos:

- `feat:` para una funcionalidad.
- `fix:` para una corrección.
- `docs:` para documentación.
- `refactor:` para una mejora interna que no cambia el comportamiento esperado.
- `test:` para pruebas.

Ejemplo:

```text
docs: definir flujo de contribución
```

Los commits deben reflejar avance real. No se agrupan cambios ajenos al Issue ni
se fabrican commits o ramas de manera retroactiva.

## Pull Requests

Cada Pull Request debe ser pequeño, coherente y revisable. Como referencia, no
debe superar aproximadamente quince archivos y debe contener solo cambios del
Issue asociado.

El cuerpo se completa usando la plantilla del repositorio e incluye:

- el propósito del cambio;
- el Issue relacionado;
- los cambios realizados;
- las pruebas o verificaciones ejecutadas;
- la documentación afectada;
- evidencia visual cuando corresponda;
- la referencia de cierre `Closes #NN`.

`NN` debe reemplazarse por el número real. El Issue no se cierra manualmente: se
cierra como resultado de integrar el Pull Request que contiene esa referencia.

## Auto-revisión individual

Como el proyecto es individual, la autora revisa su propio Pull Request antes
del merge. La auto-revisión debe confirmar, al menos, que:

- el cambio satisface los criterios de aceptación del Issue;
- no se incluyeron archivos o funcionalidades fuera del alcance;
- las pruebas y verificaciones indicadas fueron ejecutadas;
- la documentación coincide con el comportamiento implementado;
- no se incorporaron credenciales ni datos sensibles;
- el Pull Request puede explicarse y defenderse en su totalidad;
- la referencia `Closes #NN` apunta al Issue correcto.

Después de completar la revisión, se utiliza exclusivamente **squash merge** con
un mensaje limpio y se elimina la rama integrada.
