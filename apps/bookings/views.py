from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView
from django.utils import timezone
from django.http import JsonResponse
from .models import TrainingSession, Booking


class SessionListView(ListView):
    model = TrainingSession
    template_name = 'bookings/sessions.html'
    context_object_name = 'sessions'
    paginate_by = 12

    def get_queryset(self):
        qs = TrainingSession.objects.filter(
            date__gte=timezone.now().date(),
            status__in=['open', 'full']
        ).select_related('trainer', 'trainer__trainer_profile')

        trainer_id = self.request.GET.get('trainer')
        session_type = self.request.GET.get('type')
        date = self.request.GET.get('date')

        if trainer_id:
            qs = qs.filter(trainer_id=trainer_id)
        if session_type:
            qs = qs.filter(session_type=session_type)
        if date:
            qs = qs.filter(date=date)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from apps.users.models import CustomUser
        ctx['trainers'] = CustomUser.objects.filter(is_trainer=True, is_active=True)
        ctx['session_types'] = TrainingSession.SESSION_TYPE_CHOICES
        if self.request.user.is_authenticated:
            ctx['user_bookings'] = set(
                self.request.user.bookings.filter(
                    status='confirmed'
                ).values_list('session_id', flat=True)
            )
        return ctx


@login_required
def book_session(request, session_id):
    session = get_object_or_404(TrainingSession, id=session_id)

    if not session.is_available:
        messages.error(request, 'This session is no longer available.')
        return redirect('sessions')

    if Booking.objects.filter(user=request.user, session=session).exists():
        messages.warning(request, 'You already have a booking for this session.')
        return redirect('my_bookings')

    # Check membership
    if not request.user.active_membership:
        messages.error(request, 'You need an active membership to book sessions.')
        return redirect('membership_plans')

    if request.method == 'POST':
        Booking.objects.create(
            user=request.user,
            session=session,
            status='confirmed',
            notes=request.POST.get('notes', '')
        )
        messages.success(request, f'Session "{session.title}" booked successfully!')
        return redirect('my_bookings')

    return render(request, 'bookings/confirm_booking.html', {'session': session})


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status == 'confirmed':
        booking.cancel()
        messages.success(request, 'Booking cancelled.')
    return redirect('my_bookings')


@login_required
def my_bookings(request):
    upcoming = Booking.objects.filter(
        user=request.user,
        session__date__gte=timezone.now().date(),
        status='confirmed'
    ).select_related('session', 'session__trainer')

    past = Booking.objects.filter(
        user=request.user,
        session__date__lt=timezone.now().date()
    ).select_related('session', 'session__trainer')[:20]

    return render(request, 'bookings/my_bookings.html', {
        'upcoming': upcoming,
        'past': past,
    })


@login_required
def rate_session(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        review = request.POST.get('review', '')
        booking.rating = min(max(rating, 1), 5)
        booking.review = review
        booking.save()
        messages.success(request, 'Review submitted! Thank you.')
        return redirect('my_bookings')
    return render(request, 'bookings/rate_session.html', {'booking': booking})


def calendar_api(request):
    """Return sessions as JSON for calendar widget."""
    sessions = TrainingSession.objects.filter(
        date__gte=timezone.now().date(),
        status__in=['open', 'full']
    ).values('id', 'title', 'date', 'start_time', 'end_time', 'session_type', 'spots_remaining')
    return JsonResponse({'sessions': list(sessions)})
