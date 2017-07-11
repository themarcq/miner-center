from django.dispatch import receiver
from django.db.models.signals import post_save
from ..models import Farm
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=Farm)
def generate_token(sender, instance, created, *args, **kwargs):
    if created:
        Token.objects.create(user=instance.user)
