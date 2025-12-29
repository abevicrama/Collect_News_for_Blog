from django.shortcuts import render, get_object_or_404
from .models import Post
from django.db.models import Count

def index(request):
    recent_posts = Post.objects.filter(publish=True).order_by('-publish_date')[:10]
    category_counts = Post.objects.values('category').annotate(count=Count('category'))
    
    context = {
        'recent_posts': recent_posts,
        'category_counts': category_counts,
    }
    return render(request, 'blog/index.html', context)

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'blog/post_detail.html', {'post': post})

