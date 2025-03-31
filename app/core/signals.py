from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from core.models import User, BasePlayer


@receiver(post_save, sender=get_user_model())
def automatically_create_basePlayer(sender, created, instance, **kwargs):
    """ Creates the BasePlayer object for a new user """
    if created:
        BasePlayer.objects.get_or_create(user=instance)

