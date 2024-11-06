from django.urls import path
from .views import *

urlpatterns = [
    path('product_create/', ProductCreateView.as_view(), name='product_create'),
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/update/<int:pk>/', SellProductView.as_view(), name='sell_product'),
    path('products/delete/<int:pk>/', ProductDeleteView.as_view(), name='product_delete'),
]