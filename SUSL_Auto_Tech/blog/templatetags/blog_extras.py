from django import template
from django.templatetags.static import static

register = template.Library()

@register.simple_tag
def category_image_url(category_name):
    """
    Returns the static URL for the image corresponding to the given category.
    """
    category_map = {
        'AI': 'blog/images/AI.png',
        'Computer': 'blog/images/computer.png',
        'Mobile': 'blog/images/phone.png',
        'Tech Gadgets': 'blog/images/tech_gadget.png',
        'Other': 'blog/images/other.png'
    }
    
    # improved fallback/normalization logic
    # Try exact match first
    image_path = category_map.get(category_name)
    
    if not image_path:
        # Try case-insensitive lookup
        lower_map = {k.lower(): v for k, v in category_map.items()}
        image_path = lower_map.get(category_name.lower())
        
    if not image_path:
        # Default to other if not found
        image_path = category_map.get('Other')

    return static(image_path)
