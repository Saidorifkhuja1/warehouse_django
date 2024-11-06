from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import *
from .forms import *
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages


class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/product_create.html'
    success_url = reverse_lazy('product_list')

    def test_func(self):
        return self.request.user.is_admin  # Only admins can create products

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass the current user to the form
        return kwargs

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.all()

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'



# class ProductUpdateView(UpdateView):
#     model = Product
#     form_class = ProductForm
#     template_name = 'product/product_update.html'
#     context_object_name = 'product'
#
#     def get_object(self, queryset=None):
#         product = get_object_or_404(Product, pk=self.kwargs['pk'])
#         return product
#
#     def form_valid(self, form):
#         product = self.get_object()
#         new_amount = form.cleaned_data['amount']
#
#         # Check if amount is less than current amount
#         if new_amount < product.amount:
#             # Subtract from current Product and update SoldProduct
#             SoldProduct.objects.create(
#                 name=product.name,
#                 cost=product.cost,
#                 amount=product.amount - new_amount,
#                 note=product.note,
#                 status='sotildi',  # Status should be 'sotildi' for SoldProduct
#                 category=product.category
#             )
#             # Update Product amount to reflect the remaining amount
#             product.amount = new_amount
#             product.save()
#
#         elif new_amount >= product.amount:
#             # If the entered amount is greater than or equal to the current amount, delete the product
#             product.delete()
#             # Create SoldProduct with the amount that was deleted
#             SoldProduct.objects.create(
#                 name=product.name,
#                 cost=product.cost,
#                 amount=product.amount,
#                 note=product.note,
#                 status='sotildi',
#                 category=product.category
#             )
#
#         # Handle status change to 'sotildi' for Product (but do not change Product's status to 'sotildi')
#         if form.cleaned_data['status'] == 'sotildi':
#             # Create a SoldProduct when status is 'sotildi'
#             SoldProduct.objects.create(
#                 name=product.name,
#                 cost=product.cost,
#                 amount=product.amount,
#                 note=product.note,
#                 status='sotildi',  # 'sotildi' for SoldProduct
#                 category=product.category
#             )
#             # Ensure Product's status remains 'yangi'
#             product.status = 'yangi'
#             product.save()
#
#         # Continue with normal response after form submission
#         messages.success(self.request, "Product updated successfully.")
#         return redirect('product_list')
#
#     def form_invalid(self, form):
#         # Handle invalid form submission (for example, invalid data)
#         messages.error(self.request, "There was an error updating the product.")
#         return self.render_to_response({'form': form})


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/product_update.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        # Fetch the product object that is being updated
        product = get_object_or_404(Product, pk=self.kwargs['pk'])
        return product

    def form_valid(self, form):
        # Retrieve the product object and the new amount entered in the form
        product = self.get_object()
        new_amount = form.cleaned_data['amount']

        # Case 1: When the entered amount is less than the current amount of the product
        if new_amount < product.amount:
            # Calculate the difference (this is the amount to be sold)
            sold_amount = new_amount

            # Create a new SoldProduct with the amount of sold products
            SoldProduct.objects.create(
                name=product.name,
                cost=product.cost,
                amount=sold_amount,
                note=product.note,
                status='sotildi',  # 'sotildi' status for SoldProduct
                category=product.category
            )

            # Update the product's amount to the new amount entered
            product.amount -= sold_amount  # Subtract sold amount from product
            product.save()

        # Case 2: When the entered amount is greater than or equal to the current amount
        elif new_amount >= product.amount:
            # Create a SoldProduct for the full amount of the current product
            SoldProduct.objects.create(
                name=product.name,
                cost=product.cost,
                amount=product.amount,  # Use the full amount of the product
                note=product.note,
                status='sotildi',  # 'sotildi' for SoldProduct
                category=product.category
            )

            # Delete the product since its amount is sold out or updated
            product.delete()

        # Ensure that the status of the product remains 'yangi'
        # Even if the user tries to set status to 'sotildi', it should not change the status of the product
        if form.cleaned_data['status'] == 'sotildi':
            # No need to change the product status, it should remain 'yangi'
            product.status = 'yangi'
            product.save()

        # Provide feedback and redirect
        messages.success(self.request, "Product updated successfully.")
        return redirect('product_list')

    def form_invalid(self, form):
        # Handle invalid form submission (for example, invalid data)
        messages.error(self.request, "There was an error updating the product.")
        return self.render_to_response({'form': form})


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'product/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')


    def test_func(self):
        return self.request.user.is_admin  # Only allow admins

