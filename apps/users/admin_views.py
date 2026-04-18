from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta
from functools import wraps

from apps.users.models import CustomUser, TrainerProfile
from apps.memberships.models import MembershipPlan, UserMembership, GymClass
from apps.workouts.models import WorkoutProgram, Exercise
from apps.diet.models import DietPlan, FoodItem
from apps.bookings.models import TrainingSession, Booking
from apps.payments.models import Payment


# ── Auth decorator ────────────────────────────────────────────────────────────
def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, 'Admin access required.')
            return redirect('landing')
        return view_func(request, *args, **kwargs)
    return wrapper


# ── Dashboard ────────────────────────────────────────────────────────────────
@staff_required
def admin_dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)
    last_month_start = (month_start - timedelta(days=1)).replace(day=1)

    total_users    = CustomUser.objects.filter(is_staff=False).count()
    active_members = UserMembership.objects.filter(is_active=True, end_date__gte=today).count()
    monthly_rev    = Payment.objects.filter(
        created_at__date__gte=month_start, status='succeeded'
    ).aggregate(t=Sum('amount'))['t'] or 0
    last_rev       = Payment.objects.filter(
        created_at__date__gte=last_month_start,
        created_at__date__lt=month_start, status='succeeded'
    ).aggregate(t=Sum('amount'))['t'] or 0
    new_users_month = CustomUser.objects.filter(created_at__date__gte=month_start, is_staff=False).count()
    total_sessions  = Booking.objects.filter(status='completed').count()
    upcoming_sessions = TrainingSession.objects.filter(
        date__gte=today, status__in=['open', 'full']
    ).count()

    # Revenue chart — last 6 months
    chart_labels, chart_data = [], []
    for i in range(5, -1, -1):
        d = today - timedelta(days=30 * i)
        label = d.strftime('%b')
        rev = Payment.objects.filter(
            created_at__year=d.year,
            created_at__month=d.month,
            status='succeeded'
        ).aggregate(t=Sum('amount'))['t'] or 0
        chart_labels.append(label)
        chart_data.append(float(rev))

    # Plan distribution
    plan_data = UserMembership.objects.filter(
        is_active=True, end_date__gte=today
    ).values('plan__display_name').annotate(count=Count('id')).order_by('-count')

    context = {
        'today': today,
        'total_users': total_users,
        'active_members': active_members,
        'monthly_revenue': monthly_rev,
        'last_revenue': last_rev,
        'new_users_month': new_users_month,
        'total_sessions': total_sessions,
        'upcoming_sessions': upcoming_sessions,
        'recent_users': CustomUser.objects.filter(is_staff=False).order_by('-created_at')[:8],
        'recent_payments': Payment.objects.select_related('user').order_by('-created_at')[:8],
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'plan_data': list(plan_data),
    }
    return render(request, 'admin_panel/dashboard.html', context)


# ── Users ────────────────────────────────────────────────────────────────────
@staff_required
def admin_users(request):
    qs = CustomUser.objects.filter(is_staff=False).order_by('-created_at')
    q = request.GET.get('q', '')
    role = request.GET.get('role', '')
    if q:
        qs = qs.filter(Q(email__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q))
    if role == 'trainer':
        qs = qs.filter(is_trainer=True)
    elif role == 'member':
        qs = qs.filter(is_trainer=False)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/users.html', {
        'page_obj': page, 'q': q, 'role': role,
        'total': qs.count(),
    })


@staff_required
def admin_user_detail(request, user_id):
    u = get_object_or_404(CustomUser, id=user_id)
    memberships = UserMembership.objects.filter(user=u).order_by('-created_at')
    payments    = Payment.objects.filter(user=u).order_by('-created_at')
    bookings    = Booking.objects.filter(user=u).select_related('session').order_by('-created_at')[:10]

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'toggle_trainer':
            u.is_trainer = not u.is_trainer
            u.save()
            messages.success(request, f'{"Added as" if u.is_trainer else "Removed from"} trainers.')
        elif action == 'toggle_active':
            u.is_active = not u.is_active
            u.save()
            messages.success(request, f'User {"activated" if u.is_active else "deactivated"}.')
        elif action == 'assign_workout':
            prog_id = request.POST.get('program_id')
            if prog_id:
                prog = get_object_or_404(WorkoutProgram, id=prog_id)
                prog.assigned_users.add(u)
                messages.success(request, f'Assigned "{prog.title}" to {u.get_full_name()}.')
        elif action == 'assign_diet':
            diet_id = request.POST.get('diet_id')
            if diet_id:
                diet = get_object_or_404(DietPlan, id=diet_id)
                diet.assigned_users.add(u)
                messages.success(request, f'Assigned "{diet.title}" to {u.get_full_name()}.')
        elif action == 'grant_membership':
            plan_id = request.POST.get('plan_id')
            days    = int(request.POST.get('days', 30))
            if plan_id:
                plan = get_object_or_404(MembershipPlan, id=plan_id)
                UserMembership.objects.create(
                    user=u, plan=plan,
                    start_date=timezone.now().date(),
                    end_date=timezone.now().date() + timedelta(days=days),
                    status='active', is_active=True,
                )
                messages.success(request, f'Granted {plan.display_name} membership for {days} days.')
        return redirect('admin_user_detail', user_id=user_id)

    context = {
        'u': u,
        'memberships': memberships,
        'payments': payments,
        'bookings': bookings,
        'active_membership': u.active_membership,
        'all_programs': WorkoutProgram.objects.filter(is_active=True),
        'all_diets': DietPlan.objects.filter(is_active=True),
        'all_plans': MembershipPlan.objects.filter(is_active=True),
        'assigned_programs': WorkoutProgram.objects.filter(assigned_users=u, is_active=True),
        'assigned_diets': DietPlan.objects.filter(assigned_users=u, is_active=True),
    }
    return render(request, 'admin_panel/user_detail.html', context)


# ── Memberships ───────────────────────────────────────────────────────────────
@staff_required
def admin_memberships(request):
    today = timezone.now().date()
    qs = UserMembership.objects.select_related('user', 'plan').order_by('-created_at')
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        qs = qs.filter(is_active=True, end_date__gte=today)
    elif status_filter == 'expired':
        qs = qs.filter(Q(is_active=False) | Q(end_date__lt=today))
    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/memberships.html', {
        'page_obj': page,
        'status_filter': status_filter,
        'total_active': UserMembership.objects.filter(is_active=True, end_date__gte=today).count(),
    })


@staff_required
def admin_plans(request):
    plans = MembershipPlan.objects.annotate(
        subscriber_count=Count('usermembership', filter=Q(usermembership__is_active=True))
    ).order_by('price')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            MembershipPlan.objects.create(
                name=request.POST['name'],
                display_name=request.POST['display_name'],
                description=request.POST.get('description', ''),
                price=request.POST['price'],
                duration_days=int(request.POST.get('duration_days', 30)),
                features=[f.strip() for f in request.POST.get('features', '').split('\n') if f.strip()],
                is_active=True,
            )
            messages.success(request, 'Plan created!')
        elif action == 'toggle':
            plan = get_object_or_404(MembershipPlan, id=request.POST['plan_id'])
            plan.is_active = not plan.is_active
            plan.save()
            messages.success(request, f'Plan {"activated" if plan.is_active else "deactivated"}.')
        return redirect('admin_plans')

    return render(request, 'admin_panel/plans.html', {'plans': plans})


# ── Sessions ──────────────────────────────────────────────────────────────────
@staff_required
def admin_sessions(request):
    today = timezone.now().date()
    qs = TrainingSession.objects.select_related('trainer').order_by('-date', '-start_time')
    period = request.GET.get('period', 'upcoming')
    if period == 'upcoming':
        qs = qs.filter(date__gte=today)
    elif period == 'past':
        qs = qs.filter(date__lt=today)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            trainer_id = request.POST.get('trainer_id')
            trainer = get_object_or_404(CustomUser, id=trainer_id, is_trainer=True)
            TrainingSession.objects.create(
                trainer=trainer,
                title=request.POST['title'],
                session_type=request.POST['session_type'],
                date=request.POST['date'],
                start_time=request.POST['start_time'],
                end_time=request.POST['end_time'],
                max_participants=int(request.POST.get('max_participants', 1)),
                price=request.POST.get('price', 0),
                location=request.POST.get('location', 'Main Floor'),
                notes=request.POST.get('notes', ''),
            )
            messages.success(request, 'Session created!')
            return redirect('admin_sessions')
        elif action == 'cancel':
            s = get_object_or_404(TrainingSession, id=request.POST['session_id'])
            s.status = 'cancelled'
            s.save()
            messages.success(request, 'Session cancelled.')
            return redirect('admin_sessions')

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/sessions.html', {
        'page_obj': page, 'period': period,
        'trainers': CustomUser.objects.filter(is_trainer=True, is_active=True),
        'session_types': TrainingSession.SESSION_TYPE_CHOICES,
    })


# ── Workouts ──────────────────────────────────────────────────────────────────
@staff_required
def admin_workouts(request):
    qs = WorkoutProgram.objects.annotate(
        member_count=Count('assigned_users')
    ).order_by('-created_at')
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'toggle':
            prog = get_object_or_404(WorkoutProgram, id=request.POST['program_id'])
            prog.is_active = not prog.is_active
            prog.save()
            messages.success(request, f'Program {"activated" if prog.is_active else "deactivated"}.')
        return redirect('admin_workouts')
    paginator = Paginator(qs, 20)
    return render(request, 'admin_panel/workouts.html', {
        'page_obj': paginator.get_page(request.GET.get('page'))
    })


# ── Diet Plans ────────────────────────────────────────────────────────────────
@staff_required
def admin_diets(request):
    qs = DietPlan.objects.annotate(
        member_count=Count('assigned_users')
    ).order_by('-created_at')
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'toggle':
            diet = get_object_or_404(DietPlan, id=request.POST['diet_id'])
            diet.is_active = not diet.is_active
            diet.save()
            messages.success(request, f'Diet plan {"activated" if diet.is_active else "deactivated"}.')
        return redirect('admin_diets')
    paginator = Paginator(qs, 20)
    return render(request, 'admin_panel/diets.html', {
        'page_obj': paginator.get_page(request.GET.get('page'))
    })


# ── Payments ──────────────────────────────────────────────────────────────────
@staff_required
def admin_payments(request):
    qs = Payment.objects.select_related('user').order_by('-created_at')
    status_filter = request.GET.get('status', '')
    if status_filter:
        qs = qs.filter(status=status_filter)
    total_revenue = Payment.objects.filter(status='succeeded').aggregate(t=Sum('amount'))['t'] or 0
    paginator = Paginator(qs, 25)
    return render(request, 'admin_panel/payments.html', {
        'page_obj': paginator.get_page(request.GET.get('page')),
        'status_filter': status_filter,
        'total_revenue': total_revenue,
        'status_choices': Payment.STATUS_CHOICES,
    })
