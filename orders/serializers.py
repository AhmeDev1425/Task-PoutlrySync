
from rest_framework import serializers
from .models import Product, Order


class ProductDeleteSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False, write_only=True)

    def validate_ids(self, ids):
        user = self.context['request'].user
        
        products = Product.active_objects.filter(id__in=ids, company=user.company)
        
        if products.count() != len(ids):
            missing_ids = set(ids) - set(products.values_list('id', flat=True))
            raise serializers.ValidationError(
                {"missing_ids": list(missing_ids)}
            )

        return ids

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name','price','stock','is_active','created_by','created_at','last_updated_at']
        read_only_fields = ['id','created_by','created_at','last_updated_at','is_active']

class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ["id", "product", "quantity", "status"]

    def validate_product(self, product):
        user = self.context["request"].user
        if product.company != user.company:
            raise serializers.ValidationError("Product does not belong to your company")
        return product

    def validate_quantity(self, qty):
        if qty <= 0:
            raise serializers.ValidationError("Quantity must be > 0")
        return qty
