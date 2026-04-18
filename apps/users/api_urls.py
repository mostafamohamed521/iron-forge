from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from .models import CustomUser, ProgressEntry


class UserSerializer(serializers.ModelSerializer):
    bmi = serializers.FloatField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone',
            'fitness_goal', 'fitness_level', 'height_cm', 'weight_kg', 'bmi'
        ]
        read_only_fields = ['id', 'email']


class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressEntry
        fields = '__all__'
        read_only_fields = ['user']


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class ProgressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entries = ProgressEntry.objects.filter(user=request.user)
        serializer = ProgressSerializer(entries, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProgressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


urlpatterns = [
    path('profile/', UserProfileAPIView.as_view(), name='api_profile'),
    path('progress/', ProgressAPIView.as_view(), name='api_progress'),
]
