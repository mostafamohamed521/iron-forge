from django.db import models
from django.conf import settings
from django.utils import timezone


class TrainingSession(models.Model):
    """A schedulable training slot offered by a trainer."""
    SESSION_TYPE_CHOICES = [
        ('personal', 'Personal Training'),
        ('group', 'Group Class'),
        ('online', 'Online Session'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('full', 'Full'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='training_sessions'
    )
    title = models.CharField(max_length=100)
    session_type = models.CharField(max_length=10, choices=SESSION_TYPE_CHOICES, default='personal')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_participants = models.PositiveIntegerField(default=1)
    current_participants = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    location = models.CharField(max_length=200, blank=True, default='Main Gym Floor')
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.title} - {self.date} {self.start_time}"

    @property
    def is_available(self):
        return (
            self.status == 'open' and
            self.current_participants < self.max_participants and
            self.date >= timezone.now().date()
        )

    @property
    def spots_remaining(self):
        return max(self.max_participants - self.current_participants, 0)


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='bookings'
    )
    session = models.ForeignKey(
        TrainingSession, on_delete=models.CASCADE,
        related_name='bookings'
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='confirmed')
    notes = models.TextField(blank=True)
    rating = models.PositiveIntegerField(null=True, blank=True)
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'session']

    def __str__(self):
        return f"{self.user.email} → {self.session}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        # Update participant count
        if is_new and self.status == 'confirmed':
            self.session.current_participants = self.session.bookings.filter(
                status='confirmed'
            ).count()
            if self.session.current_participants >= self.session.max_participants:
                self.session.status = 'full'
            self.session.save()

    def cancel(self):
        self.status = 'cancelled'
        self.save()
        self.session.current_participants = max(
            self.session.bookings.filter(status='confirmed').count(), 0
        )
        if self.session.status == 'full':
            self.session.status = 'open'
        self.session.save()
