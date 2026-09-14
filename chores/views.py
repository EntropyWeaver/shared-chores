from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render


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
    """Render the authenticated dashboard placeholder."""
    return render(request, 'chores/dashboard.html')
