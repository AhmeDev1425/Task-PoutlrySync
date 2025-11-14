from .views import ProductListView, ProductDeleteView, OrderView, order_export_view
from django.urls import path

urlpatterns = [
    path('api/products/', ProductListView.as_view(), name='product-list'),  # GET
    path('api/products/delete/', ProductDeleteView.as_view(), name='product-delete'),  # DELETE
    path('api/orders/', OrderView.as_view(), name='order-create'),  # POST
    path('api/orders/export/', order_export_view, name='order-export'),  # GET
]
