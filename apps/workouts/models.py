from django.db import models
from django.conf import settings


class MuscleGroup(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Exercise(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    EQUIPMENT_CHOICES = [
        ('none', 'No Equipment'),
        ('dumbbells', 'Dumbbells'),
        ('barbell', 'Barbell'),
        ('machine', 'Machine'),
        ('resistance_bands', 'Resistance Bands'),
        ('bodyweight', 'Bodyweight'),
        ('cable', 'Cable'),
        ('kettlebell', 'Kettlebell'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    instructions = models.TextField()
    muscle_groups = models.ManyToManyField(MuscleGroup, related_name='exercises')
    difficulty = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES)
    equipment = models.CharField(max_length=20, choices=EQUIPMENT_CHOICES, default='none')
    image = models.ImageField(upload_to='exercises/', blank=True, null=True)
    video_url = models.URLField(blank=True)
    calories_per_minute = models.FloatField(default=5.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class WorkoutProgram(models.Model):
    GOAL_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('endurance', 'Endurance'),
        ('flexibility', 'Flexibility'),
        ('maintenance', 'Maintenance'),
        ('general_fitness', 'General Fitness'),
    ]
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES)
    level = models.CharField(max_length=15, choices=LEVEL_CHOICES)
    duration_weeks = models.PositiveIntegerField(default=4)
    days_per_week = models.PositiveIntegerField(default=3)
    thumbnail = models.ImageField(upload_to='programs/', blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_programs'
    )
    assigned_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True,
        related_name='assigned_programs'
    )
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_level_display()})"


class WorkoutDay(models.Model):
    program = models.ForeignKey(WorkoutProgram, on_delete=models.CASCADE, related_name='days')
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=100)
    focus = models.CharField(max_length=100, blank=True, help_text='e.g., Upper Body, Legs, Full Body')
    rest_day = models.BooleanField(default=False)

    class Meta:
        ordering = ['day_number']
        unique_together = ['program', 'day_number']

    def __str__(self):
        return f"{self.program.title} - Day {self.day_number}: {self.title}"


class WorkoutSet(models.Model):
    day = models.ForeignKey(WorkoutDay, on_delete=models.CASCADE, related_name='sets')
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT)
    order = models.PositiveIntegerField(default=1)
    sets = models.PositiveIntegerField(default=3)
    reps = models.CharField(max_length=20, default='10', help_text='e.g., 10, 8-12, AMRAP')
    rest_seconds = models.PositiveIntegerField(default=60)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.exercise.name} - {self.sets}x{self.reps}"


class WorkoutLog(models.Model):
    """Track user's completed workouts."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workout_logs')
    program = models.ForeignKey(WorkoutProgram, on_delete=models.SET_NULL, null=True, blank=True)
    day = models.ForeignKey(WorkoutDay, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    duration_minutes = models.PositiveIntegerField(default=0)
    calories_burned = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    completed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.email} - {self.date}"
