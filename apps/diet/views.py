from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .models import DietPlan, FoodItem, FoodLog, Meal


class DietPlanListView(ListView):
    model = DietPlan
    template_name = 'diet/plans.html'
    context_object_name = 'plans'
    paginate_by = 9

    def get_queryset(self):
        qs = DietPlan.objects.filter(is_active=True, is_public=True)
        goal = self.request.GET.get('goal')
        if goal:
            qs = qs.filter(goal=goal)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['goals'] = DietPlan.GOAL_CHOICES
        return ctx


class DietPlanDetailView(LoginRequiredMixin, DetailView):
    model = DietPlan
    template_name = 'diet/plan_detail.html'
    context_object_name = 'plan'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['days'] = self.object.days.prefetch_related('meals__ingredients__food_item')
        ctx['is_assigned'] = self.object.assigned_users.filter(id=self.request.user.id).exists()
        return ctx


@login_required
def my_diet(request):
    assigned = DietPlan.objects.filter(assigned_users=request.user, is_active=True)
    today_logs = FoodLog.objects.filter(user=request.user, date=timezone.now().date())
    total_calories = sum(log.calories for log in today_logs)
    return render(request, 'diet/my_diet.html', {
        'assigned_plans': assigned,
        'today_logs': today_logs,
        'total_calories': total_calories,
    })


class FoodLibraryView(ListView):
    model = FoodItem
    template_name = 'diet/food_library.html'
    context_object_name = 'foods'
    paginate_by = 20

    def get_queryset(self):
        qs = FoodItem.objects.all()
        category = self.request.GET.get('category')
        search = self.request.GET.get('q')
        if category:
            qs = qs.filter(category=category)
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = FoodItem.CATEGORY_CHOICES
        return ctx
