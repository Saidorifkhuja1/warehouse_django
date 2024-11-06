from django import forms
from .models import Warehouse, Category

class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'address', 'phone_number', 'description']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'warehouse']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get user from kwargs
        super().__init__(*args, **kwargs)

        if user and user.is_admin:
            # Admins can see their own warehouses
            self.fields['warehouse'].queryset = Warehouse.objects.filter(owner=user)
        elif user:
            # Non-admin users can see warehouses created by their admin
            self.fields['warehouse'].queryset = Warehouse.objects.filter(owner=user.owner)