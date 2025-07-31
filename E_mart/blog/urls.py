from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import BlogViewSet
from . import views # Import your traditional views

router = DefaultRouter()
router.register('blogs', BlogViewSet)

urlpatterns = [
    # Traditional blog URLs
    path('', views.blog_list, name='blog_list'),
    # If you have a blog detail page, add it here too, e.g.:
    path('<int:blog_id>/', views.blog_detail, name='blog_detail'), # Corrected view name
    # API URLs for blog
    path('api/v1/', include(router.urls)),
]
