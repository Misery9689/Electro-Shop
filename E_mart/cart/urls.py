from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CartViewSet

# Define the router for the cart app's API views
router = DefaultRouter()
router.register(r'cart', CartViewSet, basename='cart') # Use basename for custom viewsets

urlpatterns = [
    # Your existing traditional cart URLs (if any) would go here, e.g.:
    # path('', views.cart_detail, name='cart_detail'),

    # IMPORTANT: Do NOT include router.urls here with a prefix like 'api/v1/'.
    # The API URLs for this app will be included from the main project's urls.py
]
