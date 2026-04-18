from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .models import MembershipPlan, UserMembership, GymClass


class MembershipPlansView(ListView):
    model = MembershipPlan
    template_name = 'memberships/plans.html'
    context_object_name = 'plans'

    def get_queryset(self):
        return MembershipPlan.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            ctx['current_membership'] = self.request.user.active_membership
        return ctx


@login_required
def select_plan(request, plan_id):
    plan = get_object_or_404(MembershipPlan, id=plan_id, is_active=True)
    # Redirect to payment flow
    request.session['selected_plan_id'] = plan_id
    return redirect('checkout', plan_id=plan_id)


@login_required
def my_membership(request):
    memberships = UserMembership.objects.filter(user=request.user).order_by('-created_at')
    active = memberships.filter(is_active=True, end_date__gte=timezone.now().date()).first()
    return render(request, 'memberships/my_membership.html', {
        'memberships': memberships,
        'active': active,
    })


class GymClassListView(ListView):
    model = GymClass
    template_name = 'memberships/classes.html'
    context_object_name = 'classes'
    paginate_by = 9

    def get_queryset(self):
        qs = GymClass.objects.filter(is_active=True).select_related('trainer')
        category = self.request.GET.get('category')
        if category:
            qs = qs.filter(category=category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = GymClass.CATEGORY_CHOICES
        return ctx
