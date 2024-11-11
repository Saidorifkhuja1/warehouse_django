from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('homepage', HomePageView.as_view(), name='homepage'),
    path('worker/create/', WorkerCreateView.as_view(), name='worker_create'),
    path('warehouse/<int:warehouse_id>/workers/', WorkerListView.as_view(), name='worker_list'),
    path('worker/update/<int:pk>/', WorkerUpdateView.as_view(), name='worker_update'),
    path('', LoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('profile/details/', RetrieveProfileView.as_view(), name='profile_detail'),
    path('profile/update/<int:pk>/', UpdateProfileView.as_view(), name='profile_update'),
    path('profile/delete/', DeleteProfileView.as_view(), name='profile_delete'),
    path('worker/delete/<int:pk>/', WorkerDeleteView.as_view(), name='worker_delete'),
    path('profile/password-reset/', PasswordResetView.as_view(), name='password_reset'),
]
