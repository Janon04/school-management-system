from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import admin_required
from .models import Promotion


@login_required
@admin_required
def promotion_list_view(request):
    """List all promotions"""
    promotions = Promotion.objects.all().order_by('-promoted_on')
    return render(request, 'promotions/promotion_list.html', {'promotions': promotions})


@login_required
@admin_required
def promote_students_view(request):
    """Bulk promote students"""
    # Bulk promotion logic would go here
    return render(request, 'promotions/promote_students.html')
