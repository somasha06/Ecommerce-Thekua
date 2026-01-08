from .models import *
from django.forms import ModelForm,ImageField,FileInput

class Categoryform(ModelForm):
    class Meta:
        model=Category
        fields="__all__"

class Subcategoryform(ModelForm):
    class Meta:
        model=SubCategory
        fields="__all__"

class Productform(ModelForm):
    class Meta:
        model=Product
        exclude = ["seller", "slug"]

class Productvariantform(ModelForm):
    class Meta:
        model=ProductVariant
        fields="__all__"

class StoreProfileForm(ModelForm):
    class Meta:
        model = StoreProfile
        fields = "__all__"


