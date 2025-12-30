"""
Custom template tags for fees management
"""
from django import template

register = template.Library()


@register.filter
def sum_amounts(fee_list):
    """Calculate sum of amounts from a list of fee structures"""
    try:
        return sum([fee.amount for fee in fee_list])
    except (TypeError, AttributeError):
        return 0


@register.filter
def sum_payment_amounts(payment_list):
    """Calculate sum of amounts from a list of payments"""
    try:
        return sum([payment.amount_paid for payment in payment_list])
    except (TypeError, AttributeError):
        return 0


@register.filter
def filter_by_status(payment_list, status):
    """Filter payments by status"""
    try:
        return [p for p in payment_list if p.status == status]
    except (TypeError, AttributeError):
        return []
