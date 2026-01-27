from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'Textarea'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'class': 'Input'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'Input'}))
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'Input'}))

    class Meta:
        model = Order
        fields = ['full_name', 'phone', 'city', 'address']