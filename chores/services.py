import secrets
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone

from chores.models import Household, Membership, Task


ACCESS_CODE_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
ACCESS_CODE_LENGTH = 8
ACCESS_CODE_ATTEMPTS = 10


class HouseholdOperationError(Exception):
    """A household operation that cannot be completed safely."""


class TaskCompletionError(Exception):
    """Base error for a task completion that cannot be performed."""


class TaskNotFoundError(TaskCompletionError):
    """The task is unavailable within the user's household."""


class TaskPermissionError(TaskCompletionError):
    """The user is not allowed to complete the task."""


class TaskAlreadyCompletedError(TaskCompletionError):
    """The task has already completed its state transition."""


def generate_access_code():
    return ''.join(
        secrets.choice(ACCESS_CODE_ALPHABET)
        for _ in range(ACCESS_CODE_LENGTH)
    )


def _create_household_with_unique_code(name):
    for _ in range(ACCESS_CODE_ATTEMPTS):
        try:
            with transaction.atomic():
                return Household.objects.create(
                    name=name,
                    access_code=generate_access_code(),
                )
        except IntegrityError:
            continue

    raise HouseholdOperationError(
        'No se pudo generar un código único. Inténtalo de nuevo.'
    )


@transaction.atomic
def create_household_for_user(*, name, user):
    """Create a household and make the user its first member atomically."""
    locked_user = get_user_model().objects.select_for_update().get(pk=user.pk)

    if Membership.objects.filter(user=locked_user).exists():
        raise HouseholdOperationError('Ya perteneces a un hogar.')

    household = _create_household_with_unique_code(name)
    household.add_member(locked_user)
    return household


@transaction.atomic
def join_household_by_code(*, access_code, user):
    """Join an existing household by code while enforcing domain limits."""
    locked_user = get_user_model().objects.select_for_update().get(pk=user.pk)

    if Membership.objects.filter(user=locked_user).exists():
        raise HouseholdOperationError('Ya perteneces a un hogar.')

    try:
        household = Household.objects.select_for_update().get(
            access_code=access_code,
        )
    except Household.DoesNotExist as error:
        raise HouseholdOperationError(
            'No existe ningún hogar con ese código.'
        ) from error

    if household.is_full:
        raise HouseholdOperationError('Ese hogar ya tiene 6 miembros.')

    household.add_member(locked_user)
    return household


@transaction.atomic
def complete_task_for_user(*, task_id, user):
    """Complete a task once, recording its assignee and completion time."""
    membership = (
        Membership.objects.select_related('household')
        .filter(user=user)
        .first()
    )
    if membership is None:
        raise TaskNotFoundError

    try:
        task = Task.objects.select_for_update().get(
            pk=task_id,
            household=membership.household,
        )
    except Task.DoesNotExist as error:
        raise TaskNotFoundError from error

    if task.assignee_id != user.pk:
        raise TaskPermissionError

    if task.status == Task.Status.COMPLETED:
        raise TaskAlreadyCompletedError

    task.status = Task.Status.COMPLETED
    task.completed_by = user
    task.completed_at = timezone.now()
    task.save(update_fields=('status', 'completed_by', 'completed_at'))

    if task.recurrence == Task.Recurrence.WEEKLY:
        Task.objects.create(
            household=task.household,
            creator=task.creator,
            assignee=task.assignee,
            title=task.title,
            description=task.description,
            due_date=timezone.localdate(task.completed_at) + timedelta(days=7),
            recurrence=Task.Recurrence.WEEKLY,
            generated_from=task,
        )

    return task
