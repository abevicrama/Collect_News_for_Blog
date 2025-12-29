from django.shortcuts import render, get_object_or_404
from .models import Post
from django.db.models import Count

from django.core.paginator import Paginator

def index(request):
    post_list = Post.objects.filter(publish=True).order_by('-publish_date')
    paginator = Paginator(post_list, 5) # Show 5 posts per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    category_counts = Post.objects.values('category').annotate(count=Count('category'))
    
    context = {
        'recent_posts': page_obj, # Rename to generic posts in template or keep check
        'page_obj': page_obj,
        'category_counts': category_counts,
    }
    return render(request, 'blog/index.html', context)

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    category_counts = Post.objects.values('category').annotate(count=Count('category'))
    return render(request, 'blog/post_detail.html', {'post': post, 'category_counts': category_counts})

def contact(request):
    return render(request, 'blog/contact.html')

def category_posts(request, category_name):
    # Case insensitive filtering for category
    post_list = Post.objects.filter(category__iexact=category_name, publish=True).order_by('-publish_date')
    paginator = Paginator(post_list, 5)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    category_counts = Post.objects.values('category').annotate(count=Count('category'))
    
    context = {
        'recent_posts': page_obj, # Reuse the same template loop
        'page_obj': page_obj,
        'category_counts': category_counts,
        'current_category': category_name,
    }
    return render(request, 'blog/index.html', context)

