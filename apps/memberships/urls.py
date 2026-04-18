from django.urls import path
from . import views

urlpatterns = [
    path('', views.MembershipPlansView.as_view(), name='membership_plans'),
    path('select/<int:plan_id>/', views.select_plan, name='select_plan'),
    path('my/', views.my_membership, name='my_membership'),
    path('classes/', views.GymClassListView.as_view(), name='gym_classes'),
]
