# E_mart/blog/api_views.py
from rest_framework import viewsets
from .models import Blog # Change from Post to Blog
from .serializers import BlogSerializer # Change from PostSerializer to BlogSerializer

class BlogViewSet(viewsets.ModelViewSet): # Renamed from PostViewSet
    # Change order_by from '-created_at' to '-published_date'
    queryset = Blog.objects.all().order_by('-published_date')
    serializer_class = BlogSerializer # Change from PostSerializer to BlogSerializer
