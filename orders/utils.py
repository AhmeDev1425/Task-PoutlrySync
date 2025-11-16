from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.http import HttpResponse
from rest_framework.exceptions import ValidationError
from .models import Order, Product
import csv
import logging

class OrderMixin:

    @staticmethod
    @transaction.atomic
    def create_order(data, user):
        try:
            product = Product.active_objects.select_for_update().get(
                id=data["product"],
                company=user.company
            )
        except Product.DoesNotExist:
            return data["product"]
            # raise ValidationError("Product isn,t belong to your company")
        
        quantity = data["quantity"]
        if product.stock < quantity:
            return product
            # raise ValidationError("not enough stock")

        product.stock = F('stock') - quantity
        product.save()
        order = Order.objects.create(
            company=user.company,
            product=product,
            quantity=quantity,
            status="pending",
            created_by=user
        )
        logging.getLogger("orders.confirmation").info(
                "Order created: order_id=%s user=%s company=%s product=%s qty=%s",
                order.id, user.id, user.company.id, order.product.id, order.quantity
            )
        return order


    @staticmethod
    @transaction.atomic
    def update_order(order, data, user):
        if order.created_at.date() != timezone.now().date():
            raise ValidationError("Can't edit old orders")
        
        if order.company != user.company:
            raise ValidationError("Order does not belong to your company")
        
        if not "product" in data:
            data["product"] = order.product.id
        if not "quantity" in data:
            raise ValidationError("Quantity is required")

        old_product = Product.active_objects.select_for_update().get(id=order.product_id)

        new_product = Product.active_objects.select_for_update().get(
            id=data["product"], 
            company=user.company
        )

        old_qty = order.quantity
        new_qty = data["quantity"]

        old_product.stock = F('stock') + old_qty
        old_product.save()

        if new_product.stock < new_qty:
            raise ValidationError("not enough stock")

        new_product.stock = F('stock') - new_qty
        new_product.save()
        order.product = new_product
        order.quantity = data.get("quantity", order.quantity)
        order.status = data.get("status", order.status)  # لو محتاج تحدث status كمان

        order.save()


        logging.getLogger("orders.confirmation").info(
                "Order %s for company %s had update by %s. product=%s qty=%s",
                order.id, user.company.id, user.id, order.product.id, order.quantity
            )
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