from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from .models import MembershipPlan, UserMembership


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipPlan
        fields = '__all__'


class UserMembershipSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserMembership
        fields = '__all__'


class PlansAPIView(APIView):
    permission_classes = []

    def get(self, request):
        plans = MembershipPlan.objects.filter(is_active=True)
        return Response(PlanSerializer(plans, many=True).data)


class MyMembershipAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        membership = request.user.active_membership
        if not membership:
            return Response({'detail': 'No active membership.'}, status=404)
        return Response(UserMembershipSerializer(membership).data)


urlpatterns = [
    path('plans/', PlansAPIView.as_view()),
    path('my/', MyMembershipAPIView.as_view()),
]
