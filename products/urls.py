from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListCreateView.as_view(), name='product_list_create'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
]