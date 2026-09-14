import secrets

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from chores.models import Household, Membership


ACCESS_CODE_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
ACCESS_CODE_LENGTH = 8
ACCESS_CODE_ATTEMPTS = 10


class HouseholdOperationError(Exception):
    """A household operation that cannot be completed safely."""


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
