from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from .models import *
from rest_framework.viewsets import ModelViewSet
from django.db.models import Exists, OuterRef, BooleanField, Value
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from .permissions import *
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.permissions import AllowAny
from django.db.models import Q,Min
from decimal import Decimal, InvalidOperation
from django.db.models.functions import Coalesce
import razorpay
from razorpay.errors import SignatureVerificationError


class SignupRequestAPIView(APIView):
    authentication_classes = [] 
    permission_classes = [AllowAny]
    
    def post(self,request):
        print("hit")
        serializer=SignupRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) #runs validate()
        pending_user=serializer.save() #calls create()
        #creates PendingUser
        return Response({"message": "OTP sent successfully","session_id": str(pending_user.session_id)},status=status.HTTP_200_OK)
    

class OTPVerifyAPIView(APIView):
    authentication_classes = [] 
    permission_classes = [AllowAny]

    def post(self,request):
        serializer=OTPVerifySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):# if is_valid passed than every data get stored in serializer.validated_data and when we call serializer.save() drf passes that data into create(self, validated_data)
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


class CategoryViewSet(ModelViewSet):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer
    permission_classes=[IsAdminOrSeller]
    
class SubcategoryViewSet(ModelViewSet):
    # queryset=SubCategory.objects.all()
    serializer_class=SubCategorySeializer
    permission_classes=[IsAdminOrSeller]

    def get_queryset(self):
        queryset=SubCategory.objects.all()

        category_id=self.request.query_params.get("category")
        if category_id:
            queryset=queryset.filter(category_id=category_id)
        return queryset
    
class ProductViewSet(ModelViewSet):
    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrSeller()]
        return []

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def get_queryset(self):
        queryset = Product.objects.prefetch_related("productvariants")
        user=self.request.user

        if self.action in ["list", "retrieve"]:
            queryset = queryset.filter(is_active=True)

            search = self.request.query_params.get("search") # it's just if the url has key search than store it in search
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

            # ↕ Sorting
            if sort == "price_low":
                queryset = queryset.order_by("effective_price")
            elif sort == "price_high":
                queryset = queryset.order_by("-effective_price")
            elif sort == "newest":
                queryset = queryset.order_by("-created_at")

            if user.is_authenticated:
                wishlist = user.wishlist
                queryset = queryset.annotate( #annotate=It only adds extra information to the query result.
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
    permission_classes=[IsAdminOrSeller]

    def get_queryset(self):
        queryset=ProductVariant.objects.all()
        product_id=self.request.query_params.get("product")
        if product_id:
            queryset=queryset.filter(product_id=product_id)
        return queryset

class WishlistViewSet(ReadOnlyModelViewSet):
    serializer_class=WishlistSerializer
    permission_classes=[IsCustomer]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    
    # def perform_create(self, serializer):
    #     wishlist = self.request.user.wishlist
    #     serializer.save(user=self.request.user)

    # def my_wishlist(self,request):
    #     wishlist,_=Wishlist.objects.get_or_create(user=request.user)
    #     serializer=self.get_serializer(wishlist)
    #     return Response(serializer.data)
    
class WishlistItemViewSet(ModelViewSet):
    serializer_class=WishlistitemSerializer
    permission_classes=[IsCustomer]

    def get_queryset(self):
        return WishlistItem.objects.filter(wishlist__user=self.request.user).select_related("product_variant","product_variant__product")#To filter through relations → use __
    
    def perform_create(self, serializer):
        # wishlist,_=Wishlist.objects.get_or_create(user=self.request.user)
        serializer.save(wishlist=self.request.user.wishlist)

    @action(detail=False, methods=["post"])
    def add(self,request):
        variant_id=request.data.get("product_variant")

        if not variant_id:
            return Response({"error": "product_variant is required"},status=400)
        
        # wishlist,_=Wishlist.objects.get_or_create(user=request.user)
        product_variant=get_object_or_404(ProductVariant,id=variant_id)

        item,created=WishlistItem.objects.get_or_create(wishlist=request.user.wishlist,product_variant=product_variant)

        serializer=self.get_serializer(item)
        return Response(serializer.data,status=201 if created else 200)
    

    @action(detail=False, methods=["post"]) #Custom endpoints require @action
    def remove(self,request):
        variant_id=request.data.get("product_variant")

        # WishlistItem.objects.filter(Wishlist_user=request.user,product_variant_id=variant_id).delete()

       
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

class CartViewSet(ReadOnlyModelViewSet):
    serializer_class=CartSerializer
    permission_classes=[IsCustomer]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
class CartItemViewSet(ModelViewSet):
    serializer_class=CartItemSerializer
    permission_classes=[IsCustomer]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user).select_related("product_variant","product_variant__product")
    
    def perform_create(self, serializer):
        # cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=self.request.user)

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
    permission_classes=[IsCustomer]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    # def perform_create(self,serializer):
    #     serializer.save(user=self.request.user)

class OrderItemViewSet(ReadOnlyModelViewSet):
    serializer_class=OrderItemSerializer
    permission_classes=[IsCustomer]

    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user).select_related("order","product_variant")
    
class CheckoutView(APIView):
    permission_classes=[IsCustomer]

    @transaction.atomic
    def post(self,request):
        cart=get_object_or_404(Cart,user=request.user)

        if not cart.items.exists():
            return Response({"detail":"Cart is empty"},status=status.HTTP_400_BAD_REQUEST)

        order=Order.objects.create(user=request.user)

        total_price=0

        #cart.items → all items
        #cart_item → one item from that list

        for cart_item in cart.items.select_related("product_variant"):    #“cart.items=All CartItem objects that belong to this cart” select_related=When fetching CartItem, also fetch the related ProductVariant in the SAME query
            order_item=OrderItem.objects.create(order=order,product_variant=cart_item.product_variant,quantity=cart_item.quantity,price=cart_item.product_variant.price)
                                #left order=field name from orderitem | right order=variable above defined order=order means Set the order_id of this OrderItem to the ID of the Order we just created
            total_price +=(
                order_item.quantity*order_item.price
            )

        order.total_price=total_price
        order.save()

        # cart.items.all().delete()

        return Response(
            {
                "message": "Order placed successfully",
                "order_id": order.id,
                "total_price": total_price
            },
            status=status.HTTP_201_CREATED
        )
    
#A user first has a Cart, and inside the cart there are CartItems that store all the selected products and quantities.

# When the user clicks Checkout, the backend creates an Order, and all the cart items are copied into OrderItems inside that order.

#After the order and order items are created, the user proceeds to payment.

#Once the payment is successful, the order is confirmed, and the user can see it in My Orders.



    
class CreatePaymentView(APIView):
    permission_classes=[IsCustomer]

    def post(self,request):
        order=get_object_or_404(Order,id=request.data.get("order_id"),user=request.user,status__in=["pending","failed"])

        client=razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))

        razorpay_order=client.order.create(
            {
               "amount": int(order.total_price * 100),  # paise
                "currency": "INR",
                "payment_capture": 1 
            }
        )

        order.razorpay_order_id=razorpay_order["id"]
        order.razorpay_payment_id=None
        order.status="pending"
        order.save()

        PaymentHistory.objects.create(
            user=request.user,
            order=order,
            razorpay_order_id=razorpay_order["id"],
            amount=order.total_price,
            status="created"
        )

        return Response({
            "razorpay_order_id": razorpay_order["id"],
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": int(order.total_price * 100),
            "currency": "INR"
        }, status=status.HTTP_200_OK)


class VerifyPaymentView(APIView):
    permission_classes=[IsCustomer]

    def post(self,request):
        data=request.data

        order=get_object_or_404(Order,razorpay_order_id=data.get("razorpay_order_id"),user=request.user,status="pending")

        payment = PaymentHistory.objects.filter(
            razorpay_order_id=data.get("razorpay_order_id"),
            order=order
        ).last()

        client=razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))

        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": data.get("razorpay_order_id"),
                "razorpay_payment_id": data.get("razorpay_payment_id"),
                "razorpay_signature": data.get("razorpay_signature"),
            })

        except SignatureVerificationError:
            order.status="failed"
            order.razorpay_payment_id = data.get("razorpay_payment_id")
            order.save()

            payment.status = "failed"
            payment.razorpay_payment_id = data.get("razorpay_payment_id")
            payment.razorpay_signature = data.get("razorpay_signature")
            payment.error_reason = "Signature verification failed"
            payment.save()

            return Response(
                {"detail": "Payment failed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        

        #success
        order.status="paid"
        order.razorpay_payment_id=data.get("razorpay_payment_id")
        order.save()

        payment.status = "success"
        payment.razorpay_payment_id = data.get("razorpay_payment_id")
        payment.razorpay_signature = data.get("razorpay_signature")
        payment.save()

        CartItem.objects.filter(cart__user=request.user).delete()

        return Response({"message":"Payment successful"},status=status.HTTP_200_OK)
    

