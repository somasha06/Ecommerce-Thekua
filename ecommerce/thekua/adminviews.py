from .models import *
from django.shortcuts import render,redirect,get_object_or_404
from .adminforms import *
from .decorators import admin_or_seller_required
from .permissions import *
from django.db.models import Count, Sum, Max

# from .utils import *


def home(request):
    subcategories=SubCategory.objects.all()
    products=Product.objects.all()
    return render(request,"home.html",{"subcategories":subcategories,"products":products})

def viewproduct(request,id):
    product=Product.objects.get(id=id)
    productvariants=product.productvariants.filter(is_active=True)
    default_variant = productvariants.first()
    profile = StoreProfile.objects.first()
    images = product.images.all()   


    subcategories=SubCategory.objects.all()
    return render(request,"view_product.html",{"product":product,"subcategories":subcategories,"productvariants":productvariants,"default_variant":default_variant,"profile":profile,"images":images})

def dashboard(request):
    count={
        "customers":Role.objects.filter(role=Role.CUSTOMER).count(),
        "product":Product.objects.count(),
        "order":Order.objects.count(),
    }
    return render(request,"admin/dashboard.html",count)

# @admin_or_seller_required
def managecategory(request):
    form=Categoryform(request.POST or None,request.FILES or None)
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

def editcategory(request,id):
    category=get_object_or_404(Category,id=id)
    form=Categoryform(request.POST or None,request.FILES or None,instance=category )
    if request.method=="POST":
        if form.is_valid():
            form.save()
            return redirect(managecategory)
    return render(request,"admin/editcategory.html",{"category":category,"form":form})
        

# @admin_or_seller_required
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

def editsubcategory(request,id):
    subcategory=SubCategory.objects.get(id=id)
    form=Subcategoryform(request.POST or None,request.FILES or None,instance=subcategory)
    if request.method=="POST":
        if form.is_valid():
            form.save()
            return redirect(managesubcategory)
    return render(request,"admin/editsubcategory.html",{"subcategory":subcategory,"form":form})

# @admin_or_seller_required
def insertproduct(request):
    form=Productform(request.POST or None)
    files=request.FILES.getlist("productimages")

    if request.method=="POST":
        if form.is_valid():
            product=form.save(commit=False)
            product.seller=User.objects.filter(roles__role="seller",is_active=True).first()
            product.seller=request.user
            product.save()
            for file in files:
                Productimage.objects.create(product=product,productimages=file)
            
            return redirect(manageproduct)
    return render(request,"admin/insertproduct.html",{"form":form})

# @admin_or_seller_required
def manageproduct(request):
    products=Product.objects.all()
    return render(request,"admin/manageproduct.html",{"products":products})

def deleteproduct(request,id):
    deletedproduct=Product.objects.get(id=id)
    deletedproduct.delete()
    return redirect(manageproduct)


def editproduct(request,id):
    product=Product.objects.get(id=id)
    files=request.FILES.getlist("productimages")

    form=Productform(request.POST or None,request.FILES or None,instance=product)
    if request.method=="POST":
        if form.is_valid():
            form.save()
            for file in files:
                Productimage.objects.create(product=product,productimages=file)
            return redirect(manageproduct)
    images=product.images.all()
    return render(request,"admin/editproduct.html",{"product":product,"form":form,"images":images})

def allcustomer(request):
    customers=Role.objects.filter(role=Role.CUSTOMER).select_related("user").annotate(
        wishlist_count=Count("user__wishlist__wishlistitem", distinct=True),
            order_count=Count("user__orders", distinct=True),
            total_spent=Sum("user__orders__total_price"),
            last_order=Max("user__orders__created_at"),
    )
    

    return render(request,"admin/viewcustomer.html",{"customers":customers})

def viewcustomerprofile(request,id):
    user=get_object_or_404(User,id=id)
    orders=Order.objects.filter(user=user)
    wishlistitems=WishlistItem.objects.filter(wishlist__user=user)
    cartitems=CartItem.objects.filter(cart__user=user)
    addresses = user.address.all()  # related_name="address"

    context={
        "customer":user,
        "addresses": addresses,
        "ordercount":orders.count(),
        "wishlistcount":wishlistitems.count(),
        "cartcount":cartitems.count(),
    }

    return render(request,"admin/viewcustomerprofile.html",context)


def viewcustomerwishlist(request,id):
    user=get_object_or_404(User,id=id)
    wishlistitem=WishlistItem.objects.filter(wishlist__user=user).select_related("product_variant", "product_variant__product")
    return render(request,"admin/viewcustomerwishlist.html",{"user":user,"wishlistitem":wishlistitem})

def viewcustomercart(request,id):
    user=get_object_or_404(User,id=id)
    cartitems=CartItem.objects.filter(cart__user=user).select_related("product_variant", "product_variant__product")

    return render(request,"admin/viewcustomercart.html",{"user":user,"cartitems":cartitems})

def viewcustomerorder(request,id):
    user=get_object_or_404(User,id=id)
    orders=Order.objects.filter(user=user).select_related("user").order_by("-created_at")
    return render(request,"admin/viewcustomerorder.html",{"user":user,"orders":orders})

def viewcustomerorderitems(request,order_id):
    order=get_object_or_404(Order,id=order_id)

    items=OrderItem.objects.filter(order=order).select_related("product_variant","product_variant__product")
    return render(request,"admin/viewcustomerorderitems.html",{"order":order,"items":items})

def paidorders(request):
    
    paidorders=Order.objects.filter(status="success").order_by("-created_at")
    pendingorders=Order.objects.filter(status="failed").order_by("-created_at")

    return render(request,"admin/paidorder.html",{"paidorders":paidorders,"pendingorders":pendingorders})

def insertproductvariant(request):
    form=Productvariantform(request.POST or None, request.FILES or None)
    if request.method=="POST":
        if form.is_valid():
            form.save()
            return redirect(manageproductvariant)
    return render(request,"admin/insertproductvariant.html",{"form":form})

def manageproductvariant(request):
    variants=ProductVariant.objects.all()
    return render(request,"admin/manageproductvariant.html",{"variants":variants})

def deleteproductvariant(request,id):
    remove=ProductVariant.objects.get(id=id)
    remove.delete()
    return redirect(manageproductvariant)

def editproductvariant(request,id):
    productvariant=ProductVariant.objects.get(id=id)
    form=Productvariantform(request.POST or None,request.FILES or None,instance=productvariant)
    if request.method=="POST":
        if form.is_valid():
            form.save()
            return redirect(manageproductvariant)
    return render(request,"admin/editproductvariant.html",{"productvariant":productvariant,"form":form})

def storeprofile(request):
    profile,created=StoreProfile.objects.get_or_create(id=1)

    form=StoreProfileForm(request.POST or None,request.FILES or None,instance=profile)

    if request.method=="POST":
        if form.is_valid():
            form.save()
            return redirect("storeprofile")
        
    return render(request,"admin/storeprofile.html",{"form":form,"profile":profile})

def about(request):
    profile = StoreProfile.objects.get(id=1)
    return render(request, "about.html", {"profile": profile})

def deleteproductimage(requset,image_id):
    images=get_object_or_404(Productimage,id=image_id)
    product_id=images.product.id
    if requset.method=="POST":
        images.delete()
    return redirect("editproduct",id=product_id)