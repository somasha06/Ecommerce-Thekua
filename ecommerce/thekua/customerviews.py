from .models import *
from django.shortcuts import render,redirect,get_object_or_404
from .customerforms import *
from django.contrib.auth import login


def customerbase(request):
    return render(request,"user/customerbase.html")

# def customerwishlist(request):
#     return render(request,"user/customerwishlist.html")

def customerwishlistitem(request):
    user=request.user
    wishlistitem=WishlistItem.objects.filter(wishlist__user=user).select_related("product_variant", "product_variant__product")
    return render(request,"user/customerwishlistitem.html",{"user":user,"wishlistitem":wishlistitem})

def customerorder(request):
    user=request.user
    orders=Order.objects.filter(user=user)
    return render(request,"user/customerorder.html",{"user":user,"orders":orders})

def customerorderitem(request,id):
    order=get_object_or_404(Order,id=id,user=request.user)
    orderitem=OrderItem.objects.filter(order=order).select_related("product_variant","product_variant__product")
    return render(request,"user/customerorderitem.html",{"order":order,"orderitem":orderitem})

def customercartitem(request):
    user=request.user
    cartitem=CartItem.objects.filter(cart__user=user).select_related("product_variant","product_variant__product")
    return render(request,"user/customercartitem.html",{"user":user,"cartitem":cartitem})

def signup(request):
    if request.method=="POST":
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request,"registration/signup.html",{"error": "Username already exists"})
        
        user=User.objects.create_user(username=username,email=email,password=password)

        login(request,user)
        return redirect(customerbase)
    
    return render(request,"auth/signup.html")