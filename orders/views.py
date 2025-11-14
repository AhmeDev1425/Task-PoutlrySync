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
from .permessions import IsAdmin, IsOperator

# TODO: multi-tenant support based on company

class ProductListView(generics.ListAPIView):
    """
    GET /api/products/ — List all active products for the user's company
    """
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Product.active_objects.filter(company=user.company)

class ProductDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/products/ — Soft-delete one or more products
    """
    serializer_class = ProductDeleteSerializer
    permission_classes = [IsAdmin]
    queryset = Product.active_objects.all() 

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data['ids']

        deleted_count = self.get_queryset().filter(
            id__in=ids,
            company=request.user.company
        ).update(is_active=False, last_updated_at=timezone.now())

        if deleted_count == 0:
            return Response(
                {'error': 'No products found to delete'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            {'message': f'{deleted_count} product(s) deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )

class OrderView(generics.CreateAPIView, generics.UpdateAPIView):
    """
    POST /api/orders/ — Create one or more orders
    """
    serializer_class = OrderSerializer 
    permission_classes = [IsAdmin|IsOperator]

    def create(self, request, *args, **kwargs):
        user = request.user
        orders_data = request.data.get('orders', [])
        created_orders = []

        for order_data in orders_data:
            order_data['company'] = user.company.id
            order_data['created_by'] = user.id
            order_quantity = order_data.get('quantity', 0)
            product_id = order_data.get('product')
            try:
                product = Product.active_objects.get(id=product_id, company=user.company, is_active=True)
            except Product.DoesNotExist:
                return Response({'error': f'Product with {product_id} does not exist '}, status=status.HTTP_400_BAD_REQUEST)
            if product.stock < order_quantity:
                return Response({'error': f'Insufficient stock for product {product.name}'}, status=status.HTTP_400_BAD_REQUEST)
            
            product.purchase_done(order_quantity)
            serializer = self.get_serializer(data=order_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            created_orders.append(serializer.data)
            
        return Response({'orders': created_orders,'message':"your order has been created ! and we had send details to ur email. could you check it ?"}, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        user = request.user
        order_id = kwargs.get('pk')
        try:
            order = Order.objects.get(id=order_id, company=user.company)
        except Order.DoesNotExist:
            return Response({'error': 'Order does not exist'}, status=status.HTTP_404_NOT_FOUND)

        if IsOperator().has_permission(request, self):
            if order.created_at.date() != timezone.now().date():
                return Response({'error': 'Operators can only edit orders created today'}, status=status.HTTP_403_FORBIDDEN)

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(order, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

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

