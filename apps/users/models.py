from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from PIL import Image
import os


class CustomUser(AbstractUser):
    """Extended user model with fitness profile data."""

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say'),
    ]

    FITNESS_GOAL_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('endurance', 'Endurance'),
        ('flexibility', 'Flexibility'),
        ('maintenance', 'Maintenance'),
        ('general_fitness', 'General Fitness'),
    ]

    FITNESS_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in format: '+999999999'. Up to 15 digits."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)

    # Physical stats
    height_cm = models.FloatField(null=True, blank=True)
    weight_kg = models.FloatField(null=True, blank=True)

    # Fitness preferences
    fitness_goal = models.CharField(max_length=20, choices=FITNESS_GOAL_CHOICES, default='general_fitness')
    fitness_level = models.CharField(max_length=15, choices=FITNESS_LEVEL_CHOICES, default='beginner')

    # Role
    is_trainer = models.BooleanField(default=False)

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    @property
    def bmi(self):
        if self.height_cm and self.weight_kg:
            height_m = self.height_cm / 100
            return round(self.weight_kg / (height_m ** 2), 1)
        return None

    @property
    def active_membership(self):
        from apps.memberships.models import UserMembership
        from django.utils import timezone
        return UserMembership.objects.filter(
            user=self,
            is_active=True,
            end_date__gte=timezone.now().date()
        ).first()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Resize profile image to save bandwidth
        if self.profile_image:
            try:
                img = Image.open(self.profile_image.path)
                if img.height > 400 or img.width > 400:
                    img.thumbnail((400, 400))
                    img.save(self.profile_image.path)
            except Exception:
                pass


class TrainerProfile(models.Model):
    """Extended profile for trainers."""

    SPECIALIZATION_CHOICES = [
        ('strength', 'Strength Training'),
        ('cardio', 'Cardio & Endurance'),
        ('yoga', 'Yoga & Flexibility'),
        ('nutrition', 'Nutrition & Diet'),
        ('crossfit', 'CrossFit'),
        ('martial_arts', 'Martial Arts'),
        ('rehabilitation', 'Rehabilitation'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='trainer_profile')
    specialization = models.CharField(max_length=20, choices=SPECIALIZATION_CHOICES)
    years_experience = models.PositiveIntegerField(default=0)
    certifications = models.TextField(blank=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_available = models.BooleanField(default=True)
    rating = models.FloatField(default=0.0)
    total_sessions = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Trainer Profile'

    def __str__(self):
        return f"Trainer: {self.user.get_full_name()}"


class ProgressEntry(models.Model):
    """Track user body measurements over time."""

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='progress_entries')
    date = models.DateField()
    weight_kg = models.FloatField(null=True, blank=True)
    body_fat_percentage = models.FloatField(null=True, blank=True)
    muscle_mass_kg = models.FloatField(null=True, blank=True)
    chest_cm = models.FloatField(null=True, blank=True)
    waist_cm = models.FloatField(null=True, blank=True)
    hips_cm = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']
        verbose_name = 'Progress Entry'
        verbose_name_plural = 'Progress Entries'

    def __str__(self):
        return f"{self.user.email} - {self.date}"
