from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/edit/', views.UserProfileUpdateView.as_view(), name='profile_edit'),
    path('trainers/', views.TrainerListView.as_view(), name='trainers'),
    path('progress/add/', views.add_progress_entry, name='add_progress'),
    path('progress/data/', views.progress_data_api, name='progress_data'),
]
