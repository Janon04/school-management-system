from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Staff


@login_required
def staff_list_view(request):
    staff_members = Staff.objects.filter(is_active=True)
    return render(request, 'staff/staff_list.html', {'staff_members': staff_members})


@login_required
def staff_detail_view(request, pk):
    """View staff member details"""
    staff = get_object_or_404(Staff, pk=pk)
    
    context = {
        'staff': staff,
    }
    return render(request, 'staff/staff_detail.html', context)
