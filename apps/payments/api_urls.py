from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'currency', 'status', 'payment_type',
                  'description', 'created_at']
        read_only_fields = fields


class PaymentsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = Payment.objects.filter(user=request.user)
        return Response(PaymentSerializer(payments, many=True).data)


urlpatterns = [
    path('', PaymentsAPIView.as_view()),
]
