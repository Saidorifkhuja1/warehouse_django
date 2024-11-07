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



class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'account/home.html'



class WorkerCreateView(UserPassesTestMixin, CreateView):
    model = User
    form_class = WorkerForm
    template_name = 'account/worker_create.html'
    success_url = reverse_lazy('worker_list')

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
        return super().form_valid(form)

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






class WorkerListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'account/worker_list.html'
    context_object_name = 'workers'

    # Only admins can access this view
    def test_func(self):
        return self.request.user.is_admin

    # Filter workers to show only those created by the current admin
    def get_queryset(self):
        return User.objects.filter(created_by=self.request.user)








class WorkerUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    fields = ['name', 'last_name', 'phone_number', 'warehouse', 'photo', 'is_active', 'is_admin']
    template_name = 'account/worker_update.html'
    success_url = reverse_lazy('worker_list')  # Adjust this to your actual URL for worker listings

    def get_object(self, queryset=None):
        worker = get_object_or_404(User, pk=self.kwargs['pk'], created_by=self.request.user)
        return worker

    def form_valid(self, form):
        # Ensure the creator can set is_admin to True if desired
        return super().form_valid(form)

    def test_func(self):
        # Check if the current user is an admin and created this worker
        worker = self.get_object()
        return self.request.user.is_admin and worker.created_by == self.request.user