from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class User(AbstractUser):
    email=models.EmailField(unique=True)
    mobile_no=models.CharField(max_length=10,unique=True,null=True,blank=True)
    profile_pic = models.ImageField(upload_to="profile_pic/", null=True, blank=True)

    def __str__(self):
        return self.username
    
class PendingUser(models.Model):
    session_id=models.UUIDField(default=uuid.uuid4,unique=True) #uuid4=random unique ID
    email=models.EmailField(null=True,blank=True)
    mobile_no=models.CharField(max_length=10,null=True,blank=True)
    otp=models.CharField(max_length=6)
    created_at=models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(days=365)
    
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
    
class Address(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="address")
    name=models.CharField(max_length=100,null=True,blank=True)
    phone=models.CharField(max_length=10,null=True,blank=True)
    street=models.TextField(null=True,blank=True)
    city=models.CharField(max_length=100,null=True,blank=True)
    pin_code=models.CharField(max_length=6,null=True,blank=True)
    state=models.CharField(max_length=100,null=True,blank=True)
    country=models.CharField(max_length=100,null=True,blank=True)
    ADDRESS_CHOICES=(
        ("home","Home"),
        ("work","Work"),
    )
    address_type=models.CharField(max_length=10,choices=ADDRESS_CHOICES,default="home")
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}-name"
    

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)

class Category(models.Model):
    name=models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
class SubCategory(models.Model):
    category=models.ForeignKey(Category,related_name="subcategory",on_delete=models.CASCADE)
    name=models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Product(models.Model):
    # category=models.ForeignKey(Category,on_delete=models.CASCADE)
    sub_category=models.ForeignKey(SubCategory,on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    description=models.CharField(max_length=500)
    seller=models.ForeignKey(User,on_delete=models.CASCADE)
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)
    is_active=models.BooleanField(default=False)

class ProductVariant(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    weight=models.CharField(max_length=200)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    discount_price=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    stock=models.PositiveIntegerField()
    sku=models.PositiveIntegerField()
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.name} - {self.weight}"
    
class Reviews(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="reviews")
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])    
    comments=models.TextField(blank=True)
    created_at=models.DateField(auto_now_add=True)

    class Meta:
        unique_together=("product","user")

    def __str__(self):
        return f"{self.product.name} - {self.rating}⭐ by {self.user.username}"


    
