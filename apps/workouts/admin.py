from django.contrib import admin
from .models import MuscleGroup, Exercise, WorkoutProgram, WorkoutDay, WorkoutSet, WorkoutLog


@admin.register(MuscleGroup)
class MuscleGroupAdmin(admin.ModelAdmin):
    list_display = ['name']


class WorkoutSetInline(admin.TabularInline):
    model = WorkoutSet
    extra = 1


class WorkoutDayInline(admin.StackedInline):
    model = WorkoutDay
    extra = 1


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'difficulty', 'equipment']
    list_filter = ['difficulty', 'equipment']
    filter_horizontal = ['muscle_groups']
    search_fields = ['name']


@admin.register(WorkoutProgram)
class WorkoutProgramAdmin(admin.ModelAdmin):
    list_display = ['title', 'goal', 'level', 'duration_weeks', 'is_active']
    list_filter = ['goal', 'level', 'is_active']
    filter_horizontal = ['assigned_users']
    inlines = [WorkoutDayInline]


@admin.register(WorkoutDay)
class WorkoutDayAdmin(admin.ModelAdmin):
    list_display = ['program', 'day_number', 'title', 'rest_day']
    inlines = [WorkoutSetInline]


@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'program', 'date', 'duration_minutes', 'calories_burned']
    list_filter = ['date']
    search_fields = ['user__email']
    date_hierarchy = 'date'
