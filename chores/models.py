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


class Task(models.Model):
    """A household chore assigned to one of its members."""

    class Recurrence(models.TextChoices):
        NONE = 'none', 'Puntual'
        WEEKLY = 'weekly', 'Semanal'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        COMPLETED = 'completed', 'Completada'

    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name='tasks',
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_tasks',
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='assigned_tasks',
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    recurrence = models.CharField(
        max_length=6,
        choices=Recurrence,
        default=Recurrence.NONE,
    )
    status = models.CharField(
        max_length=9,
        choices=Status,
        default=Status.PENDING,
        editable=False,
    )
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        editable=False,
        null=True,
        on_delete=models.PROTECT,
        related_name='completed_tasks',
    )
    completed_at = models.DateTimeField(
        blank=True,
        editable=False,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()

        if not self.household_id:
            return

        errors = {}
        household_members = Membership.objects.filter(
            household_id=self.household_id,
        )

        if self.creator_id and not household_members.filter(
            user_id=self.creator_id,
        ).exists():
            errors['creator'] = 'The creator must belong to the task household.'

        if self.assignee_id and not household_members.filter(
            user_id=self.assignee_id,
        ).exists():
            errors['assignee'] = 'The assignee must belong to the task household.'

        if self.status == self.Status.COMPLETED:
            if not self.completed_by_id:
                errors['completed_by'] = 'A completed task must record its user.'
            elif self.assignee_id != self.completed_by_id:
                errors['completed_by'] = 'Only the assignee can complete this task.'

            if not self.completed_at:
                errors['completed_at'] = 'A completed task must record its time.'
        else:
            if self.completed_by_id:
                errors['completed_by'] = 'A pending task cannot have a completing user.'
            if self.completed_at:
                errors['completed_at'] = 'A pending task cannot have a completion time.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
