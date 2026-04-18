from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import serializers
from .models import TrainingSession, Booking
from django.utils import timezone


class SessionSerializer(serializers.ModelSerializer):
    trainer_name = serializers.CharField(source='trainer.get_full_name', read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    spots_remaining = serializers.IntegerField(read_only=True)

    class Meta:
        model = TrainingSession
        fields = ['id', 'title', 'session_type', 'date', 'start_time', 'end_time',
                  'trainer_name', 'price', 'location', 'is_available', 'spots_remaining']


class BookingSerializer(serializers.ModelSerializer):
    session = SessionSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['user']


class SessionsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        sessions = TrainingSession.objects.filter(
            date__gte=timezone.now().date(),
            status__in=['open', 'full']
        ).select_related('trainer')
        return Response(SessionSerializer(sessions, many=True).data)


class BookingsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(user=request.user).select_related('session')
        return Response(BookingSerializer(bookings, many=True).data)

    def post(self, request):
        session_id = request.data.get('session_id')
        try:
            session = TrainingSession.objects.get(id=session_id)
        except TrainingSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=404)

        if not session.is_available:
            return Response({'error': 'Session not available'}, status=400)

        booking, created = Booking.objects.get_or_create(
            user=request.user, session=session,
            defaults={'status': 'confirmed'}
        )
        if not created:
            return Response({'error': 'Already booked'}, status=400)

        return Response(BookingSerializer(booking).data, status=201)


urlpatterns = [
    path('sessions/', SessionsAPIView.as_view()),
    path('', BookingsAPIView.as_view()),
]
