from .views import ProductView, OrderView, order_export_view
from django.urls import path

urlpatterns = [
    path('products/', ProductView.as_view(), name='product-list-delete'),
    path('orders/', OrderView.as_view(), name='order-create-update'), 
    path('orders/<int:pk>/', OrderView.as_view()), # PATCH/PUT
    path('orders/export/', order_export_view, name='order-export'), 
]
