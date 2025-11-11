
from rest_framework import serializers
from .models import Product, Order

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'last_updated_at']


class ProductDeleteSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField())

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'product', 'quantity', 'status', 'shipped_at']