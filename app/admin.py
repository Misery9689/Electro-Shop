from django.contrib import admin

from .models import Category, Product, Order, OrderItem

# Register your models here.
admin.site.register([
    # Add your models here
    # Example: YourModelName,
    Category,
    Product,
    Order,
    OrderItem,
])