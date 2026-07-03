from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import LearningSession
from .services import register_session


@receiver(post_save, sender=LearningSession)
def on_session_created(sender, instance, created, **kwargs):
    if created:
        register_session(instance)
