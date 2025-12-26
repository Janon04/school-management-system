"""
Custom template filters for class operations
"""
from django import template

register = template.Library()


@register.filter(name='multiply')
def multiply(value, arg):
    """
    Multiplies the value by the argument
    Usage: {{ value|multiply:arg }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter(name='divide')
def divide(value, arg):
    """
    Divides the value by the argument
    Usage: {{ value|divide:arg }}
    """
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter(name='percentage')
def percentage(value, total):
    """
    Calculates percentage
    Usage: {{ value|percentage:total }}
    """
    try:
        if float(total) == 0:
            return 0
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0
