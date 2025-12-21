from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from thekua.models import Wishlist

User = settings.AUTH_USER_MODEL

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_wishlist(sender, instance, created, **kwargs):
    if created:
        Wishlist.objects.create(user=instance)
