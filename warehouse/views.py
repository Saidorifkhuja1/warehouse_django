from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from account.models import *
from .forms import *
from django.shortcuts import get_object_or_404
from .models import Warehouse
from django.db.models import Q
from django.core.exceptions import PermissionDenied


class WarehouseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = 'warehouse/warehouse_create.html'
    success_url = reverse_lazy('homepage')

    def test_func(self):
        return self.request.user.is_admin  # Only admins can create warehouses

    def form_valid(self, form):
        form.instance.owner = self.request.user  # Set the current user as the owner
        return super().form_valid(form)


class WarehouseListView(LoginRequiredMixin, ListView):
    model = Warehouse
    template_name = 'warehouse/warehouse_list.html'
    context_object_name = 'warehouses'

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            # Admins should see only warehouses they created
            return Warehouse.objects.filter(owner=user)
        else:
            # Workers should see warehouses connected to them and those created by their creator
            creator = user.owner if hasattr(user, 'owner') else None
            if creator:
                # Filter warehouses owned by the creator or assigned to the worker
                return Warehouse.objects.filter(owner=creator) | Warehouse.objects.filter(connected_users=user)
            return Warehouse.objects.none()





class WarehouseDetailView(LoginRequiredMixin, DetailView):
    model = Warehouse
    template_name = 'warehouse/warehouse_detail.html'
    context_object_name = 'warehouse'


class WarehouseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = 'warehouse/warehouse_update.html'
    success_url = reverse_lazy('warehouse_list')

    def test_func(self):
        return self.request.user == self.get_object().owner  # Only the owner can update the warehouse


class WarehouseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Warehouse
    template_name = 'warehouse/warehouse_delete.html'
    success_url = reverse_lazy('warehouse_list')

    def test_func(self):
        return self.request.user == self.get_object().owner  # Only the owner can delete the warehouse





class CategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'warehouse/category_create.html'

    def test_func(self):
        return self.request.user.is_admin  # Only allow admins to create categories

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass the current user to the form
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['warehouse'] = get_object_or_404(Warehouse, pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        # Redirect to the category list view for the current warehouse
        return reverse_lazy('category_list', kwargs={'pk': self.kwargs['pk']})





class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'warehouse/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        user = self.request.user
        warehouse_id = self.kwargs['pk']  # Get warehouse ID from URL
        warehouse = get_object_or_404(Warehouse, pk=warehouse_id)

        if user.is_admin:
            # Admin sees categories for the specific warehouse they own
            return Category.objects.filter(warehouse=warehouse, warehouse__owner=user)
        else:
            # Workers or other users see categories linked to their admin’s warehouses
            return Category.objects.filter(warehouse=warehouse, warehouse__owner=user.owner) if hasattr(user, 'owner') else Category.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['warehouse'] = get_object_or_404(Warehouse, pk=self.kwargs['pk'])
        return context




class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'warehouse/category_detail.html'
    context_object_name = 'category'

    def get_success_url(self):
        # Redirect to the category list of the related warehouse
        return reverse_lazy('category_list', kwargs={'pk': self.object.warehouse.pk})



class CategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'warehouse/category_update.html'

    def test_func(self):
        user = self.request.user
        category = self.get_object()
        # Only admins can update categories, and they must own the warehouse
        return user.is_admin and category.warehouse.owner == user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass the current user to the form
        return kwargs

    def get_success_url(self):
        # Redirect to the category list view for the current warehouse
        return reverse_lazy('category_detail', kwargs={'pk': self.get_object().warehouse.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['warehouse'] = self.get_object().warehouse  # Pass warehouse to template
        return context




class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Category
    template_name = 'warehouse/category_delete.html'

    def get_success_url(self):
        # Redirect to the category list of the related warehouse
        return reverse_lazy('category_list', kwargs={'pk': self.object.warehouse.pk})

    def test_func(self):
        return self.request.user.is_admin
