from django.urls import path
from . import views

urlpatterns = [
    path('', views.DietPlanListView.as_view(), name='diet_plans'),
    path('<int:pk>/', views.DietPlanDetailView.as_view(), name='diet_detail'),
    path('my/', views.my_diet, name='my_diet'),
    path('foods/', views.FoodLibraryView.as_view(), name='food_library'),
]
