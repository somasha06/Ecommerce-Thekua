from .models import *
from django.shortcuts import render,redirect,get_object_or_404
from .adminforms import *

def home(request):
    subcategories=SubCategory.objects.all()
    products=Product.objects.all()
    return render(request,"home.html",{"subcategories":subcategories,"products":products})

def viewproduct(request,id):
    product=Product.objects.get(id=id)
    subcategories=SubCategory.objects.all()
    return render(request,"view_product.html",{"product":product,"subcategories":subcategories})

def dashboard(request):
    return render(request,"admin/dashboard.html")

def managecategory(request):
    form=Categoryform(request.POST or None)
    categories=Category.objects.all()
    if request.method=="POST":
        if form.is_valid():
            form.save()
            return redirect(managecategory)
    return render(request,"admin/managecategory.html",{"form":form,"categories":categories})

def deletecategory(request,id):
    deletedcategory=Category.objects.get(id=id)
    deletedcategory.delete()
    return redirect(managecategory)

def managesubcategory(request):
    form=Subcategoryform(request.POST or None , request.FILES or None)
    subcategories=SubCategory.objects.all()
    if request.method=="POST":
        if form.is_valid():
            form.save()
            return redirect(managesubcategory)
    return render(request,"admin/managesubcategory.html",{"form":form,"subcategories":subcategories})

def deletesubcategory(request,id):
    deletedcategory=SubCategory.objects.get(id=id)
    deletedcategory.delete()
    return redirect(managesubcategory)

def insertproduct(request):
    form=Productform(request.POST or None,request.FILES or None)
    if request.method=="POST":
        if form.is_valid():
            form.save()
            return redirect(manageproduct)
    return render(request,"admin/insertproduct.html",{"form":form})

def manageproduct(request):
    products=Product.objects.all()
    return render(request,"admin/manageproduct.html",{"products":products})

def deleteproduct(request,id):
    deletedproduct=Product.objects.get(id=id)
    deletedproduct.delete()
    return redirect(manageproduct)



def allcustomer(request):
    customers=Role.objects.filter(role=Role.CUSTOMER).select_related("user")
    
    for customer in customers:
        customer.wishlist_count = WishlistItem.objects.filter(
            wishlist__user=customer.user
        ).count()


        customer.order_count = Order.objects.filter(
            user=customer.user
        ).count()


    return render(request,"admin/viewcustomer.html",{"customers":customers})

def allseller(request):
    sellers=Role.objects.filter(role=Role.SELLER).select_related("user")
    return render(request,"admin/viewseller.html",{"sellers":sellers})


def customerwishlist(request,user_id):
    user=get_object_or_404(User,id=user_id)
    wishlistitem=WishlistItem.objects.filter(wishlist__user=user).select_related("product_variant", "product_variant__product")
    return render(request,"admin/customerwishlist.html",{"user":user,"wishlistitems":wishlistitem})



def customerorder(request,user_id):
    user=get_object_or_404(User,id=user_id)
    orders=Order.objects.filter(user=user).order_by("-created_at")
    return render(request,"admin/customerorder.html",{"user":user,"orders":orders})

def orderitems(request,order_id):
    order=get_object_or_404(Order,id=order_id)

    items=OrderItem.objects.filter(order=order).select_related("product_variant","product_variant__product")
    return render(request,"admin/orderitems.html",{"order":order,"items":items})

def paidorders(request):
    orders=Order.objects.filter(status="PAID").order_by("-created_at")
    return render(request,"admin/paidorder.html",{"orders":orders})