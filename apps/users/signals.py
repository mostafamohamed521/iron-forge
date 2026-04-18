from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, TrainerProfile


@receiver(post_save, sender=CustomUser)
def create_trainer_profile(sender, instance, created, **kwargs):
    """Auto-create trainer profile when user is made a trainer."""
    if instance.is_trainer and not hasattr(instance, 'trainer_profile'):
        TrainerProfile.objects.get_or_create(user=instance)
