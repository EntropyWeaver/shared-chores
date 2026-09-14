from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Household(models.Model):
    """A group of roommates who share chores."""

    MAX_MEMBERS = 6

    name = models.CharField(max_length=100)
    access_code = models.CharField(max_length=12, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.memberships.count()

    @property
    def is_full(self):
        return self.member_count >= self.MAX_MEMBERS

    def add_member(self, user):
        """Add a user while applying the membership domain rules."""
        return Membership.objects.create(
            household_id=self.pk,
            user_id=user.pk,
        )


class Membership(models.Model):
    """A user's membership in their single household."""

    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='membership',
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} in {self.household}'

    def clean(self):
        super().clean()

        if not self.household_id:
            return

        existing_members = Membership.objects.filter(
            household_id=self.household_id,
        ).exclude(pk=self.pk)

        if existing_members.count() >= Household.MAX_MEMBERS:
            raise ValidationError(
                {'household': 'A household cannot have more than 6 members.'}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
