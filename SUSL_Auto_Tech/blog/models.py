from django.db import models
from django.contrib.auth.models import User
import django.utils.timezone

class Post(models.Model):
    post_id = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    URL= models.URLField()
    category = models.CharField(max_length=200)
    publish_date = models.DateTimeField(default=django.utils.timezone.now)
    publish = models.BooleanField(default=False)
    original_author = models.CharField(max_length=500, default='', blank=True)

    def __str__(self):
        return self.title