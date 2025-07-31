from rest_framework import serializers
from .models import Blog

class BlogSerializer(serializers.ModelSerializer):
    # If author is a ForeignKey, you might want to display the author's username
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Blog
        fields = '__all__' # This will include 'author' and 'image'
        # If you want to explicitly list fields:
        # fields = ['id', 'title', 'content', 'author', 'author_username', 'image', 'published_date', 'updated_date']
