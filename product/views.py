from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import *
from .forms import *
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse




class ProductCreateView(CreateView):
    model = Product
    fields = ['name', 'cost', 'amount', 'description', 'note', 'status', 'category']
    template_name = 'product/product_create.html'

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)

        # Get the current user
        user = self.request.user

        # Find warehouses created by the user or the user's creator
        user_warehouses = Warehouse.objects.filter(
            owner__in=[user, user.created_by]
        )

        # Filter categories based on these warehouses
        form.fields['category'].queryset = Category.objects.filter(
            warehouse__in=user_warehouses
        )

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category, pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        # Redirect to the product list or a specific page after successful creation
        return reverse('product_list', kwargs={'pk': self.kwargs['pk']})


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        # Get the category by pk from the URL
        category = get_object_or_404(Category, pk=self.kwargs['pk'])
        # Filter products by the retrieved category and order by the created_at field in descending order
        return Product.objects.filter(category=category).order_by('-add_time')  # Assuming 'created_at' is the field for creation date

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the category to the context to display it in the template if needed
        context['category'] = get_object_or_404(Category, pk=self.kwargs['pk'])
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retrieve the category associated with the product and pass it to the context
        context['category'] = self.object.category
        return context

from django.core.exceptions import ValidationError

class SellProductView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/sell_product.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        # Fetch the product object that is being updated
        product = get_object_or_404(Product, pk=self.kwargs['pk'])
        return product

    def form_valid(self, form):
        # Retrieve the product object and the amount entered in the form
        product = self.get_object()
        entered_amount = form.cleaned_data['amount']
        new_status = form.cleaned_data['status']

        # Validate that the entered amount is not greater than the current amount
        if entered_amount > product.amount:
            form.add_error('amount', 'You cannot enter an amount greater than the current amount.')
            return self.form_invalid(form)

        # Calculate the new amount by subtracting the entered amount
        new_amount = product.amount - entered_amount

        # Check if the status is changing to 'sotildi'
        if new_status == 'sotildi':
            # Create a new SoldProduct with the amount sold
            SoldProduct.objects.create(
                name=product.name,
                cost=product.cost,
                amount=entered_amount,
                note=product.note,
                status='sotildi',
                category=product.category
            )

            # Update the product's amount to the calculated new amount
            product.amount = new_amount
            if new_amount == 0:
                # If all of the amount is sold, delete the product
                product.delete()
            else:
                # If some amount remains, reset the status to 'yangi'
                product.status = 'yangi'
                product.save()
        else:
            # If status is not 'sotildi', just update the amount
            product.amount = new_amount
            product.save()

        messages.success(self.request, "Product updated successfully.")
        return redirect(self.get_success_url())

    def get_success_url(self):
        # Redirect to the product list for the current product's category
        return reverse('product_list', kwargs={'pk': self.object.category.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.object.category  # Pass the category of the current product
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user

        if user.is_admin:
            form.fields['category'].queryset = Category.objects.filter(warehouse__owner=user)
            if user.created_by:
                form.fields['category'].queryset |= Category.objects.filter(
                    warehouse__owner__in=user.created_by.get_admins()
                )
        else:
            form.fields['category'].queryset = Category.objects.filter(warehouse__owner=user.created_by)

        return form


class SoldProductListView(LoginRequiredMixin, ListView):
    model = SoldProduct
    template_name = 'product/sold_product_list.html'
    context_object_name = 'sold_products'

    def get_queryset(self):
        # Get the category by pk from the URL
        category = get_object_or_404(Category, pk=self.kwargs['pk'])
        # Filter products by the retrieved category and order by the created_at field in descending order
        return SoldProduct.objects.filter(category=category).order_by('-add_time')  # Assuming 'created_at' is the field for creation date

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the category to the context to display it in the template if needed
        context['category'] = get_object_or_404(Category, pk=self.kwargs['pk'])
        return context



class ProductUpdateView(UpdateView):
    model = Product
    fields = ['name', 'cost', 'amount', 'description', 'note', 'status', 'category']
    template_name = 'product/product_update.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        # Fetch the specific product being updated based on the primary key (pk)
        return get_object_or_404(Product, pk=self.kwargs['pk'])

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)

        # Get the current user
        user = self.request.user

        # Find warehouses created by the user or the user's creator
        user_warehouses = Warehouse.objects.filter(
            owner__in=[user, user.created_by]
        )

        # Filter categories based on these warehouses
        form.fields['category'].queryset = Category.objects.filter(
            warehouse__in=user_warehouses
        )

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the category associated with the current product
        context['category'] = self.object.category
        return context

    def get_success_url(self):
        # Redirect to the product list after a successful update
        return reverse('product_list', kwargs={'pk': self.object.category.pk})





class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'product/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')


    def test_func(self):
        return self.request.user.is_admin  # Only allow admins

