from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import WorkoutProgram, WorkoutDay, Exercise, WorkoutLog
from django.utils import timezone


class WorkoutProgramListView(ListView):
    model = WorkoutProgram
    template_name = 'workouts/programs.html'
    context_object_name = 'programs'
    paginate_by = 9

    def get_queryset(self):
        qs = WorkoutProgram.objects.filter(is_active=True, is_public=True)
        level = self.request.GET.get('level')
        goal = self.request.GET.get('goal')
        if level:
            qs = qs.filter(level=level)
        if goal:
            qs = qs.filter(goal=goal)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['levels'] = WorkoutProgram.LEVEL_CHOICES
        ctx['goals'] = WorkoutProgram.GOAL_CHOICES
        return ctx


class WorkoutProgramDetailView(LoginRequiredMixin, DetailView):
    model = WorkoutProgram
    template_name = 'workouts/program_detail.html'
    context_object_name = 'program'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['days'] = self.object.days.prefetch_related('sets__exercise', 'sets__exercise__muscle_groups')
        ctx['is_assigned'] = self.object.assigned_users.filter(id=self.request.user.id).exists()
        return ctx


class ExerciseListView(ListView):
    model = Exercise
    template_name = 'workouts/exercises.html'
    context_object_name = 'exercises'
    paginate_by = 12

    def get_queryset(self):
        qs = Exercise.objects.prefetch_related('muscle_groups')
        difficulty = self.request.GET.get('difficulty')
        equipment = self.request.GET.get('equipment')
        if difficulty:
            qs = qs.filter(difficulty=difficulty)
        if equipment:
            qs = qs.filter(equipment=equipment)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['difficulties'] = Exercise.DIFFICULTY_CHOICES
        ctx['equipment_choices'] = Exercise.EQUIPMENT_CHOICES
        return ctx


@login_required
def my_workouts(request):
    assigned = WorkoutProgram.objects.filter(assigned_users=request.user, is_active=True)
    logs = WorkoutLog.objects.filter(user=request.user)[:10]
    return render(request, 'workouts/my_workouts.html', {
        'assigned_programs': assigned,
        'recent_logs': logs,
    })


@login_required
def log_workout(request, day_id):
    from django.contrib import messages
    day = get_object_or_404(WorkoutDay, id=day_id)
    if request.method == 'POST':
        WorkoutLog.objects.create(
            user=request.user,
            program=day.program,
            day=day,
            date=timezone.now().date(),
            duration_minutes=int(request.POST.get('duration', 0)),
            calories_burned=int(request.POST.get('calories', 0)),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, 'Workout logged!')
    return render(request, 'workouts/log_workout.html', {'day': day})
