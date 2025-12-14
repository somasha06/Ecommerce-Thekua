from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Profile, Role, PendingUser

admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Role)
admin.site.register(PendingUser)
