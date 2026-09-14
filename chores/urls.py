from django.contrib.auth import views as auth_views
from django.urls import path

from chores import views

app_name = 'chores'

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/signup/', views.signup, name='signup'),
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login',
    ),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('households/create/', views.create_household, name='create-household'),
    path('households/join/', views.join_household, name='join-household'),
]
