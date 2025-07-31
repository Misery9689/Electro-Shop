from django.db import models
from django.conf import settings # Import settings for ForeignKey to User

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    # This creates the 'author_id' column in the database
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)

    published_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_date']

    def __str__(self):
        return self.title
