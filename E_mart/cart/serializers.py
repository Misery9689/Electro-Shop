from rest_framework import serializers
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.CharField(source='product.image', read_only=True)  # Adjust field name as needed
    product_slug = serializers.CharField(source='product.slug', read_only=True)  # If you have slug field
    item_total = serializers.ReadOnlyField(source='total_price')  # Uses the model property

    class Meta:
        model = CartItem
        fields = [
            'id', 
            'product', 
            'product_name', 
            'product_image', 
            'product_slug',
            'quantity', 
            'price', 
            'item_total'
        ]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()  # Uses the model property
    total_price = serializers.ReadOnlyField()  # Uses the model property

    class Meta:
        model = Cart
        fields = [
            'id', 
            'user', 
            'session_key', 
            'created_at', 
            'updated_at', 
            'items', 
            'total_items', 
            'total_price'
        ]