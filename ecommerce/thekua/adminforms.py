from .models import *
from django.forms import ModelForm

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
        fields="__all__"
