from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes 
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Order, Product
from .serializers import ProductSerializer, ProductDeleteSerializer, OrderSerializer, OrderEditSerializer
from .permessions import IsAdmin, IsOperator, IsAdminOrOperator
import logging
from .utils import OrderMixin, export_order_util
from django.db import transaction
from django.db.models import F

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
        return super().get_permissions()

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

        with transaction.atomic():
            deleted_count = Product.active_objects.filter(id__in=ids,company=request.user.company)\
                            .update(is_active=False, last_updated_at=timezone.now())

        return Response(
            {'message': f'{deleted_count} product(s) deleted successfully'},
            status=status.HTTP_200_OK
        )


class OrderView(generics.CreateAPIView, 
                generics.UpdateAPIView, OrderMixin):
    """
    POST /api/orders/ — Create one or more orders
    PATCH/PUT /api/orders/<id>/ — Edit an order (operator can edit only today's orders)
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrOperator]

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            return [IsOperator()]
        return super().get_permissions()

    # def get_serializer_class(self):
    #     if self.request.method == "POST":
    #         return OrderSerializer
    #     if self.request.method in ("PUT", "PATCH"):
    #         return OrderEditSerializer
    #     return super().get_serializer_class()


    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = self.create_order(serializer.validated_data, request.user)
        return Response(OrderSerializer(order).data, status=201)

    def patch(self, request, pk):
        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        order = self.update_order(order, serializer.validated_data, request.user)
        return Response(OrderSerializer(order).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_export_view(request):
    """
    GET /api/orders/export/ — Export company’s orders (CSV)
    """

    user = request.user
    orders = Order.objects.filter(company=user.company)
    return export_order_util(orders)



