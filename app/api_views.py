# E_mart/app/api_views.py
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from .models import Category, Product, Order, OrderItem, Wishlist
from .serializers import (
    UserSerializer,
    CategorySerializer,
    ProductSerializer,
    OrderSerializer,
    OrderItemSerializer,
    WishlistSerializer
)
from django_filters.rest_framework import DjangoFilterBackend
from cart.models import Cart, CartItem

# Read-only viewset for Django's User model
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated] # Only authenticated users can view users

# Viewset for Category model (CRUD operations)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny] # Categories can be public

# Viewset for Product model (CRUD operations)
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_new', 'rating']
    permission_classes = [permissions.AllowAny] # Products can be public

# Viewset for OrderItem model (CRUD operations)
class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated] # Order items require authentication

# Viewset for Order model (CRUD operations)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated] # Orders require authentication

    def perform_create(self, serializer):
        user = self.request.user
        cart = None
        if user.is_authenticated:
            cart = Cart.objects.filter(user=user).first()
        else:
            session_key = self.request.session.session_key
            if session_key:
                cart = Cart.objects.filter(session_key=session_key).first()

        if not cart or not cart.items.exists():
            raise serializers.ValidationError("Cannot place an order with an empty cart.")

        order = serializer.save(user=user)

        total_price = 0
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                price=cart_item.price,
                quantity=cart_item.quantity
            )
            total_price += cart_item.get_cost()

        order.total_price = total_price
        order.save()
        cart.items.all().delete()

    # Custom action to mark an order as paid
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_as_paid(self, request, pk=None):
        order = self.get_object()
        order.paid = True
        order.save()
        return Response({'status': 'order marked as paid'})

# Viewset for Wishlist model (CRUD operations)
class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated] # Wishlist requires authentication

    # Filter queryset to only show wishlist items for the authenticated user
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Wishlist.objects.filter(user=self.request.user)
        return Wishlist.objects.none() # Return empty queryset if user is not authenticated

    # Override perform_create to automatically assign the authenticated user
    def perform_create(self, serializer):
        # Prevent duplicate entries for the same user and product
        product = serializer.validated_data.get('product')
        if Wishlist.objects.filter(user=self.request.user, product=product).exists():
            return Response({"detail": "This product is already in your wishlist."}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=self.request.user)
