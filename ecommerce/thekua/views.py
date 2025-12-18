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
from .permissions import *
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
        return queryset
    
class ProductVariantViewSet(ModelViewSet):
    serializer_class=ProductVariantSerializer
    permission_classes=[IsAdminOrSeller]

    def get_queryset(self):
        queryset=ProductVariant.objects.all()
        product_id=self.request.query_params.get("product")
        if product_id:
            queryset=queryset.filter(product_id=product_id)
        return queryset

class WishlistViewSet(ModelViewSet):
    serializer_class=WishlistSerializer
    permission_classes=[IsAdminorCustomer]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)