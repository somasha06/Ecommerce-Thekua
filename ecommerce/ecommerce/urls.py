from django.contrib import admin
from django.contrib.auth import authenticate,logout
from django.urls import path,include
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from thekua.views import *
from thekua.adminviews import *
from thekua.customerviews import *
from django.contrib.auth import views as auth_views


router = routers.DefaultRouter()
router.register(r"address", AddressViewSet, basename="address")
router.register(r"category",CategoryViewSet,basename="category")
router.register(r"subcategory",SubcategoryViewSet,basename="subcategory")
router.register(r"product",ProductViewSet,basename="product")
router.register(r"productsvariant",ProductVariantViewSet,basename="productvariant")
# router.register(r"wishlist",WishlistViewSet,basename="wishlist")
router.register(r"wishlist", WishlistViewSet, basename="wishlist")
router.register(r"wishlistitem", WishlistItemViewSet, basename="wishlist-items")
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
    path("createpayment/", CreatePaymentView.as_view()),
    path("verifypayment/", VerifyPaymentView.as_view()),
    path("customer/profile/", CustomerProfileUpdateView.as_view()),
    path("cart/applycoupon/", ApplyCouponView.as_view(), name="apply-coupon"),
    path("cart/removecoupon/", RemoveCouponView.as_view()),

    path("getcoupon/",GetCouponView.as_view()),

    path("",home,name="homepage"),
    path("p/<int:id>",viewproduct,name="viewproduct"),
    path("admin/",dashboard,name="dashboardpage"),
    path("admin/category",managecategory,name="managecategory"),
    path("admin/category/<int:id>/",deletecategory,name="deletecategory"),
    path("admin/subcategory",managesubcategory,name="managesubcategory"),
    path("admin/subcategory/<int:id>/",deletesubcategory,name="deletesubcategory"),
    path("admin/product",insertproduct,name="insertproduct"),
    path("admin/productvariant",insertproductvariant,name="insertproductvariant"),
    path("admin/product/<int:id>/",deleteproduct,name="deleteproduct"),
    path("admin/productvariant/<int:id>/",deleteproductvariant,name="deleteproductvariant"),
    path("admin/manageproduct",manageproduct,name="manageproduct"),
    path("admin/manageproductvariant",manageproductvariant,name="manageproductvariant"),

    path("admin/customer", allcustomer, name="allcustomer"),
    path("admin/customer/<int:id>/",viewcustomerprofile,name="viewcustomerprofile"),
    path("admin/customer/<int:id>/wishlist/",viewcustomerwishlist, name="viewcustomerwishlist"),
    path("admin/customer/<int:id>/cart/",viewcustomercart, name="viewcustomercart"),
    path("admin/customer/<int:id>/orders/",viewcustomerorder, name="viewcustomerorder"),
    path("admin/customerorder/<int:id>/items/",viewcustomerorderitems,name="viewcustomerorderitems"),
    path("admin/customerorders/totalorders/",totalorders, name="totalorders"),

    path("admin/storeprofile",storeprofile,name="storeprofile"),
    path("about/",about, name="about"),
    path("admin/category/<int:id>/edit/", editcategory, name="editcategory"),
    path("admin/subcategory/<int:id>/edit/", editsubcategory, name="editsubcategory"),
    path("admin/product/<int:id>/edit/", editproduct, name="editproduct"),
    path("admin/productvariant/<int:id>/edit/", editproductvariant, name="editproductvariant"),

    # path("auth/",include("django.contrib.auth.urls")),
    path("customer/",customerbase,name="customerbase"),
    # path("customer/wishlist/",customerwishlist,name="customerwishlist"),
    path("customer/wishlistitem/",customerwishlistitem,name="customerwishlistitem"),
    path("customer/order/",customerorder,name="customerorder"),
    path("customer/<int:id>/orderitem/",customerorderitem,name="customerorderitem"),
    path("customer/cartitem/",customercartitem,name="customercartitem"),
    # path("auth/login/",login,name="login"),
    # path("auth/logout/",logout,name="logout"),
    # path("auth/signup/",signup,name="signup"),

]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)

#hello testing

