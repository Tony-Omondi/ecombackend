from rest_framework import serializers
from .models import Category, Product, ProductImage, Variant

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ['id', 'size', 'color', 'stock']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = VariantSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'category', 'category_id',
            'stock', 'sku', 'brand', 'images', 'variants', 'created_at', 'updated_at'
        ]

    def validate_sku(self, value):
        if Product.objects.filter(sku=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError('SKU must be unique.')
        return value