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
# admin.site.register(Wishlist)
admin.site.register(WishlistItem)
admin.site.register(CartItem)
admin.site.register(OrderItem)
admin.site.register(Reviews)
# admin.site.register(Coupon)
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "discount_amount", "expires_at", "active")
    search_fields = ("code",)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    readonly_fields = ("user",)
    def has_add_permission(self, request):
        return False
    
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    readonly_fields = ("user",)
    def has_add_permission(self, request):
        return False
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ("user",)
    def has_add_permission(self, request):
        return False