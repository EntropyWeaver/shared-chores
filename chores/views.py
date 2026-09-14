from django.shortcuts import render


def home(request):
    """Render the public landing page for Shared Chores."""
    return render(request, 'chores/home.html')
