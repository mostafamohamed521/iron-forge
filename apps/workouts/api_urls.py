from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import WorkoutProgram, Exercise, WorkoutLog


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'description', 'difficulty', 'equipment', 'video_url']


class WorkoutProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutProgram
        fields = ['id', 'title', 'description', 'goal', 'level', 'duration_weeks', 'days_per_week']


class WorkoutLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutLog
        fields = '__all__'
        read_only_fields = ['user']


class WorkoutsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        programs = WorkoutProgram.objects.filter(is_active=True, is_public=True)
        return Response(WorkoutProgramSerializer(programs, many=True).data)


class WorkoutLogsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = WorkoutLog.objects.filter(user=request.user)
        return Response(WorkoutLogSerializer(logs, many=True).data)

    def post(self, request):
        serializer = WorkoutLogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


urlpatterns = [
    path('', WorkoutsAPIView.as_view()),
    path('logs/', WorkoutLogsAPIView.as_view()),
]
