from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import serializers
from .models import DietPlan, FoodLog, FoodItem


class DietPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietPlan
        fields = ['id', 'title', 'description', 'goal', 'duration_weeks', 'daily_calories']


class FoodLogSerializer(serializers.ModelSerializer):
    calories = serializers.FloatField(read_only=True)

    class Meta:
        model = FoodLog
        fields = '__all__'
        read_only_fields = ['user']


class DietPlansAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        plans = DietPlan.objects.filter(is_active=True, is_public=True)
        return Response(DietPlanSerializer(plans, many=True).data)


class FoodLogAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = FoodLog.objects.filter(user=request.user)
        return Response(FoodLogSerializer(logs, many=True).data)

    def post(self, request):
        serializer = FoodLogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


urlpatterns = [
    path('', DietPlansAPIView.as_view()),
    path('logs/', FoodLogAPIView.as_view()),
]
