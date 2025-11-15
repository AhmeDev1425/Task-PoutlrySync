
from .models import Product

from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.http import HttpResponse
import csv

from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError
from .models import Order, Product
from django.utils import timezone


class OrderMixin:

    @staticmethod
    @transaction.atomic
    def create_order(data, user):
        product = Product.objects.select_for_update().get(
            id=data["product"],
            company=user.company
        )

        quantity = data["quantity"]

        if product.stock < quantity:
            raise ValidationError("Insufficient stock")

        product.stock = F('stock') - quantity
        product.save()

        order = Order.objects.create(
            company=user.company,
            product=product,
            quantity=quantity,
            status="pending",
            created_by=user
        )
        return order


    @staticmethod
    @transaction.atomic
    def update_order(order, data, user):
        if order.created_at.date() != timezone.now().date():
            raise ValidationError("Can't edit old orders")

        old_product = Product.objects.select_for_update().get(id=order.product_id)

        new_product = Product.objects.select_for_update().get(
            id=data["product"], 
            company=user.company
        )

        old_qty = order.quantity
        new_qty = data["quantity"]

        old_product.stock = F('stock') + old_qty
        old_product.save()

        if new_product.stock < new_qty:
            raise ValidationError("Insufficient stock")

        new_product.stock = F('stock') - new_qty
        new_product.save()

        for key, value in data.items():
            setattr(order, key, value)
        order.save()

        return order


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