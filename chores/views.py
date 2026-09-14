from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render

from chores.forms import CreateHouseholdForm, JoinHouseholdForm
from chores.models import Membership
from chores.services import (
    HouseholdOperationError,
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
    """Show household details or the actions for joining one."""
    membership = (
        Membership.objects.select_related('household')
        .filter(user=request.user)
        .first()
    )
    household = membership.household if membership else None
    household_members = (
        household.memberships.select_related('user') if household else []
    )

    return render(
        request,
        'chores/dashboard.html',
        {
            'household': household,
            'household_members': household_members,
        },
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
