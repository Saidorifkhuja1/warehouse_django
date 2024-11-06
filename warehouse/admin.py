from django.contrib import admin
from .models import *

from django.contrib import admin

#
@admin.register(Warehouse)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'phone_number','description']
    search_fields = ['name', 'address']


admin.site.register(Category)
