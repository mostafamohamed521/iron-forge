from django.urls import path
from . import views

urlpatterns = [
    path('checkout/<int:plan_id>/', views.checkout, name='checkout'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('history/', views.payment_history, name='payment_history'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]
