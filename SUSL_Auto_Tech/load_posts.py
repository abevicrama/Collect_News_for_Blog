import os
import sys
import csv
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SUSL_Auto_Tech.settings')
django.setup()

from blog.models import Post
from django.contrib.auth.models import User

def import_data():
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'blog_post', 'blog_details.csv')
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return

    # Ensure a user exists to assign as author
    author, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com'})
    if created:
        author.set_password('admin')
        author.save()
        print("Created default admin user.")

    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        count = 0
        for row in reader:
             # csv header: post_id, title, content, category, author, url, publish_date, publish, checked
            
            # Skip if already exists
            # Check if exists, update if so, otherwise create
            post, created = Post.objects.get_or_create(post_id=row['post_id'], defaults={
                'title': row['title'],
                'body': row.get('summary', row.get('content', '')),
                'category': row['category'],
                'URL': row['url'],
                'author': author,
                'publish': True,
                'original_author': row.get('author', ''),
                'publish_date': row.get('publish_date')
            })

            if created:
                print(f"Created: {post.title[:30]}...")
            else:
                 # Skip existing posts
                 pass

    print(f"Successfully imported {count} posts.")

if __name__ == '__main__':
    import_data()
