from django import forms
from .models import Good


class GoodForm(forms.ModelForm):
    class Meta:
        model = Good
        fields = ['name', 'brand', 'description', 'price', 'dates', 'cover_image']  

