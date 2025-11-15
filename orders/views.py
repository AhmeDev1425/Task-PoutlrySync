from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes 
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Order, Product
from .serializers import ProductSerializer, ProductDeleteSerializer, OrderSerializer
from .permessions import IsAdmin, IsOperator, IsAdminOrOperator
from .utils import OrderMixin, export_order_util
from django.db import transaction


class ProductView(generics.GenericAPIView):
    """
    GET /api/products/ — List all active products for the user's company

    [
        {
            "id": 15,
            "name": "Company 3 Product 1",
            "price": "384.39",
            "stock": 18,
            "is_active": true,
            "created_by": 1,
            "created_at": "2025-11-15T22:03:19.978303Z",
            "last_updated_at": "2025-11-15T22:03:19.978443Z"
        },
        {
            "id": 16,
            "name": "Company 3 Product 2",
            "price": "277.66",
            "stock": 22,
            "is_active": true,
            "created_by": 6,
            "created_at": "2025-11-15T22:03:19.985242Z",
            "last_updated_at": "2025-11-15T22:03:19.985387Z"
        }
    ]

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


class OrderView(generics.GenericAPIView, OrderMixin):
    """
    POST /api/orders/ — Create one or more orders
    [
        {"product": 15, "quantity": 3},
        {"product": 16, "quantity": 22}
    ]
    or {"product": 15, "quantity": 3},

    PATCH/PUT /api/orders/<id>/ — Edit an order (operator can edit only today's orders)
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrOperator]

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            return [IsOperator()]
        return super().get_permissions()

    def post(self, request):
        data = request.data
    
        if isinstance(data, dict):
            data = [data]

        serializer = self.get_serializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)

        created_orders = []
        user = request.user

        with transaction.atomic():
            for order_data in serializer.validated_data:
                order = self.create_order(order_data, user)
                created_orders.append(order)

        return Response(
            OrderSerializer(created_orders, many=True).data,
            status=201
        )
    
    def patch(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        if not pk:
            return Response({"error": "Order ID is required"}, status=400)



        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_order = self.update_order(order, serializer.validated_data, request.user)
        return Response(OrderSerializer(updated_order).data)

    
    # def put(self, request):
    #     self.patch(request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_export_view(request):
    """
    GET /api/orders/export/ — Export company’s orders (CSV)
    """

    user = request.user
    orders = Order.objects.filter(company=user.company)
    return export_order_util(orders)



