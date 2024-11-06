from django.contrib import admin
from .models import Product, SoldProduct

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'cost', 'amount', 'add_time', 'status', 'category']
    search_fields = ['name', 'status','description']
    list_filter = ['category', 'add_time']
    ordering = ['-add_time']


@admin.register(SoldProduct)
class SoldProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'cost', 'amount', 'add_time', 'status','category']
    search_fields = ['name', 'status', 'note']
    list_filter = ['category', 'add_time']
    ordering = ['-add_time']


