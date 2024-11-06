
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .forms import UserCreationForm, UserChangeForm


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('phone_number', 'name', 'last_name', 'created_by', 'warehouse', 'photo', 'is_active', 'is_admin', 'is_superuser')
    list_filter = ('is_admin', 'is_active', 'is_superuser')
    fieldsets = (
        ('Personal info', {'fields': ('phone_number', 'password', 'name', 'last_name', 'created_by', 'warehouse', 'photo')}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'name', 'last_name', 'created_by', 'warehouse', 'photo', 'password1', 'is_active', 'is_admin', 'is_superuser'),
        }),
    )
    search_fields = ('phone_number', 'name', 'last_name', 'warehouse__name', 'photo')
    ordering = ('phone_number',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
