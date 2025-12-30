"""
Template tags for fees app
"""
from django import template

register = template.Library()


@register.filter
def sum_amounts(fee_list):
    """Calculate sum of amounts from a list of fee structures"""
    return sum([fee.amount for fee in fee_list])
