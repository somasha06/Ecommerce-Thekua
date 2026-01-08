from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from thekua.models import Wishlist, Cart

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_related_objects(sender, instance, created, **kwargs):
    if created:
        Wishlist.objects.get_or_create(user=instance)
        Cart.objects.get_or_create(user=instance)

