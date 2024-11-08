# urls.py

from django.urls import path
from .views import *

urlpatterns = [
    # Warehouse URLs
    path('warehouses_list/', WarehouseListView.as_view(), name='warehouse_list'),
    path('warehouses_create/', WarehouseCreateView.as_view(), name='warehouse_create'),
    path('warehouses_detail/<int:pk>/', WarehouseDetailView.as_view(), name='warehouse_detail'),
    path('warehouses/update/<int:pk>/', WarehouseUpdateView.as_view(), name='warehouse_update'),
    path('warehouses/delete/<int:pk>/', WarehouseDeleteView.as_view(), name='warehouse_delete'),

    # Category URLs
    path('warehouses/<int:pk>/categories_list/', CategoryListView.as_view(), name='category_list'),
    path('warehouses/<int:pk>/categories_create/', CategoryCreateView.as_view(), name='category_create'),
    path('categories_detail/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
    path('categories/update/<int:pk>/', CategoryUpdateView.as_view(), name='category_update'),
    path('categories/delete/<int:pk>/', CategoryDeleteView.as_view(), name='category_delete'),
]
