# Shared Chores

Aplicación web para gestionar tareas domésticas compartidas entre 2 y 6 compañeros de piso adultos. Este repositorio forma parte del Module 1 de **AI Dev Tools Zoomcamp 2026** y desarrolla un MVP especificado antes de comenzar la implementación.

## Estado

MVP completo. Las Tasks 1–10 del backlog están implementadas y verificadas mediante tests automatizados y una instalación limpia.

## Funcionalidades

- Registro, inicio y cierre de sesión.
- Creación de un hogar con código de acceso único.
- Incorporación de hasta seis miembros mediante el código compartido.
- Creación de tareas puntuales o semanales con asignación manual.
- Panel personal con tareas vencidas y próximas tareas pendientes.
- Finalización restringida a la persona asignada.
- Historial personal ordenado por fecha de finalización.
- Generación idempotente de la siguiente ocurrencia semanal.
- Aislamiento de datos y operaciones entre hogares.

## Stack

- Python 3.12 o posterior.
- Django 6.1.
- SQLite.
- `uv` para dependencias y entorno virtual.
- Plantillas HTML renderizadas por Django.

## Instalación

Necesitas Git, Python 3.12 o posterior y [`uv`](https://docs.astral.sh/uv/) instalados.

```bash
git clone https://github.com/EntropyWeaver/shared-chores.git
cd shared-chores
uv sync
```

`uv sync` crea el entorno virtual e instala las versiones resueltas en `uv.lock`.

## Base de datos

Aplica las migraciones para crear la base de datos SQLite local:

```bash
uv run python manage.py migrate
```

La aplicación crea `db.sqlite3` en la raíz del proyecto. No se necesitan servicios externos para ejecutar el MVP localmente.

## Ejecución

```bash
uv run python manage.py runserver
```

Abre <http://127.0.0.1:8000/> en el navegador. Para probar dos usuarios simultáneamente, utiliza dos perfiles de navegador diferentes o una ventana privada.

## Comprobaciones y tests

```bash
uv run python manage.py check
uv run python manage.py makemigrations --check
uv run python manage.py test
```

La suite cubre las reglas de hogar, asignación, permisos, ordenación del panel, finalización, recurrencia semanal, historial y aislamiento entre hogares.

## Demostración manual del MVP

### 1. Crear y compartir un hogar

1. Registra el usuario `ana` y crea un hogar.
2. Copia el código de acceso mostrado en su panel.
3. En una segunda sesión, registra el usuario `leo` y únete con ese código.
4. Comprueba que ambos miembros aparecen en el mismo hogar.

### 2. Crear y asignar tareas

1. Desde la sesión de `ana`, crea una tarea puntual asignada a `leo`.
2. Crea también una tarea semanal asignada a `leo`.
3. Comprueba que el selector sólo ofrece miembros del hogar.
4. En la sesión de `leo`, verifica que ambas tareas aparecen en su panel y no en el de `ana`.

### 3. Consultar y completar responsabilidades

1. Crea una tarea con fecha pasada y otra con fecha futura para `leo`.
2. Comprueba que la vencida aparece primero y la futura después.
3. Intenta completar una tarea de `leo` desde la sesión de `ana`: la aplicación debe rechazarlo.
4. Complétala desde la sesión de `leo` y verifica que desaparece del panel.

### 4. Verificar recurrencia, historial y aislamiento

1. Completa la tarea semanal desde la sesión de `leo`.
2. Comprueba que aparece una única nueva ocurrencia pendiente con vencimiento siete días después de la finalización.
3. Abre **Mi historial** y verifica que la ocurrencia terminada muestra su fecha y hora.
4. Crea otro hogar con una tercera cuenta y confirma que sus tareas no aparecen ni pueden completarse desde las sesiones de `ana` o `leo`.

## Decisiones principales

- Cada usuario pertenece como máximo a un hogar y cada tarea queda vinculada a uno.
- Las consultas de tareas se acotan por hogar y usuario para evitar filtraciones.
- La finalización y la generación semanal ocurren en una única transacción.
- Cada ocurrencia sólo puede generar una sucesora, garantizado también por la base de datos.
- Las tareas completadas se conservan como historial en lugar de reutilizarse.

## Documentación

- [Especificación del producto](_docs/plan.md)
- [Backlog del MVP](backlog.md)

## Alcance

Este proyecto es un MVP local. El despliegue público, CI/CD, notificaciones, edición de tareas y calendarios de repetición personalizados quedan fuera de esta versión.
