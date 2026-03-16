from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Inventory

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
class InventoryForm(forms.ModelForm):
    
    ingredient_name = forms.CharField(
        label="Ingredient Name", 
        max_length=128, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Tomato'})
    )
    unit = forms.CharField(
        label="Unit", 
        max_length=16, 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. pcs, g, ml'})
    )
    field_order = ['ingredient_name', 'unit', 'quantity', 'purchase_date', 'expiry_date']

    class Meta:
        model = Inventory
    
        fields = ['quantity', 'purchase_date', 'expiry_date']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['ingredient_name'].initial = self.instance.ingredient.name
            self.fields['ingredient_name'].widget.attrs['readonly'] = True
            self.fields['unit'].initial = self.instance.ingredient.unit
            self.fields['unit'].widget.attrs['readonly'] = True    


