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
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import re_path


router = routers.DefaultRouter()
router.register(r"address", AddressViewSet, basename="address")
router.register(r"category",CategoryViewSet,basename="category")
router.register(r"subcategory",SubcategoryViewSet,basename="subcategory")
router.register(r"product",ProductViewSet,basename="product")
router.register(r"productsvariant",ProductVariantViewSet,basename="productvariant")
router.register(r"wishlist", WishlistViewSet, basename="wishlist")
router.register(r"wishlistitem", WishlistItemViewSet, basename="wishlist-items")
router.register(r"cart", CartViewSet, basename="cart")
router.register(r"cartitem", CartItemViewSet, basename="cartitem")
router.register(r"orderitem", OrderItemViewSet, basename="orderitem")
router.register(r"order", OrderViewSet, basename="order")

schema_view = get_schema_view(
    openapi.Info(
        title="Thekua Ecommerce API",
        default_version='v1',
        description="API documentation for Thekua Ecommerce",
        contact=openapi.Contact(email="admin@momscrunch.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


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
    path("orders/<int:order_id>/products/<int:product_id>/review/", AddReviewsView.as_view(), name="addreview"),
    path("order/<int:order_id>/products/<int:product_id>/reviews/", ProductReviewListView.as_view(), name="productreviews"),
    path("admin/orders/<int:order_id>/status/",ChangeOrderStatusView.as_view()),
    path("customer/orders/<int:order_id>/cancel",CancelOrderView.as_view()),
    path("getcoupon/",GetCouponView.as_view()),


    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0),
            name='schema-json'),

    re_path(r'^swagger/$',
            schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'),

    re_path(r'^redoc/$',
            schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc'),

    path("totalorders/",TotalOrderView.as_view(),name="TotalOrder"),
    path("orderslist/",OrderListView.as_view(),name="OrderListView"),
    path("totalrevenue/",TotalRevenueView.as_view(),name="TotalRevenue"),
    path("todayorders/",TodayOrdersView.as_view(),name="TodayOrders"),
    path("lowstock/",LowStockAlertView.as_view(),name="LowStock"),

    #Seller
    path("products/", ProductListView.as_view()),
    path("seller/orders/",SellerAllOrdersView.as_view()),
    path("seller/pendingorders/",PendingOrderView.as_view()),
    path("seller/shippedorders/",ShippedOrderView.as_view()),
    path("seller/deliveredorders/",DeliveredOrderView.as_view()),
    path("seller/reviews/",SellerProductReviewView.as_view()),

    #Customer
    path("customerer/orders/",CustomerAllOrdersView.as_view()),
    path("customerer/orderscount/",CustomerAllOrdersCountView.as_view()),
    path("customerer/orderdetail/",CustomerOrderDetailView.as_view()),
    path("customerer/pendingorders/",CustomerPendingOrderView.as_view()),
    path("customerer/deliveredorders/",CustomerDeliveredOrderView.as_view()),
    path("customerer/shippedorders/",CustomerShippedOrderView.as_view()),

    # ADMIN
    path("",home,name="homepage"),
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
    path("p/<int:id>",viewproduct,name="viewproduct"),
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
    path('admin/product/image/delete/<int:id>/',delete_product_image,name='delete_product_image'),

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

]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT) 
#hello testing

