# E_mart/app/serializers.py
from rest_framework import serializers
from .models import Category, Product, Order, OrderItem, Wishlist
from django.contrib.auth.models import User

# Serializer for the built-in Django User model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email'] # Expose relevant user fields

# Serializer for your Category model
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__' # Includes 'id' and 'name'

# Serializer for your Product model
class ProductSerializer(serializers.ModelSerializer):
    # Display category name instead of just ID
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = '__all__' # Includes all fields: id, image, name, description, price, category, is_new, rating
        # If you want to explicitly list fields:
        # fields = ['id', 'image', 'name', 'description', 'price', 'category', 'category_name', 'is_new', 'rating']

# Serializer for your OrderItem model
class OrderItemSerializer(serializers.ModelSerializer):
    # Display product name and price from the related product
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_price', 'price', 'quantity', 'get_cost']
        read_only_fields = ['price'] # Price should be set from product at creation, not user input

# Serializer for your Order model
class OrderSerializer(serializers.ModelSerializer):
    # Nested serializers to display related user and order items
    user = UserSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True) # 'read_only=True' means items can't be created/updated directly via order API

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'created_at', 'updated_at', 'paid', 'total_price',
            'shipping_address', 'payment_method', 'name', 'phone', 'email',
            'items', 'get_total_cost'
        ]
        read_only_fields = ['total_price', 'get_total_cost'] # These should be calculated by the model/logic

# Serializer for your Wishlist model
class WishlistSerializer(serializers.ModelSerializer):
    # Nested serializers to display related user and product details
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    # Allow creating/updating wishlist by providing just the product ID
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'product', 'product_id', 'created_at']
        read_only_fields = ['user'] # User should be set automatically based on authenticated user
