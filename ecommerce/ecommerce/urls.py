"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from thekua.views import *
from thekua.adminviews import *

router = routers.DefaultRouter()
router.register(r"address", AddressViewSet, basename="address")
router.register(r"categories",CategoryViewSet,basename="category")
router.register(r"subcategories",SubcategoryViewSet,basename="subcategory")
router.register(r"products",ProductViewSet,basename="product")
router.register(r"productsvariants",ProductVariantViewSet,basename="productvariant")
# router.register(r"wishlist",WishlistViewSet,basename="wishlist")
router.register(r"wishlists", WishlistViewSet, basename="wishlist")
router.register(r"wishlistitems", WishlistItemViewSet, basename="wishlist-items")
router.register(r"cart", CartViewSet, basename="cart")
router.register(r"cartitem", CartItemViewSet, basename="cartitem")
router.register(r"orderitem", OrderItemViewSet, basename="orderitem")
router.register(r"order", OrderViewSet, basename="order")


urlpatterns = [
    path('superadmin/', admin.site.urls),
    # path("", include("thekua.urls")),
    path('api-auth/', include('rest_framework.urls')),
    path("api/", include(router.urls)),
    path("signup/", SignupRequestAPIView.as_view()),
    path("verify-otp/", OTPVerifyAPIView.as_view()),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("payment/create/", CreatePaymentView.as_view()),
    path("payment/verify/", VerifyPaymentView.as_view()),

    path("",home,name="homepage"),
    path("p/<int:id>",viewproduct,name="viewproduct"),
    path("admin/",dashboard,name="dashboardpage"),
    path("admin/category",managecategory,name="managecategory"),
    path("admin/category/<int:id>/",deletecategory,name="deletecategory"),
    path("admin/subcategory",managesubcategory,name="managesubcategory"),
    path("admin/subcategory/<int:id>/",deletesubcategory,name="deletesubcategory"),
    path("admin/product",insertproduct,name="insertproduct"),
    path("admin/product/<int:id>/",deleteproduct,name="deleteproduct"),
    path("admin/manageproduct",manageproduct,name="manageproduct"),
    path("admin/seller",allseller,name="allseller"),
    path("admin/customer", allcustomer, name="allcustomer"),
    path("admin/customer/<int:user_id>/wishlist/",customerwishlist, name="customerwishlist"),
    path("admin/customer/<int:user_id>/orders/",customerorder, name="customerorder"),
    path("admin/order/<int:order_id>/items/",orderitems,name="orderitems"),
    path("admin/orders/paid/",paidorders, name="paidorders"),

]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)

#hello testing

