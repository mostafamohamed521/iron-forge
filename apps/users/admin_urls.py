from django.urls import path
from apps.users import admin_views

urlpatterns = [
    path('', admin_views.admin_dashboard, name='admin_dashboard'),
    path('users/', admin_views.admin_users, name='admin_users'),
    path('users/<int:user_id>/', admin_views.admin_user_detail, name='admin_user_detail'),
    path('memberships/', admin_views.admin_memberships, name='admin_memberships'),
    path('plans/', admin_views.admin_plans, name='admin_plans'),
    path('sessions/', admin_views.admin_sessions, name='admin_sessions'),
    path('workouts/', admin_views.admin_workouts, name='admin_workouts'),
    path('diets/', admin_views.admin_diets, name='admin_diets'),
    path('payments/', admin_views.admin_payments, name='admin_payments'),
]
