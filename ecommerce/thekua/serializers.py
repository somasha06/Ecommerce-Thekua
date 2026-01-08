from rest_framework import serializers
from .models import *
from .utils import generate_otp,send_otp
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

User=get_user_model()

class SignupRequestSerializer(serializers.Serializer):
    email=serializers.EmailField(required=False)
    mobile_no=serializers.CharField(required=False)
    profile_pic=serializers.ImageField(required=False)

    def validate(self,data):
        if not data.get("email") and not data.get("mobile_no"):
            raise serializers.ValidationError("Email or mobile number is required")
        return data
    
    def create(self,validated_data):
        otp=generate_otp()

        pending_user=PendingUser.objects.create(
            email=validated_data.get("email"),
            mobile_no=validated_data.get("mobile_no"),
            otp=otp #sesseion id and created at is filled automatically by  Django 
        )

        send_otp(validated_data.get("email") or validated_data.get("mobile_no"),otp)

        return pending_user
    
class OTPVerifySerializer(serializers.Serializer):
    session_id=serializers.UUIDField()
    otp=serializers.CharField(max_length=6)
    username=serializers.CharField()
    password=serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            pending=PendingUser.objects.get(session_id=data["session_id"],otp=data["otp"])
        except PendingUser.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP")
        if pending.is_expired():
            raise serializers.ValidationError("OTP expired")
        if User.objects.filter(username=data["username"]).exists():
            raise serializers.ValidationError("Username already taken")
        
        data["pending_user"] = pending
        return data
    
    def create(self, validated_data):
        pending=validated_data["pending_user"]

        user=User.objects.create(
            username=validated_data["username"], #validated_data contains clean, validated input from the request
            email=pending.email,
            mobile_no=pending.mobile_no,
        )

        user.set_password(validated_data["password"])
        user.save()

        Role.objects.create(
            user=user,
            role=Role.CUSTOMER,
            active=True
        )

        pending.delete()
        return user
    
class LoginSerializer(serializers.Serializer):
    username=serializers.CharField()
    password=serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid username or password")

        if not user.is_active:
            raise serializers.ValidationError("User account is inactive")

        refresh = RefreshToken.for_user(user)

        return {
            "user":user,
            "user_id": user.id,
            "username": user.username,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
    
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model=Address
        exclude = ["user"]
        read_only_fields=["user"]

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "mobile_no","profile_pic"]
        extra_kwargs = {
            "email": {"required": True},
            # "mobile_no": {"required": True}
        }

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=["id","name","slug","is_active"]
        read_only_fields = ["slug"]

class SubCategorySeializer(serializers.ModelSerializer):
    category_name=serializers.ReadOnlyField(source="category.name")

    class Meta:
        model=SubCategory
        fields=["category", "category_name","id", "name","slug","image"]
        read_only_fields = ["slug"]

class ProductVariantSerializer(serializers.ModelSerializer):
    product_name=serializers.ReadOnlyField(source="product.name")

    class Meta:
        model=ProductVariant
        fields=["id","product","product_name","weight","price","discount_price","stock","sku","is_active"]

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=Productimage
        fields=["id","productimages"]

class ProductSerializer(serializers.ModelSerializer):
    subcategory_name=serializers.ReadOnlyField(source="subcategory.name")
    is_wishlisted = serializers.BooleanField(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model=Product
        fields=["id","name","subcategory","subcategory_name","starting_from","is_active","images","slug","is_wishlisted"]
        read_only_fields = ["slug"]



class ProductDetailSerializer(serializers.ModelSerializer):
    subcategory_name=serializers.ReadOnlyField(source="subcategory.name")
    seller_username=serializers.ReadOnlyField(source="seller.username")
    variants = ProductVariantSerializer(many=True, read_only=True,source="productvariants")
    
    class Meta:
        model=Product
        fields=["id","subcategory","subcategory_name","seller_username","name","description","created_at","updated_at","is_active","slug","variants"]

class Review(serializers.ModelSerializer):
    review_user=serializers.ReadOnlyField(source="user.username")
    class Meta:
        model=Reviews
        fields=["id","product","review_user","rating","comments"]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
class WishlistitemSerializer(serializers.ModelSerializer):
    
    product_name=serializers.ReadOnlyField(source="product_variant.product.name")
    product_weight=serializers.ReadOnlyField(source="product_variant.weight")
    product_price = serializers.ReadOnlyField(source="product_variant.price")
    product_slug=serializers.ReadOnlyField(source="product_variant.product.slug")

    class Meta:
        model=WishlistItem
        fields=["id","product_variant","product_name","product_slug","product_weight","product_price","added_at"]
        read_only_fields=["id","added_at"]

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ["id", "created_at"]

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model=Cart
        fields=["id","created_at"]

class CartItemSerializer(serializers.ModelSerializer):
    product_name=serializers.ReadOnlyField(source="product_variant.product.name")
    product_weight=serializers.ReadOnlyField(source="product_variant.weight")
    product_price = serializers.ReadOnlyField(source="product_variant.price")
    product_slug=serializers.ReadOnlyField(source="product_variant.product.slug")

    class Meta:
        model=CartItem
        fields=["id","product_variant","product_name","product_slug","product_weight","product_price","quantity","added_at"]
        read_only_fields=["id","added_at"]

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=OrderItem
        fields=["id","product_variant","quantity","price"]

        read_only_fields=["price"]

class OrderSerializer(serializers.ModelSerializer):
    items=OrderItemSerializer(many=True,read_only=True)
    class Meta:
        model=Order
        fields=["id","user","status","total_price","created_at","items"]

        read_only_fields=["user","total_price","created_at"]

class CouponApplySerializer(serializers.Serializer):
    code=serializers.CharField()
    # cart_total=serializers.DecimalField(max_digits=10,decimal_places=2)

class GetCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model=Coupon
        fields=["code","discount_type","discount_amount","min_price","max_price","expires_at",]
