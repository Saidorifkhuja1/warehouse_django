from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
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




class WarehouseListView(ListView):
    model = Warehouse
    template_name = 'warehouse_list.html'
    context_object_name = 'warehouses'

    def get_queryset(self):
        user = self.request.user


        if user.is_admin:
            # Warehouses owned by the admin
            warehouses = Warehouse.objects.filter(owner=user)

            # Warehouses created by admins connected to this admin
            connected_admins = User.objects.filter(created_by=user)
            warehouses |= Warehouse.objects.filter(owner__in=connected_admins)

            # Warehouses where the user is directly connected via the 'warehouse' ForeignKey
            warehouses |= Warehouse.objects.filter(id=user.warehouse.id) if user.warehouse else Warehouse.objects.none()

            return warehouses




class WarehouseDetailView(LoginRequiredMixin, DetailView):
    model = Warehouse
    template_name = 'warehouse/warehouse_detail.html'
    context_object_name = 'warehouse'

    def get_object(self, queryset=None):
        # Get the warehouse object
        warehouse = super().get_object(queryset)

        user = self.request.user
        if (
            warehouse.owner == user or
            (user.is_admin and (
                user.warehouse == warehouse or
                warehouse.owner == user.created_by
            ))
        ):
            return warehouse

        # Raise a 404 error if the user does not have access
        raise Http404("You do not have permission to view this warehouse.")







class WarehouseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = 'warehouse/warehouse_update.html'
    success_url = reverse_lazy('warehouse_list')

    def test_func(self):
        warehouse = self.get_object()
        user = self.request.user
        is_owner = user == warehouse.owner
        is_connected_admin = warehouse.owner.creator_user.filter(id=user.id).exists()
        is_directly_connected = user.warehouse == warehouse

        return is_owner or is_connected_admin or is_directly_connected








class WarehouseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Warehouse
    template_name = 'warehouse/warehouse_delete.html'
    success_url = reverse_lazy('warehouse_list')

    def test_func(self):
        warehouse = self.get_object()
        user = self.request.user


        is_owner = user == warehouse.owner
        is_connected_admin = warehouse.owner.creator_user.filter(id=user.id).exists()
        is_directly_connected = user.warehouse == warehouse

        return is_owner or is_connected_admin or is_directly_connected


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
            # Admins can see all categories for the specified warehouse, regardless of who owns it
            return Category.objects.filter(warehouse=warehouse)
        else:
            # Workers or other users can only see categories linked to their admin’s warehouses
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
        return self.request.user.is_admin

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
