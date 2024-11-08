from django import forms
from .models import Product
from warehouse.models import Category,Warehouse

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'cost', 'amount', 'description', 'note', 'status', 'category']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Retrieve user from kwargs
        super().__init__(*args, **kwargs)

        if user and user.is_admin:
            # Admins can see only categories they created
            self.fields['category'].queryset = Category.objects.filter(warehouse__owner=user)
        elif user:
            # Workers and other users can see only categories created by their admin
            self.fields['category'].queryset = Category.objects.filter(warehouse__owner=user.owner)


class ProductForm2(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'cost', 'amount', 'description', 'note', 'status', 'category']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        warehouse_id = kwargs.pop('warehouse_id', None)  # Get warehouse_id from kwargs
        super().__init__(*args, **kwargs)

        if user and user.is_admin:
            if warehouse_id:
                # Filter categories by the specific warehouse
                self.fields['category'].queryset = Category.objects.filter(warehouse_id=warehouse_id)
            else:
                self.fields['category'].queryset = Category.objects.none()
