from django.shortcuts import render #**
from rest_framework.views import APIView #**
from rest_framework.response import Response #**
from rest_framework import status #**
from .serializers import * #**
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from .models import *  #**
from rest_framework.viewsets import ModelViewSet
from django.db.models import Exists, OuterRef, BooleanField, Value
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from .permissions import *
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.permissions import AllowAny #**
from django.db.models import Q,Min
from decimal import Decimal, InvalidOperation
from django.db.models.functions import Coalesce
import razorpay
from razorpay.errors import SignatureVerificationError
from django.db.models import F


class SignupRequestAPIView(APIView):
    authentication_classes = [] 
    permission_classes = [AllowAny]
    
    def post(self,request):

        serializer=SignupRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pending_user=serializer.save()

        return Response({"message": "OTP sent successfully","session_id": str(pending_user.session_id)},status=status.HTTP_200_OK)
    

class OTPVerifyAPIView(APIView):
    authentication_classes = [] 
    permission_classes = [AllowAny]

    def post(self,request):
        serializer=OTPVerifySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response({"message": "User created successfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginAPIView(APIView):
    authentication_classes = [] 
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data

            return Response(
                {
                    "message": "Login successful",
                    "user_id": data["user_id"],
                    "username": data["username"],
                    "access": data["access"],
                    "refresh": data["refresh"],
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressViewSet(ModelViewSet):
    serializer_class=AddressSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self,serializer):
        serializer.save(user=self.request.user)

class CustomerProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Profile updated",
            "data": serializer.data
        })




class CategoryViewSet(ModelViewSet):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer
    permission_classes=[IsAdminOrSellerOrReadOnly]
    
class SubcategoryViewSet(ModelViewSet):
    # queryset=SubCategory.objects.all()
    serializer_class=SubCategorySeializer
    permission_classes=[IsAdminOrSellerOrReadOnly]

    def get_queryset(self):
        queryset=SubCategory.objects.all()

        category_id=self.request.query_params.get("category")
        if category_id:
            queryset=queryset.filter(category_id=category_id) #✔️ Filters subcategories of that category only
        return queryset
    
class ProductViewSet(ModelViewSet):
    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrSellerOrReadOnly()]
        return []

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def get_queryset(self):
        queryset = Product.objects.prefetch_related("productvariants") #prefetch helps to get the variant in dict form inside product
        user=self.request.user

        if self.action in ["list", "retrieve"]:
            queryset = queryset.filter(is_active=True)

            search = self.request.query_params.get("search")
            sort = self.request.query_params.get("sort")
            min_price = self.request.query_params.get("min_price")
            max_price = self.request.query_params.get("max_price")
            subCategory_id=self.request.query_params.get("subcategory")

            if subCategory_id:
                queryset=queryset.filter(subCategory_id=subCategory_id)
            
            if search:
                q=(
                    Q(name__icontains=search) |
                    Q(description__icontains=search) |
                    Q(subcategory__name__icontains=search) |
                    Q(subcategory__category__name__icontains=search)
                )

                try:
                    price = Decimal(search)
                    q |= Q(productvariants__price=price)
                    q |= Q(productvariants__discount_price=price)
                except InvalidOperation:
                    pass

                queryset=queryset.filter(q)

            if min_price:
                queryset = queryset.filter(
                    productvariants__price__gte=Decimal(min_price)
                )

            if max_price:
                queryset = queryset.filter(
                    productvariants__price__lte=Decimal(max_price)
                )


            if sort == "price_low":
                queryset = queryset.order_by("effective_price")
            elif sort == "price_high":
                queryset = queryset.order_by("-effective_price")
            elif sort == "newest":
                queryset = queryset.order_by("-created_at")

            if user.is_authenticated:
                wishlist = user.wishlist
                queryset = queryset.annotate(
                    is_wishlisted=Exists(
                        WishlistItem.objects.filter(
                            wishlist=wishlist,
                            product_variant__product=OuterRef("pk")
                        )
                    )
                )
            else:
                queryset = queryset.annotate(
                    is_wishlisted=Value(False, output_field=BooleanField())
                )

        return queryset.distinct()
    
    
class ProductVariantViewSet(ModelViewSet):
    serializer_class=ProductVariantSerializer
    permission_classes=[IsAdminOrSellerOrReadOnly]

    def get_queryset(self):
        queryset=ProductVariant.objects.all()
        product_id=self.request.query_params.get("product")
        if product_id:
            queryset=queryset.filter(product_id=product_id)
        return queryset

class WishlistViewSet(ReadOnlyModelViewSet):
    serializer_class=WishlistSerializer
    permission_classes=[IsAdminOrCustomerReadOnly]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    

    
class WishlistItemViewSet(ModelViewSet):
    serializer_class=WishlistitemSerializer
    permission_classes=[IsAdminOrCustomerReadOnly]

    def get_queryset(self):
        wishlist, _ = Wishlist.objects.get_or_create(user=self.request.user)
        return WishlistItem.objects.filter(wishlist=wishlist).select_related("product_variant","product_variant__product")
    
    def perform_create(self, serializer):
        serializer.save(wishlist=self.request.user.wishlist)

    @action(detail=False, methods=["post"])
    def add(self,request):
        variant_id=request.data.get("product_variant")

        if not variant_id:
            return Response({"error": "product_variant is required"},status=400)
        
        wishlist,_=Wishlist.objects.get_or_create(user=request.user)
        product_variant=get_object_or_404(ProductVariant,id=variant_id)

        item,created=WishlistItem.objects.get_or_create(wishlist=wishlist,product_variant=product_variant)

        serializer=self.get_serializer(item)
        return Response(serializer.data,status=201 if created else 200)
    

    @action(detail=False, methods=["post"])
    def remove(self,request):
        variant_id=request.data.get("product_variant")

        if not variant_id:
            return Response(
                {"detail": "product_variant is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        deleted, _ = WishlistItem.objects.filter(
            wishlist__user=request.user,
            product_variant_id=variant_id
        ).delete()

        if deleted == 0:
            return Response(
                {"detail": "Item not found in wishlist"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"detail": "Removed from wishlist"},
            status=status.HTTP_200_OK
        )

class CartViewSet(ModelViewSet):
    serializer_class=CartSerializer
    permission_classes=[IsAdminOrCustomerReadOnly]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=["post"])
    def applycoupon(self, request):
        code = request.data.get("code")

        if not code:
            return Response(
                {"detail": "Coupon code is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart, _ = Cart.objects.get_or_create(user=request.user)

        coupon = Coupon.objects.filter(code__iexact=code, active=True).first()

        if not coupon:
            return Response(
                {"detail": "Invalid coupon"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart.coupon = coupon
        cart.save()

        return Response(
            {"detail": "Coupon applied successfully"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=["post"])
    def removecoupon(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)

        if not cart.coupon:
            return Response(
                {"detail": "No coupon applied"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart.coupon = None
        cart.save()

        return Response(
            {"detail": "Coupon removed successfully"},
            status=status.HTTP_200_OK
        )
    
class CartItemViewSet(ModelViewSet):
    serializer_class=CartItemSerializer
    permission_classes=[IsAdminOrCustomerReadOnly]

    def get_queryset(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart).select_related("product_variant","product_variant__product")
    
    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)

    @action(detail=False,methods=["post"])
    def add(self,request):
        variant_id=request.data.get("product_variant")
        qty=int(request.data.get("quantity",1))

        if not variant_id:
            return Response(
                {"detail": "product_variant is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        product_variant=get_object_or_404(ProductVariant,id=variant_id)

        cart, _ = Cart.objects.get_or_create(user=request.user)


        item,created=CartItem.objects.get_or_create(cart=cart,product_variant=product_variant,defaults={"quantity":qty},)

        if not created:
            item.quantity += qty
            item.save()

        serializer=self.get_serializer(item)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=["post"])
    def remove(self, request):
        variant_id = request.data.get("product_variant")

        if not variant_id:
            return Response(
                {"detail": "product_variant is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        deleted, _ = CartItem.objects.filter(
            cart__user=request.user,
            product_variant_id=variant_id
        ).delete()

        if deleted == 0:
            return Response(
                {"detail": "Item not found in cart"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({"detail": "Removed from cart"})

class OrderViewSet(ReadOnlyModelViewSet):
    serializer_class=OrderSerializer
    permission_classes=[IsAdminOrCustomerReadOnly]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    


class OrderItemViewSet(ReadOnlyModelViewSet):
    serializer_class=OrderItemSerializer
    permission_classes=[IsAdminOrCustomerReadOnly]

    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user).select_related("order","product_variant")
    
class CheckoutView(APIView):
    permission_classes=[IsCustomer]

    @transaction.atomic
    def post(self,request):
        cart=get_object_or_404(Cart,user=request.user)
        cart_items = cart.items.all()

        if not cart_items.exists():
            return Response({"detail":"Cart is empty"},status=status.HTTP_400_BAD_REQUEST)


        total_price = sum(item.total_price for item in cart_items)
        discount = Decimal(0)
        coupon = cart.coupon


        
        if coupon:
            if not coupon.is_valid():
                return Response(
                    {"detail": "Coupon expired or invalid"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if total_price < coupon.min_price:
                return Response(
                    {"detail": f"Minimum order ₹{coupon.min_price} required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if coupon.max_price and total_price > coupon.max_price:
                return Response(
                    {"detail": "Coupon not applicable for this cart"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if coupon.discount_type == "percent":
                discount = (Decimal(coupon.discount_amount) / 100) * total_price
            else:
                discount = Decimal(coupon.discount_amount)

        final_price = total_price - discount

        order=Order.objects.create(user=request.user,coupon=coupon,total_price=total_price,discount_price=discount,final_price=final_price,status="pending")


        for cart_item in cart.items.select_related("product_variant"):
            order_item=OrderItem.objects.create(order=order,product_variant=cart_item.product_variant,quantity=cart_item.quantity,price=cart_item.product_variant.price)

        if coupon:
            coupon.used_count = F("used_count") + 1
            coupon.save(update_fields=["used_count"])


        return Response(
            {
                "message": "Order placed successfully",
                "order_id": order.id,
                "total_price": total_price,
                "discount": discount,
                "final_price": final_price
            },
            status=status.HTTP_201_CREATED
        )
    
class CreatePaymentView(APIView):
    permission_classes = [IsCustomer]

    def post(self, request):
        order = get_object_or_404(
            Order,
            id=request.data.get("order_id"),
            user=request.user,
            status__in=["pending", "failed"]
        )

       
        if order.final_price <= 0:
            return Response({"detail": "Invalid order amount"},status=status.HTTP_400_BAD_REQUEST)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        
        razorpay_order = client.order.create({
            "amount": int(order.final_price),  
            "currency": "INR",
            "payment_capture": 1
        })

        
        order.razorpay_order_id = razorpay_order["id"]
        order.razorpay_payment_id = None
        order.status = "pending"
        order.save(update_fields=["razorpay_order_id", "razorpay_payment_id", "status"])

        PaymentHistory.objects.create(user=request.user,order=order,razorpay_order_id=razorpay_order["id"],amount=order.final_price,   
        )

        return Response({
            "razorpay_order_id": razorpay_order["id"],
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": int(order.final_price),
            "currency": "INR"
        }, status=status.HTTP_200_OK)


class VerifyPaymentView(APIView):
    permission_classes = [IsCustomer]

    @transaction.atomic
    def post(self, request):
        data = request.data

        order = get_object_or_404(
            Order,
            razorpay_order_id=data.get("razorpay_order_id"),
            user=request.user,
            status="pending"
        )

        payment = PaymentHistory.objects.filter(
            razorpay_order_id=order.razorpay_order_id,
            order=order
        ).last()

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        
        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": data.get("razorpay_order_id"),
                "razorpay_payment_id": data.get("razorpay_payment_id"),
                "razorpay_signature": data.get("razorpay_signature"),
            })
        except SignatureVerificationError:
            order.status = "failed"
            order.razorpay_payment_id = data.get("razorpay_payment_id")
            order.save(update_fields=["status", "razorpay_payment_id"])

            payment.status = "failed"
            payment.razorpay_payment_id = data.get("razorpay_payment_id")
            payment.razorpay_signature = data.get("razorpay_signature")
            payment.error_reason = "Signature verification failed"
            payment.save()

            return Response(
                {"detail": "Payment verification failed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        
        expected_amount = int(order.final_price * 100)
        
        order.status = "paid"
        order.razorpay_payment_id = data.get("razorpay_payment_id")
        order.save(update_fields=["status", "razorpay_payment_id"])

        payment.status = "success"
        payment.razorpay_payment_id = data.get("razorpay_payment_id")
        payment.razorpay_signature = data.get("razorpay_signature")
        payment.save()

        
        if order.coupon:
            Coupon.objects.filter(
                id=order.coupon.id
            ).update(used_count=F("used_count") + 1)

        
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.items.all().delete()
            cart.coupon = None
            cart.save(update_fields=["coupon"])

        return Response(
            {"message": "Payment successful"},
            status=status.HTTP_200_OK
        )



class ApplyCouponView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request):
        serializer=CouponApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code=serializer.validated_data["code"]
        # cart_total=serializer.validated_data["cart_total"]

        coupon=get_object_or_404(Coupon,code=code,active=True)
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return Response({"valid": False, "message": "Cart is empty"},status=400)
        
        cart_total=sum(item.total_price for item in cart_items)

        if not coupon.is_valid():
            return Response({"valdid":False ,"message":"coupon expired or usage limit reached"},status=400)
        
        if cart_total < coupon.min_price:
            return Response({"error": f"Minimum order ₹{coupon.min_price} required"},status=400)
        
        if coupon.max_price and cart_total > coupon.max_price:
            return Response({"valid": False, "message": "Coupon not applicable for this price"},status=400)
        
        if coupon.used_count >= coupon.usage_limit:
            return Response({"error": "Coupon usage limit reached"},status=400)
        
        cart.coupon = coupon
        cart.save()

        if coupon.discount_type=="percent":
            discount = (Decimal(coupon.discount_amount) / 100) * cart_total

        else:
            discount = Decimal(coupon.discount_amount)
        
        final_amount=cart_total-discount

        return Response({
            "valid": True,
            "coupon": coupon.code,
            "discount_type": coupon.discount_type,
            "discount": round(discount, 2),
            "final_amount": round(final_amount, 2),
            "message": "Coupon applied successfully"
        })
    

class GetCouponView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,requset):
        cart=get_object_or_404(Cart,user=requset.user)
        cart_items=CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return Response({"message": "Cart is empty", "coupons": []},status=400)
        
        cart_total=sum(item.total_price for item in cart_items)
        today = timezone.now().date()

        coupons = Coupon.objects.filter(
            active=True,
            expires_at__gte=today,
            used_count__lt=F("usage_limit"),
            min_price__lte=cart_total
        ).filter(
            models.Q(max_price__isnull=True) |
            models.Q(max_price__gte=cart_total)
        )

        serializer = GetCouponSerializer(coupons, many=True)

        return Response({
            "cart_total": round(cart_total, 2),
            "available_coupons": serializer.data
        })
    
class RemoveCouponView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = get_object_or_404(Cart, user=request.user)

        if not cart.coupon:
            return Response(
                {"message": "No coupon applied to cart"},
                status=400
            )

        cart.coupon = None
        cart.save(update_fields=["coupon"])

        return Response({
            "message": "Coupon removed successfully",
            "coupon": None
        })
