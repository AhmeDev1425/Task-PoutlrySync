
from rest_framework import serializers
from .models import Product, Order


class ProductDeleteSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField())


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name','price','stock','is_active','created_by','created_at','last_updated_at']
        read_only_fields = ['id','created_by','created_at','last_updated_at','is_active']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id','product','quantity','status','created_by','created_at','shipped_at']
        read_only_fields = ['id','created_by','created_at','status','shipped_at']