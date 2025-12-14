from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class User(AbstractUser):
    email=models.EmailField(unique=True)
    mobile_no=models.CharField(max_length=10,unique=True,null=True,blank=True)

    def __str__(self):
        return self.username
    
class PendingUser(models.Model):
    session_id=models.UUIDField(default=uuid.uuid4,unique=True) #uuid4=random unique ID
    email=models.EmailField(null=True,blank=True)
    mobile_no=models.CharField(max_length=10,null=True,blank=True)
    # username=models.CharField(max_length=150)
    # password=models.CharField(max_length=100)
    otp=models.CharField(max_length=6)
    created_at=models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)
    
    def __str__(self):
        return self.email or self.mobile_no or str(self.session_id)
    
class Role(models.Model):
    ADMIN="admin"
    SELLER="seller"
    CUSTOMER="customer"

    ROLE_CHOICES =[
        (ADMIN, "Admin"),
        (SELLER, "Seller"),
        (CUSTOMER, "Customer"),
    ]

    role=models.CharField(max_length=20,choices=ROLE_CHOICES)
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="roles")
    active=models.BooleanField(default=False)

    class Meta:
        unique_together=("user","role")

    def __str__(self):
        return f"{self.user.username}-{self.role}"
    
class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")
    name=models.CharField(max_length=100,null=True,blank=True)
    address=models.TextField(null=True,blank=True)
    pin_code=models.CharField(max_length=6,null=True,blank=True)
    state=models.CharField(max_length=100,null=True,blank=True)
    country=models.CharField(max_length=100,null=True,blank=True)
    profile_pic = models.ImageField(upload_to="profile_pic/", null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}-profile"
    

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)