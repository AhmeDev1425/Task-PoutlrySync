import csv
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Order, Product
from .serializers import ProductSerializer, ProductDeleteSerializer, OrderSerializer
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


# 

class ProductListView(generics.ListAPIView):
    """
    GET /api/products/ — List all active products for the user's company
    """
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Product.objects.filter(company=user.company)

class ProductDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/products/ — Soft-delete one or more products
    """
    serializer_class = ProductDeleteSerializer

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data['ids']
        user = request.user
        products = Product.all_objects.filter(id__in=ids,company=user.company).update(is_active=False,last_updated_at=timezone.now())

        return Response(status=status.HTTP_204_NO_CONTENT)
    

class OrderCreateView(generics.CreateAPIView):
    """
    POST /api/orders/ — Create one or more orders
    """
    serializer_class = OrderSerializer  # Assume OrderSerializer is defined elsewhere
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        orders_data = request.data.get('orders', [])
        created_orders = []

        for order_data in orders_data:
            order_data['company'] = user.company.id
            order_data['created_by'] = user.id
            serializer = self.get_serializer(data=order_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            created_orders.append(serializer.data)

        return Response({'orders': created_orders}, status=status.HTTP_201_CREATED)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_export_view(request):
    """
    GET /api/orders/export/ — Export company’s orders (CSV)
    """

    user = request.user
    orders = Order.objects.filter(company=user.company)

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