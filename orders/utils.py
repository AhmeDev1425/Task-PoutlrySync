
from .models import Order, Product

from rest_framework.response import Response
from rest_framework import status


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
        return Response(
            {"error": f"Product {product_id} not found or inactive"},
            status=status.HTTP_400_BAD_REQUEST
        )
    if product.stock < quantity:
        return Response(
            {"error": f"Insufficient stock for product {product.name}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    return product,quantity