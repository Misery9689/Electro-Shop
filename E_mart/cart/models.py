# models.py
from django.db import models
from django.conf import settings
from django.db.models import Sum, F
from app.models import Product  # Assuming Product model is in 'app' app

class Cart(models.Model):
    # Use OneToOneField for a single cart per user
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True, unique=True)  # Unique for anonymous carts
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_items(self):
        """Calculate total number of items in cart"""
        return self.items.aggregate(total=Sum('quantity'))['total'] or 0
    
    @property  
    def total_price(self):
        """Calculate total price of all items in cart"""
        return self.items.aggregate(
            total=Sum(F('quantity') * F('price'))
        )['total'] or 0

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        if self.session_key:
            return f"Anonymous Cart ({self.session_key[:5]}...)"
        return "Empty Cart"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of adding to cart

    class Meta:
        unique_together = ('cart', 'product')  # A product can only be in a cart once

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.price * self.quantity