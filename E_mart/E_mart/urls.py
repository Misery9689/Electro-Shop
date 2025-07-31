from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth.views import LogoutView
from rest_framework.routers import DefaultRouter

from blog.urls import router as blog_router_instance
from app.urls import router as app_router_instance # Assuming app.urls exists and has a router
from cart.urls import router as cart_router_instance # Import the cart router

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Create a main router for all API endpoints
main_router = DefaultRouter()
main_router.registry.extend(blog_router_instance.registry)
main_router.registry.extend(app_router_instance.registry)
main_router.registry.extend(cart_router_instance.registry) # Extend with cart router

class LogoutViewAllowGET(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.Index, name='index'),
    path('index/', views.Index, name='index'),
    path('shop/', views.Shop, name='shop'),
    path('blog/', include('blog.urls')),
    path('checkout/', views.CheckOut, name='checkout'),
    path('about_us/', views.AboutUs, name='about_us'),
    path('contact/', views.Contact, name='contact'),
    path('login/', views.Login, name='login'),
    path('register/', views.Register, name='register'),
    path('signup/', views.Signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('products/<int:product_id>/', views.product_detail_view, name='detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:id>/', views.cart_add, name='cart_add'),
    path('cart/item_clear/<int:id>/', views.item_clear, name='item_clear'),
    path('cart/item_increment/<int:id>/', views.item_increment, name='item_increment'),
    path('cart/item_decrement/<int:id>/', views.item_decrement, name='item_decrement'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('my-orders/', views.user_orders, name='order_list'),
    path('master/', views.Master, name='master'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('create-sample-order/', views.create_sample_order, name='create_sample_order'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:product_id>/', views.wishlist_remove, name='wishlist_remove'),
    path('wishlist/add-all-to-cart/', views.wishlist_add_all_to_cart, name='wishlist_add_all_to_cart'),
    path('api/v1/', include(main_router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
