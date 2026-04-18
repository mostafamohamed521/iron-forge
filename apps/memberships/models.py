from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class MembershipPlan(models.Model):
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('vip', 'VIP'),
    ]
    BILLING_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
    ]

    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CHOICES, default='monthly')
    duration_days = models.PositiveIntegerField(default=30)
    features = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    stripe_price_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['price']

    def __str__(self):
        return f"{self.display_name} - ${self.price}/{self.billing_cycle}"


class UserMembership(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending Payment'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberships')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    auto_renew = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Membership'

    def __str__(self):
        return f"{self.user.email} - {self.plan.display_name}"

    @property
    def days_remaining(self):
        delta = self.end_date - timezone.now().date()
        return max(delta.days, 0)

    @property
    def is_expired(self):
        return self.end_date < timezone.now().date()

    def save(self, *args, **kwargs):
        if self.is_expired:
            self.is_active = False
            self.status = 'expired'
        super().save(*args, **kwargs)


class GymClass(models.Model):
    """Group fitness classes (e.g., Yoga, Spin, HIIT)."""
    CATEGORY_CHOICES = [
        ('yoga', 'Yoga'),
        ('spin', 'Spin / Cycling'),
        ('hiit', 'HIIT'),
        ('pilates', 'Pilates'),
        ('boxing', 'Boxing'),
        ('zumba', 'Zumba'),
        ('strength', 'Strength Training'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='taught_classes'
    )
    duration_minutes = models.PositiveIntegerField(default=60)
    max_capacity = models.PositiveIntegerField(default=20)
    thumbnail = models.ImageField(upload_to='classes/', blank=True, null=True)
    required_plan = models.CharField(
        max_length=20,
        choices=MembershipPlan.PLAN_CHOICES,
        default='basic'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
