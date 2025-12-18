from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Address)
admin.site.register(Role)
admin.site.register(PendingUser)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(Wishlist)
admin.site.register(Reviews)
