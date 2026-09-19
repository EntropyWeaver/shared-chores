# Shared Chores — Backlog del MVP

Fuente de verdad: [`_docs/plan.md`](_docs/plan.md)  
Estado: listo para implementación incremental

## Reglas de trabajo

- Las tareas se implementan en el orden indicado salvo que se documente otra decisión.
- Cada tarea debe caber en una sesión de trabajo y terminar en un commit coherente.
- Antes de programar, se revisan sus criterios de aceptación y sus límites.
- Cada comportamiento nuevo debe incluir tests automatizados.
- Una tarea no está terminada hasta que sus tests y la suite completa pasan.
- La implementación no puede ampliar silenciosamente el alcance del MVP.

## Task 1 — Crear una página inicial con un test funcional

**Status:** completada.

**Goal:** demostrar que Django, la aplicación `chores`, el enrutamiento, una vista y una plantilla funcionan juntos de extremo a extremo.

**Description:** crear una página mínima de Shared Chores en `/` y cubrirla con un test. Este será el primer comportamiento observable de la aplicación y sustituirá el estado actual de cero tests por una línea base verificable.

**Acceptance criteria:**

- [x] Una petición `GET /` devuelve HTTP 200.
- [x] La respuesta contiene el nombre `Shared Chores`.
- [x] La vista pertenece a la aplicación `chores` y utiliza una plantilla HTML.
- [x] `uv run python manage.py test` descubre al menos un test y la suite completa pasa.

**Out of scope:** autenticación, modelos de dominio, formularios y diseño visual definitivo.

**Dependencies:** bootstrap de Django completado.

## Task 2 — Añadir registro y autenticación de usuarios

**Goal:** permitir que cada compañero de piso utilice una identidad propia y una sesión autenticada.

**Description:** implementar registro, inicio de sesión y cierre de sesión utilizando el sistema de autenticación incluido en Django.

**Acceptance criteria:**

- [x] Un visitante puede crear una cuenta con nombre de usuario y contraseña válidos.
- [x] No se permiten nombres de usuario duplicados.
- [x] Un usuario registrado puede iniciar y cerrar sesión.
- [x] Las rutas privadas redirigen a inicio de sesión cuando el visitante es anónimo.
- [x] Los flujos principales de autenticación están cubiertos por tests.

**Out of scope:** correo electrónico obligatorio, recuperación de contraseña, OAuth y autenticación multifactor.

**Dependencies:** Task 1.

## Task 3 — Modelar hogares y pertenencia

**Goal:** representar un hogar compartido y la pertenencia de cada usuario a un único hogar.

**Description:** crear los modelos necesarios para almacenar hogares, códigos de acceso y miembros. Las reglas de capacidad y pertenencia deben residir en una capa reutilizable, no únicamente en la interfaz.

**Acceptance criteria:**

- [x] Un hogar tiene nombre y un código de acceso único.
- [x] Un usuario puede pertenecer como máximo a un hogar.
- [x] Un hogar admite como máximo 6 miembros.
- [x] Las restricciones de pertenencia y capacidad están cubiertas por tests.
- [x] Se crea y aplica una migración válida.

**Out of scope:** roles administrativos, varios hogares por usuario y expulsión de miembros.

**Dependencies:** Task 2.

## Task 4 — Crear un hogar o unirse mediante código

**Goal:** permitir que usuarios autenticados formen el grupo de convivencia que compartirá las tareas.

**Description:** ofrecer dos acciones a quien todavía no pertenece a un hogar: crear uno o introducir el código de uno existente.

**Acceptance criteria:**

- [x] Un usuario sin hogar puede crear uno y se convierte en su primer miembro.
- [x] El hogar creado muestra un código que puede compartirse.
- [x] Un usuario sin hogar puede unirse mediante un código válido.
- [x] Un código inexistente o un hogar completo producen un error visible y no alteran datos.
- [x] Un usuario que ya pertenece a un hogar no puede crear otro ni unirse a otro.

**Out of scope:** invitaciones por correo, enlaces temporales y regeneración del código.

**Dependencies:** Task 3.

## Task 5 — Crear y asignar tareas domésticas

**Goal:** permitir que cualquier miembro cree una tarea y la asigne manualmente dentro de su hogar.

**Description:** modelar y exponer un formulario para tareas puntuales o semanales con título, descripción opcional, responsable y fecha de vencimiento.

**Acceptance criteria:**

- [x] Un miembro puede crear una tarea con título, responsable, vencimiento y repetición.
- [x] La repetición sólo admite `none` o `weekly`.
- [x] El responsable debe pertenecer al mismo hogar que quien crea la tarea.
- [x] No se puede acceder mediante el formulario a miembros de otros hogares.
- [x] Los casos válidos e inválidos están cubiertos por tests.

**Out of scope:** edición, eliminación, reasignación y rotación automática.

**Dependencies:** Task 4.

## Task 6 — Mostrar el panel personal de pendientes

**Goal:** responder al entrar a la pregunta «¿qué tengo que hacer yo?».

**Description:** construir una vista privada que muestre únicamente las tareas pendientes asignadas al usuario actual, priorizando primero las vencidas y después las próximas.

**Acceptance criteria:**

- [x] El panel sólo muestra tareas pendientes asignadas al usuario autenticado.
- [x] Las tareas vencidas aparecen antes que las no vencidas.
- [x] Dentro de cada grupo, las tareas se ordenan por vencimiento ascendente.
- [x] Las tareas completadas no aparecen en el panel principal.
- [x] No se filtra información perteneciente a otros hogares.

**Out of scope:** calendario, estadísticas, rankings y tablero completo del hogar.

**Dependencies:** Task 5.

## Task 7 — Completar tareas y conservar su resultado

**Goal:** permitir que el responsable registre de forma segura la finalización de una tarea.

**Description:** añadir la transición de pendiente a completada, almacenando quién la completó y cuándo, y protegiéndola frente a usuarios no autorizados o envíos repetidos.

**Acceptance criteria:**

- [x] Sólo la persona asignada puede completar la tarea.
- [x] La finalización registra usuario y fecha/hora.
- [x] Otro usuario no puede completar una tarea ajena.
- [x] Una tarea completada no puede completarse de nuevo.
- [x] La operación y sus permisos están cubiertos por tests.

**Out of scope:** aprobación por terceros, fotografías, comentarios y reapertura.

**Dependencies:** Task 6.

## Task 8 — Generar la siguiente ocurrencia semanal

**Goal:** mantener tareas semanales sin perder el historial de las ocurrencias completadas.

**Description:** cuando se completa una tarea semanal, crear exactamente una nueva tarea pendiente para la misma persona con vencimiento siete días después de la finalización.

**Acceptance criteria:**

- [x] Completar una tarea puntual no genera ninguna tarea nueva.
- [x] Completar una tarea semanal genera exactamente una ocurrencia pendiente.
- [x] La nueva ocurrencia conserva título, descripción, hogar, responsable y repetición.
- [x] Su vencimiento es siete días posterior a la fecha de finalización.
- [x] Los reintentos no pueden producir duplicados.

**Out of scope:** calendarios personalizados, recuperación de semanas omitidas y cambio automático de responsable.

**Dependencies:** Task 7.

## Task 9 — Añadir historial y endurecer el aislamiento

**Goal:** cerrar el MVP con una consulta útil del trabajo realizado y una revisión completa de autorización entre hogares.

**Description:** crear una vista de historial y añadir tests de regresión que intenten acceder a recursos de otros usuarios y hogares.

**Acceptance criteria:**

- [ ] El usuario puede consultar sus tareas completadas ordenadas desde la más reciente.
- [ ] El historial identifica la tarea y cuándo fue completada.
- [ ] Ninguna vista permite consultar o manipular tareas de otro hogar.
- [ ] La suite cubre accesos anónimos, usuarios del mismo hogar y usuarios de otro hogar.
- [ ] Toda la suite del proyecto pasa.

**Out of scope:** exportaciones, analítica y auditoría administrativa avanzada.

**Dependencies:** Task 8.

## Task 10 — Documentar y verificar el MVP completo

**Goal:** dejar una primera versión funcional, reproducible y comprensible para otra persona.

**Description:** actualizar la documentación de ejecución, revisar la navegación y ejecutar todas las comprobaciones del proyecto desde un entorno limpio.

**Acceptance criteria:**

- [ ] El README explica instalación, migraciones, ejecución y tests.
- [ ] Una persona puede reproducir el proyecto usando `uv sync`.
- [ ] `uv run python manage.py check` no informa de problemas.
- [ ] `uv run python manage.py test` ejecuta y supera toda la suite.
- [ ] Los cuatro flujos principales del `plan.md` pueden demostrarse manualmente.

**Out of scope:** despliegue público, CI/CD y funcionalidades posteriores al MVP.

**Dependencies:** Tasks 1–9.
