from django import forms
from .models import Product
from warehouse.models import Category

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





class ProductUpdateForm(forms.ModelForm):
    sold_amount = forms.IntegerField(required=False, min_value=1)

    class Meta:
        model = Product
        fields = ['name', 'cost', 'amount', 'description', 'note', 'status', 'category']

    def clean(self):
        cleaned_data = super().clean()
        sold_amount = cleaned_data.get('sold_amount')
        current_amount = self.instance.amount if self.instance else 0

        if sold_amount and sold_amount > current_amount:
            raise forms.ValidationError("Cannot sell more than available amount")

        return cleaned_data