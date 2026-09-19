# Shared Chores — Especificación del producto (MVP)

Estado: MVP completado y verificado

Módulo: AI Dev Tools Zoomcamp 2026 — Module 1  
Agente de programación elegido: Codex

## 1. Idea de partida

Una aplicación web para gestionar tareas domésticas compartidas entre compañeros de piso.

## 2. Problema

En un piso compartido, las tareas suelen acordarse verbalmente o mediante mensajes que se pierden. Esto provoca que no siempre quede claro qué debe hacer cada persona, cuándo corresponde hacerlo o qué tareas ya se completaron.

La aplicación debe ofrecer un lugar común, sencillo y verificable donde cada miembro pueda consultar sus responsabilidades domésticas.

## 3. Usuarios objetivo

- Entre 2 y 6 adultos que viven en el mismo piso.
- Cada persona utiliza su propia cuenta.
- Todos los miembros tienen el mismo nivel de permisos dentro del hogar.
- El MVP presupone una relación de confianza entre los convivientes; no incluye supervisores ni sistemas de aprobación.

## 4. Objetivo del MVP

Permitir que los miembros de un piso creen y asignen tareas, consulten con claridad lo que tienen pendiente y registren su finalización, incluyendo tareas puntuales y tareas que se repiten semanalmente.

## 5. Funcionalidades principales

### 5.1. Hogar compartido y miembros

- Una persona puede crear un hogar compartido.
- El sistema genera un código con el que otros usuarios pueden unirse.
- Un hogar admite un máximo de 6 miembros.
- Un usuario sólo pertenece a un hogar en el MVP.
- Sólo los miembros pueden consultar las tareas de ese hogar.

### 5.2. Creación y asignación manual de tareas

Cualquier miembro puede crear una tarea y asignarla manualmente a otro miembro del mismo hogar o a sí mismo.

Cada tarea contiene:

- Título obligatorio.
- Descripción opcional.
- Persona asignada.
- Fecha de vencimiento obligatoria.
- Tipo de repetición: puntual o semanal.

La asignación automática, rotatoria o basada en carga de trabajo queda fuera del MVP.

### 5.3. Panel personal

Al iniciar sesión, la pantalla principal muestra las tareas asignadas al usuario actual:

- Primero, las tareas vencidas.
- Después, las tareas pendientes ordenadas por la fecha de vencimiento más próxima.
- Las tareas completadas no aparecen en la lista principal, pero pueden consultarse en el historial.

Una tarea se considera vencida cuando sigue pendiente y su fecha de vencimiento ya ha pasado.

### 5.4. Finalización e historial

- Sólo la persona asignada puede marcar una tarea como completada.
- Al completarla, el sistema registra quién la completó y cuándo.
- Una tarea puntual pasa al historial y no vuelve a aparecer como pendiente.
- Al completar una tarea semanal, el sistema conserva la ocurrencia terminada en el historial y crea una nueva tarea pendiente para la misma persona, con vencimiento siete días después de la fecha de finalización.
- Una tarea ya completada no puede completarse por segunda vez.

## 6. Flujo principal

1. Una persona se registra e inicia sesión.
2. Crea un hogar o se une a uno mediante su código.
3. Un miembro crea una tarea, elige responsable, vencimiento y repetición.
4. La persona asignada ve la tarea en su panel personal.
5. La persona asignada marca la tarea como completada.
6. El sistema la guarda en el historial y, si era semanal, genera la siguiente ocurrencia.

## 7. Reglas de negocio

1. Todos los datos de una tarea pertenecen a un único hogar.
2. El creador y la persona asignada deben pertenecer al mismo hogar que la tarea.
3. Ningún usuario puede ver ni modificar tareas de otro hogar.
4. Sólo la persona asignada puede completar la tarea.
5. El estado persistido de una tarea es `pending` o `completed`; `overdue` se calcula a partir del estado y la fecha de vencimiento.
6. Las repeticiones admitidas son `none` y `weekly`.
7. Completar una tarea semanal produce exactamente una nueva ocurrencia pendiente.
8. La nueva ocurrencia semanal mantiene título, descripción, hogar y persona asignada.

## 8. Criterios de aceptación del MVP

- [x] Un usuario autenticado puede crear un hogar y obtener un código para compartirlo.
- [x] Otro usuario puede utilizar el código válido para unirse al hogar.
- [x] No puede haber más de 6 miembros en el mismo hogar.
- [x] Un miembro puede crear una tarea y asignarla a cualquier miembro del mismo hogar.
- [x] No se puede asignar una tarea a alguien ajeno al hogar.
- [x] El panel personal muestra sólo las tareas pendientes del usuario autenticado.
- [x] Las tareas vencidas aparecen antes que las pendientes no vencidas.
- [x] Otro miembro no puede completar una tarea ajena.
- [x] La persona asignada puede completar su tarea y ésta aparece en el historial.
- [x] Una tarea puntual completada no genera otra tarea.
- [x] Una tarea semanal completada genera exactamente una nueva ocurrencia con vencimiento siete días después.
- [x] Los usuarios no pueden acceder a los datos de otros hogares.

## 9. Fuera de alcance

- Rotación automática de responsables.
- Aprobación o verificación de tareas por otra persona.
- Fotografías como prueba de finalización.
- Notificaciones por correo, SMS o push.
- Chat, comentarios o menciones.
- Puntos, rankings, recompensas o penalizaciones.
- Repeticiones diarias, mensuales o calendarios personalizados.
- Integración con calendarios externos.
- Aplicación móvil nativa.
- Participación simultánea en varios hogares.
- Roles administrativos o jerarquías entre compañeros.
- Edición, reasignación y eliminación de tareas después de crearlas.

## 10. Restricciones técnicas iniciales

- Aplicación web construida con Django.
- Interfaz renderizada por el servidor; no se requiere React ni otro frontend independiente.
- Autenticación mediante las herramientas integradas de Django.
- SQLite como base de datos local para el ejercicio.
- Dependencias gestionadas con `uv`.
- Las reglas de permisos, ordenación, finalización y repetición deben estar cubiertas por tests automatizados.

## 11. Definición de terminado

El MVP se considera terminado cuando dos o más usuarios de prueba pueden compartir un hogar, crear y asignar tareas, consultar correctamente sus pendientes, completar únicamente las tareas propias, revisar el historial y verificar mediante tests que una tarea semanal genera su siguiente ocurrencia sin duplicados.
