from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from chores.forms import CreateHouseholdForm, CreateTaskForm, JoinHouseholdForm
from chores.models import Membership, Task
from chores.services import (
    HouseholdOperationError,
    TaskAlreadyCompletedError,
    TaskNotFoundError,
    TaskPermissionError,
    complete_task_for_user,
    create_household_for_user,
    join_household_by_code,
)


def home(request):
    """Render the public landing page for Shared Chores."""
    return render(request, 'chores/home.html')


def signup(request):
    """Create a user account and start its authenticated session."""
    if request.user.is_authenticated:
        return redirect('chores:dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chores:dashboard')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required
def dashboard(request):
    """Show household details and the user's pending tasks."""
    membership = (
        Membership.objects.select_related('household')
        .filter(user=request.user)
        .first()
    )
    household = membership.household if membership else None
    household_members = (
        household.memberships.select_related('user') if household else []
    )
    overdue_tasks = []
    upcoming_tasks = []

    if household:
        today = timezone.localdate()
        personal_tasks = Task.objects.filter(
            household=household,
            assignee=request.user,
            status=Task.Status.PENDING,
        )
        overdue_tasks = personal_tasks.filter(
            due_date__lt=today,
        ).order_by('due_date', 'id')
        upcoming_tasks = personal_tasks.filter(
            due_date__gte=today,
        ).order_by('due_date', 'id')

    return render(
        request,
        'chores/dashboard.html',
        {
            'household': household,
            'household_members': household_members,
            'overdue_tasks': overdue_tasks,
            'upcoming_tasks': upcoming_tasks,
        },
    )


@login_required
def task_history(request):
    """Show the authenticated user's completed tasks in their household."""
    membership = (
        Membership.objects.select_related('household')
        .filter(user=request.user)
        .first()
    )
    completed_tasks = []

    if membership:
        completed_tasks = (
            Task.objects.filter(
                household=membership.household,
                assignee=request.user,
                status=Task.Status.COMPLETED,
            )
            .select_related('completed_by')
            .order_by('-completed_at', '-id')
        )

    return render(
        request,
        'chores/task_history.html',
        {'completed_tasks': completed_tasks},
    )


@login_required
def create_household(request):
    """Create a household for a user who does not have one yet."""
    if Membership.objects.filter(user=request.user).exists():
        messages.error(request, 'Ya perteneces a un hogar.')
        return redirect('chores:dashboard')

    if request.method == 'POST':
        form = CreateHouseholdForm(request.POST)
        if form.is_valid():
            try:
                create_household_for_user(
                    name=form.cleaned_data['name'],
                    user=request.user,
                )
            except HouseholdOperationError as error:
                form.add_error(None, str(error))
            else:
                messages.success(request, 'Hogar creado correctamente.')
                return redirect('chores:dashboard')
    else:
        form = CreateHouseholdForm()

    return render(request, 'chores/create_household.html', {'form': form})


@login_required
def join_household(request):
    """Join a household by its shared access code."""
    if Membership.objects.filter(user=request.user).exists():
        messages.error(request, 'Ya perteneces a un hogar.')
        return redirect('chores:dashboard')

    if request.method == 'POST':
        form = JoinHouseholdForm(request.POST)
        if form.is_valid():
            try:
                join_household_by_code(
                    access_code=form.cleaned_data['access_code'],
                    user=request.user,
                )
            except HouseholdOperationError as error:
                form.add_error(None, str(error))
            else:
                messages.success(request, 'Te has unido al hogar.')
                return redirect('chores:dashboard')
    else:
        form = JoinHouseholdForm()

    return render(request, 'chores/join_household.html', {'form': form})


@login_required
def create_task(request):
    """Create a task assigned to a member of the user's household."""
    membership = (
        Membership.objects.select_related('household')
        .filter(user=request.user)
        .first()
    )

    if membership is None:
        messages.error(
            request,
            'Necesitas pertenecer a un hogar para crear tareas.',
        )
        return redirect('chores:dashboard')

    household = membership.household

    if request.method == 'POST':
        form = CreateTaskForm(request.POST, household=household)
        if form.is_valid():
            task = form.save(commit=False)
            task.household = household
            task.creator = request.user
            task.save()
            messages.success(request, 'Tarea creada correctamente.')
            return redirect('chores:dashboard')
    else:
        form = CreateTaskForm(household=household)

    return render(
        request,
        'chores/create_task.html',
        {'form': form},
    )


@login_required
@require_POST
def complete_task(request, task_id):
    """Complete one task if the authenticated user is its assignee."""
    try:
        complete_task_for_user(task_id=task_id, user=request.user)
    except TaskNotFoundError as error:
        raise Http404 from error
    except TaskPermissionError as error:
        raise PermissionDenied from error
    except TaskAlreadyCompletedError:
        messages.error(request, 'Esta tarea ya estaba completada.')
    else:
        messages.success(request, 'Tarea completada correctamente.')

    return redirect('chores:dashboard')
