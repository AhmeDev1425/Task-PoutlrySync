
from .models import Product

from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.http import HttpResponse
import csv

def deal_with_order_product(order_data):
    """
    get order data and if operator handle it to edit in his order 
    or create new order 
    """
    
    quantity = order_data.get("quantity", 0)
    product_id = order_data.get("product")

    try:
        product = Product.active_objects.get(
            id=product_id, 
            company=order_data["company"]
        )
    except Product.DoesNotExist:
        return ValidationError( f"Product {product_id} not found or inactive")
    
    if product.stock < quantity:
        return ValidationError(f"Insufficient stock for product {product.name}"),

    product.purchase_done(quantity)
    return product,quantity

def export_order_util(orders):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Product', 'Quantity', 'Status', 'Shipped At', 'Created At'])

    for order in orders:
        product_name = order.product.name if getattr(order, 'product', None) else ''
        shipped_at = order.shipped_at.isoformat() if getattr(order, 'shipped_at', None) else ''
        created_at = order.created_at.isoformat() if getattr(order, 'created_at', None) else ''
        writer.writerow([
            order.id,
            product_name,
            order.quantity,
            order.status,
            shipped_at,
            created_at
        ])

    return response


    # response = HttpResponse(content_type='text/csv')
    # response['Content-Disposition'] = 'attachment; filename="orders.csv"'
    # writer = csv.writer(response)
    # writer.writerow(['ID', 'Product', 'Quantity', 'Status', 'Shipped At', 'Created At'])
    
    # for order in queryset:
    #     writer.writerow([order.id, order.product, order.company, order.user, order.status,order.])  # Adjust fields as necessary
    # return response