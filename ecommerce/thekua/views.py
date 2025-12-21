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


# Create your views here.

class SignupRequestAPIView(APIView):
    def post(self,request):
        serializer=SignupRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) #runs validate()
        pending_user=serializer.save() #calls create()
        #creates PendingUser
        return Response({"message": "OTP sent successfully","session_id": str(pending_user.session_id)},status=status.HTTP_200_OK)
    

class OTPVerifyAPIView(APIView):
    def post(self,request):
        serializer=OTPVerifySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):# if is_valid passed than every data get stored in serializer.validated_data and when we call serializer.save() drf passes that data into create(self, validated_data)
            serializer.save()

            return Response({"message": "User created successfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginAPIView(APIView):
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
    # queryset=Product.objects.all()
    # serializer_class=ProductSerializer
    permission_classes=[IsAdminOrSeller]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def get_queryset(self):
        queryset = Product.objects.prefetch_related("productvariants")
        
        subCategory_id=self.request.query_params.get("subcategory")
        if subCategory_id:
            queryset=queryset.filter(subCategory_id=subCategory_id)
        
        user = self.request.user
        if not user.is_authenticated:
            return queryset.annotate(
                is_wishlisted=Value(False, output_field=BooleanField())
            )
        
        wishlist = user.wishlist

        return queryset.annotate(
            is_wishlisted=Exists(
                WishlistItem.objects.filter(
                    wishlist=wishlist,
                    product_variant__product=OuterRef("pk")
                )
            )
        )
    
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
