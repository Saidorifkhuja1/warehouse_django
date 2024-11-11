from django.urls import reverse
from django.views.generic import View, CreateView, DetailView, UpdateView, \
    DeleteView, FormView, TemplateView, ListView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import *
from .models import *
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout
from django.shortcuts import render
from .models import Warehouse




class HomePageView(LoginRequiredMixin, ListView):
    model = Warehouse
    template_name = 'account/home.html'
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




from django.urls import reverse_lazy

class WorkerCreateView(UserPassesTestMixin, CreateView):
    model = User
    form_class = WorkerForm
    template_name = 'account/worker_create.html'

    def test_func(self):
        return self.request.user.is_admin  # Only allow admin users to access

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter warehouse choices to only show warehouses created by the current admin
        form.fields['warehouse'].queryset = Warehouse.objects.filter(owner=self.request.user)
        return form

    def form_valid(self, form):
        form.instance.is_admin = False  # Ensure the worker cannot be an admin
        form.instance.created_by = self.request.user  # Set created_by to the current admin
        # Save the worker object first
        response = super().form_valid(form)
        # At this point, the worker is saved, so we can now access the warehouse ID
        self.warehouse_id = form.instance.warehouse.id  # Get the warehouse ID from the worker instance
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the warehouse_id to the context, default to None if not set
        context['warehouse_id'] = getattr(self, 'warehouse_id', None)
        return context

    def get_success_url(self):
        # Ensure warehouse_id is passed in the success URL
        if hasattr(self, 'warehouse_id'):
            return reverse_lazy('worker_list', kwargs={'warehouse_id': self.warehouse_id})
        return reverse_lazy('worker_list')  # Fallback in case warehouse_id is not available



class LoginView(View):
    template_name = 'account/login.html'

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            user = authenticate(request, phone_number=phone_number, password=password)
            if user is not None:
                login(request, user)
                return redirect('homepage')
            else:
                messages.error(request, "Invalid phone number or password.")
        return render(request, self.template_name, {'form': form})


class RetrieveProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'account/profile_detail.html'
    context_object_name = 'user'

    def get_object(self):
        return self.request.user






class UpdateProfileView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'account/profile_update.html'
    success_url = reverse_lazy('profile_detail')  # Redirect to the profile detail page after update

    def test_func(self):
        return self.request.user.is_admin  # Only allow access if the user is an admin

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass current user to form
        return kwargs

    def get_object(self, queryset=None):
        # Admins can update any user profile
        user_id = self.kwargs.get('pk')  # Use 'pk' from URL to get the specific user
        return User.objects.get(pk=user_id)  # This will raise a 404 if the user does not exist







class DeleteProfileView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'account/profile_confirm_delete.html'
    success_url = reverse_lazy('home')  # Redirect to homepage after deletion

    def get_object(self):
        return self.request.user  # Allow deletion of the current user profile

    def test_func(self):
        # Only allow access if the user is an admin
        return self.request.user.is_admin

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Profile deleted successfully!")  # Add success message before deletion
        return super().delete(request, *args, **kwargs)





class PasswordResetView(LoginRequiredMixin, FormView):
    template_name = 'account/password_reset.html'
    form_class = PasswordResetForm  # A form with old_password and new_password fields
    success_url = reverse_lazy('profile_detail')

    def test_func(self):
        # Only allow access if the user is an admin
        return self.request.user.is_admin
    def form_valid(self, form):
        old_password = form.cleaned_data.get("old_password")
        new_password = form.cleaned_data.get("new_password")

        user = self.request.user
        if not user.check_password(old_password):
            form.add_error("old_password", "Incorrect old password!")
            return self.form_invalid(form)

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(self.request, user)  # Keep user logged in after password change
        messages.success(self.request, "Password changed successfully!")
        return super().form_valid(form)


class WorkerCreateView(UserPassesTestMixin, CreateView):
    model = User
    form_class = WorkerForm
    template_name = 'account/worker_create.html'

    def test_func(self):
        return self.request.user.is_admin  # Only allow admin users to access

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit the queryset of the warehouse field to those created by the current admin
        form.fields['warehouse'].queryset = Warehouse.objects.filter(owner=self.request.user)
        return form

    def form_valid(self, form):
        form.instance.is_admin = False  # Ensure the worker cannot be an admin
        form.instance.created_by = self.request.user  # Set created_by to the current admin
        response = super().form_valid(form)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        warehouse_id = self.kwargs.get('warehouse_id')
        context['warehouse_id'] = warehouse_id  # Pass warehouse_id to the template
        return context

    def get_success_url(self):
        # Redirect to the homepage
        return reverse_lazy('homepage')


# Replace 'home' with the actual name of your homepage URL pattern






class WorkerListView(ListView):
    model = User
    template_name = 'account/worker_list.html'
    context_object_name = 'workers'

    def get_queryset(self):
        # Get the warehouse by ID (from URL)
        warehouse_id = self.kwargs.get('warehouse_id')
        warehouse = get_object_or_404(Warehouse, pk=warehouse_id)

        # Filter users who are workers (is_admin=False), assigned to the current warehouse
        return User.objects.filter(warehouse=warehouse, is_admin=False, created_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        warehouse_id = self.kwargs.get('warehouse_id')
        context['warehouse'] = get_object_or_404(Warehouse, pk=warehouse_id)
        return context












class WorkerUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    fields = ['name', 'last_name', 'phone_number', 'warehouse', 'photo', 'is_active', 'is_admin']
    template_name = 'account/worker_update.html'


    def get_object(self, queryset=None):
        worker = get_object_or_404(User, pk=self.kwargs['pk'], created_by=self.request.user)
        return worker

    def form_valid(self, form):
        # Ensure the creator can set is_admin to True if desired
        return super().form_valid(form)

    def get_success_url(self):
        # Dynamically generate the success URL with warehouse_id
        worker = self.get_object()
        return reverse_lazy('worker_list', kwargs={'warehouse_id': worker.warehouse.pk})

    def test_func(self):
        # Check if the current user is an admin and created this worker
        worker = self.get_object()
        return self.request.user.is_admin and worker.created_by == self.request.user


class WorkerDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'account/worker_delete.html'

    def get_object(self):
        # Get the worker to be deleted
        return self.get_queryset().get(pk=self.kwargs['pk'])

    def test_func(self):
        # Only allow deletion if the user is an admin
        return self.request.user.is_admin

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the warehouse ID from the worker object if available
        warehouse = self.get_object().warehouse if hasattr(self.get_object(), 'warehouse') else None
        context['warehouse_id'] = warehouse.pk if warehouse else None
        return context

    def get_success_url(self):
        # Redirect to the worker list page for the associated warehouse after deletion
        warehouse_id = self.get_object().warehouse.pk if hasattr(self.get_object(), 'warehouse') else None
        if warehouse_id:
            return reverse('worker_list', kwargs={'warehouse_id': warehouse_id})
        else:
            # Redirect to a default worker list or home page if warehouse_id is not found
            return reverse('home')


def custom_logout(request):
    logout(request)  # Logs out the user
    return redirect('login')