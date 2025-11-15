from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes 
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Order, Product
from .serializers import ProductSerializer, ProductDeleteSerializer, OrderSerializer, OrderEditSerializer
from .permessions import IsAdmin, IsOperator, IsAdminOrOperator
import logging
from .utils import deal_with_order_product, export_order_util
from django.db import transaction

# TODO: multi-tenant support based on company

class ProductView(generics.GenericAPIView):
    """
    GET /api/products/ — List all active products for the user's company
    DELETE /api/products/ — Soft-delete one or more products
    """
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        return Product.active_objects.filter(company=user.company)

    def get_serializer_class(self):
        if self.request.method == 'DELETE':
            return ProductDeleteSerializer
        return super().get_serializer_class()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data['ids']

        deleted_count = self.get_queryset().filter(
            id__in=ids
        ).update(is_active=False, last_updated_at=timezone.now())

        if deleted_count == 0:
            return Response(
                {'error': 'No products found to delete'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {'message': f'{deleted_count} product(s) deleted successfully'},
            status=status.HTTP_200_OK
        )

class OrderView(generics.CreateAPIView, generics.UpdateAPIView):
    """
    POST /api/orders/ — Create one or more orders
    PATCH/PUT /api/orders/<id>/ — Edit an order (operator can edit only today's orders)
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminOrOperator()]   
        if self.request.method in ("PUT", "PATCH"):
            return [IsOperator()]
        return [IsAdminOrOperator()]


    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrderSerializer
        if self.request.method in ("PUT", "PATCH"):
            return OrderEditSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        user = request.user

        orders_data = request.data.get("orders", [])
        if not isinstance(orders_data, list) or len(orders_data) == 0:
            return Response({"error": "orders must be a non-empty array"}, 
                            status=status.HTTP_400_BAD_REQUEST)

        created_orders = []
        with transaction.atomic():
            for order_data in orders_data:
                order_data["company"] = user.company.id
                order_data["created_by"] = user.id
                print(order_data)
                product,quantity = deal_with_order_product(order_data)

                serializer = self.get_serializer(data=order_data)
                serializer.is_valid(raise_exception=True)

                product.purchase_done(quantity)
                order = serializer.save()


                logging.getLogger("orders.confirmation").info(
                    "Order created: order_id=%s user=%s company=%s product=%s qty=%s",
                    order.id, user.id, user.company.id, order.product.id, order.quantity
                )

                created_orders.append(serializer.data)

        return Response({
            "orders": created_orders,
            "message": "Orders created successfully. Confirmation email logged."
        }, status=status.HTTP_201_CREATED)


    def update(self, request, *args, **kwargs):

        user = request.user
        order_id = request.data.get("order_id")

        order_data = {}
        order_data["product"] = int(request.data["product"])
        order_data["quantity"] = int(request.data["quantity"])
        order_data["id"] = int(request.data["order_id"])
        order_data["company"] = user.company.id

        try:
            order = Order.objects.get(id=order_id, company=user.company)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if order.created_at.date() != timezone.now().date():
            return Response(
                {"error": "Operators can only edit orders created today"},
                status=status.HTTP_403_FORBIDDEN
            )

        deal_with_order_product(order_data) 
 
        serializer = self.get_serializer(order, data=request.data, partial = True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_export_view(request):
    """
    GET /api/orders/export/ — Export company’s orders (CSV)
    """

    user = request.user
    orders = Order.objects.filter(company=user.company)
    return export_order_util(orders)


