import stripe
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import timedelta

from .models import Payment
from apps.memberships.models import MembershipPlan, UserMembership

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def checkout(request, plan_id):
    plan = get_object_or_404(MembershipPlan, id=plan_id, is_active=True)

    if request.method == 'POST':
        try:
            # Create Stripe PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=int(plan.price * 100),  # cents
                currency='usd',
                metadata={
                    'user_id': request.user.id,
                    'plan_id': plan.id,
                    'user_email': request.user.email,
                }
            )

            # Create pending payment record
            payment = Payment.objects.create(
                user=request.user,
                amount=plan.price,
                currency='USD',
                status='pending',
                payment_type='membership',
                stripe_payment_intent_id=intent.id,
                description=f"Membership: {plan.display_name}",
            )

            return JsonResponse({
                'client_secret': intent.client_secret,
                'payment_id': payment.id,
            })

        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'payments/checkout.html', {
        'plan': plan,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    })


@login_required
def payment_success(request):
    payment_intent_id = request.GET.get('payment_intent')
    if payment_intent_id:
        try:
            payment = Payment.objects.get(
                stripe_payment_intent_id=payment_intent_id,
                user=request.user
            )
            if payment.status == 'pending':
                # Verify with Stripe
                intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                if intent.status == 'succeeded':
                    payment.status = 'succeeded'
                    payment.save()

                    # Activate membership
                    plan = MembershipPlan.objects.get(id=intent.metadata['plan_id'])
                    start_date = timezone.now().date()
                    end_date = start_date + timedelta(days=plan.duration_days)

                    membership = UserMembership.objects.create(
                        user=request.user,
                        plan=plan,
                        start_date=start_date,
                        end_date=end_date,
                        status='active',
                        is_active=True,
                    )
                    payment.membership = membership
                    payment.save()

                    messages.success(request, f'🎉 Welcome to {plan.display_name}! Your membership is now active.')
                    return redirect('dashboard')

        except (Payment.DoesNotExist, stripe.error.StripeError, MembershipPlan.DoesNotExist):
            pass

    messages.error(request, 'Payment verification failed. Please contact support.')
    return redirect('membership_plans')


@login_required
def payment_cancel(request):
    messages.info(request, 'Payment cancelled.')
    return redirect('membership_plans')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        Payment.objects.filter(
            stripe_payment_intent_id=intent['id']
        ).update(status='succeeded')

    elif event['type'] == 'payment_intent.payment_failed':
        intent = event['data']['object']
        Payment.objects.filter(
            stripe_payment_intent_id=intent['id']
        ).update(status='failed')

    return HttpResponse(status=200)


@login_required
def payment_history(request):
    from django.db.models import Sum
    payments = Payment.objects.filter(user=request.user)
    total_paid = payments.filter(status='succeeded').aggregate(t=Sum('amount'))['t'] or 0
    return render(request, 'payments/history.html', {'payments': payments, 'total_paid': total_paid})
