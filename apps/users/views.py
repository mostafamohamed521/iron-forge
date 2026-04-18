from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import DetailView, UpdateView, CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Avg
from django_ratelimit.decorators import ratelimit

from .models import CustomUser, TrainerProfile, ProgressEntry
from .forms import (
    UserRegistrationForm, UserProfileForm,
    ProgressEntryForm, LoginForm
)
from apps.memberships.models import UserMembership
from apps.bookings.models import Booking
from apps.workouts.models import WorkoutProgram
from apps.diet.models import DietPlan


def landing_page(request):
    """Homepage / Landing page."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    from apps.memberships.models import MembershipPlan
    from apps.workouts.models import WorkoutProgram

    plans = MembershipPlan.objects.filter(is_active=True).order_by('price')
    membership_plans = []
    for p in plans:
        membership_plans.append({
            'id': p.id,
            'name': p.display_name,
            'price': p.price,
            'features': p.features,
            'highlighted': p.name == 'premium',
        })

    context = {
        'trainers': CustomUser.objects.filter(
            is_trainer=True, is_active=True
        ).select_related('trainer_profile')[:4],
        'membership_plans': membership_plans,
        'featured_programs': WorkoutProgram.objects.filter(
            is_active=True, is_public=True
        ).order_by('?')[:3],
        'total_members': CustomUser.objects.filter(is_staff=False, is_active=True).count(),
        'total_programs': WorkoutProgram.objects.filter(is_active=True).count(),
        'total_trainers': CustomUser.objects.filter(is_trainer=True, is_active=True).count(),
    }
    return render(request, 'landing.html', context)


@login_required
def dashboard(request):
    """Main user dashboard."""
    user = request.user
    active_membership = user.active_membership

    context = {
        'user': user,
        'active_membership': active_membership,
        'upcoming_bookings': Booking.objects.filter(
            user=user,
            session__date__gte=timezone.now().date(),
            status='confirmed'
        ).select_related('session', 'session__trainer')[:5],
        'assigned_workout': WorkoutProgram.objects.filter(
            assigned_users=user, is_active=True
        ).first(),
        'assigned_diet': DietPlan.objects.filter(
            assigned_users=user, is_active=True
        ).first(),
        'recent_progress': ProgressEntry.objects.filter(user=user)[:7],
        'stats': {
            'total_sessions': Booking.objects.filter(user=user, status='completed').count(),
            'workouts_this_month': Booking.objects.filter(
                user=user,
                status='completed',
                session__date__month=timezone.now().month
            ).count(),
        }
    }
    return render(request, 'users/dashboard.html', context)


class UserProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['progress_entries'] = ProgressEntry.objects.filter(
            user=self.request.user
        )[:10]
        ctx['bmi'] = self.request.user.bmi
        return ctx


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        # Validate file upload
        if 'profile_image' in self.request.FILES:
            file = self.request.FILES['profile_image']
            if file.content_type not in ['image/jpeg', 'image/png', 'image/webp']:
                form.add_error('profile_image', 'Only JPEG, PNG, WebP images are allowed.')
                return self.form_invalid(form)
            if file.size > 5 * 1024 * 1024:  # 5MB
                form.add_error('profile_image', 'Image must be under 5MB.')
                return self.form_invalid(form)
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


class TrainerListView(ListView):
    model = CustomUser
    template_name = 'users/trainers.html'
    context_object_name = 'trainers'
    paginate_by = 9

    def get_queryset(self):
        qs = CustomUser.objects.filter(
            is_trainer=True, is_active=True
        ).select_related('trainer_profile')

        specialization = self.request.GET.get('specialization')
        if specialization:
            qs = qs.filter(trainer_profile__specialization=specialization)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['specializations'] = TrainerProfile.SPECIALIZATION_CHOICES
        return ctx


@login_required
def add_progress_entry(request):
    if request.method == 'POST':
        form = ProgressEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            messages.success(request, 'Progress entry added!')
            return redirect('profile')
    else:
        form = ProgressEntryForm()

    return render(request, 'users/progress_form.html', {'form': form})


@login_required
def progress_data_api(request):
    """Return progress data as JSON for charts."""
    entries = ProgressEntry.objects.filter(
        user=request.user
    ).values('date', 'weight_kg', 'body_fat_percentage').order_by('date')

    return JsonResponse({
        'entries': list(entries),
        'bmi': request.user.bmi
    })


def admin_dashboard(request):
    """Custom admin analytics dashboard."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('landing')

    from apps.payments.models import Payment
    from django.db.models import Sum
    from datetime import timedelta
    from django.utils import timezone

    today = timezone.now().date()
    month_start = today.replace(day=1)

    context = {
        'total_users': CustomUser.objects.filter(is_staff=False).count(),
        'active_members': UserMembership.objects.filter(
            is_active=True, end_date__gte=today
        ).count(),
        'monthly_revenue': Payment.objects.filter(
            created_at__date__gte=month_start,
            status='succeeded'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'new_users_this_month': CustomUser.objects.filter(
            created_at__date__gte=month_start
        ).count(),
        'recent_users': CustomUser.objects.filter(
            is_staff=False
        ).order_by('-created_at')[:10],
        'recent_payments': Payment.objects.order_by('-created_at')[:10],
        'trainers': CustomUser.objects.filter(is_trainer=True),
    }
    return render(request, 'admin/custom_dashboard.html', context)


def error_404(request, exception=None):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)
