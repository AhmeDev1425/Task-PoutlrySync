from .models import Order, Product 
from django.urls import path
from .views import ProductListView, ProductDeleteView, OrderCreateView, order_export_view
from django.urls import path

urlpatterns = [
    path('api/products/', ProductListView.as_view(), name='product-list'),  # GET
    path('api/products/<int:pk>/', ProductDeleteView.as_view(), name='product-delete'),  # DELETE
    path('api/orders/', OrderCreateView.as_view(), name='order-create'),  # POST
    path('api/orders/export/', order_export_view, name='order-export'),  # GET
]
