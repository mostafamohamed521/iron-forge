from django.urls import path
from . import views

urlpatterns = [
    path('', views.WorkoutProgramListView.as_view(), name='workouts'),
    path('<int:pk>/', views.WorkoutProgramDetailView.as_view(), name='workout_detail'),
    path('exercises/', views.ExerciseListView.as_view(), name='exercises'),
    path('my/', views.my_workouts, name='my_workouts'),
    path('log/<int:day_id>/', views.log_workout, name='log_workout'),
]
