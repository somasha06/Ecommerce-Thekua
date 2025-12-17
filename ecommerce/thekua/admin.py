from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Address, Role, PendingUser

admin.site.register(User)
admin.site.register(Address)
admin.site.register(Role)
admin.site.register(PendingUser)
