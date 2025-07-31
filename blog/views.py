

from django.shortcuts import render, get_object_or_404
from .models import Blog # Assuming 'Blog' model exists in models.py

# Create your views here.

def blog_list(request):
    """
    Displays a list of all blog posts, ordered by creation date.
    """
    blogs = Blog.objects.all().order_by('-published_date')
    return render(request, 'blog/blog_list.html', {'blogs': blogs})

def blog_detail(request, blog_id):
    """
    Displays the detail of a single blog post based on its ID.
    """
    blog = get_object_or_404(Blog, id=blog_id)
    return render(request, 'blog/blog_detail.html', {'blog': blog})