from django.urls import path
from . import views

urlpatterns = [
    path('', views.SessionListView.as_view(), name='sessions'),
    path('book/<int:session_id>/', views.book_session, name='book_session'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('my/', views.my_bookings, name='my_bookings'),
    path('rate/<int:booking_id>/', views.rate_session, name='rate_session'),
    path('calendar/', views.calendar_api, name='calendar_api'),
]
