from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    if dictionary is None:
        return None
    return dictionary.get(key)
