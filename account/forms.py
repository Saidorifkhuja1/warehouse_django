from django import forms
from .models import User
class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone_number', 'name', 'last_name', 'warehouse', 'created_by', 'photo')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_admin = False
        if commit:
            user.save()
        return user




class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('phone_number', 'name', 'last_name', 'created_by', 'warehouse', 'photo')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class WorkerForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['phone_number', 'name', 'last_name', 'warehouse', 'photo']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'last_name', 'phone_number', 'photo']  # Include 'is_admin' for admin users

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Show 'is_admin' only if the current user is an admin
        if not (user and user.is_admin):
            self.fields.pop('is_admin')

class PasswordResetForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)



class LoginForm(forms.Form):
    phone_number = forms.CharField(max_length=21, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class WorkerUpdateForm(forms.ModelForm):
    is_admin = forms.BooleanField(required=False, label="Admin Status")  # Explicitly add is_admin field

    class Meta:
        model = User
        fields = ['name', 'last_name', 'phone_number', 'warehouse', 'photo', 'is_admin']  # Include is_admin in fields

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Pass the current user to the form
        super().__init__(*args, **kwargs)

        # Only allow the form to show `is_admin` if the logged-in user is eligible
        if not (user and user.is_admin):
            self.fields.pop('is_admin', None)

