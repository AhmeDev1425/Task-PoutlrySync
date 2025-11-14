from .views import ProductView, OrderView, order_export_view
from django.urls import path

urlpatterns = [
    path('products/', ProductView.as_view(), name='product'),  # GET
    path('orders/', OrderView.as_view(), name='order-create'),  # POST
    path('orders/export/', order_export_view, name='order-export'),  # GET
]
