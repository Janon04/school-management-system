from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import admin_required
from .models import Staff
from .forms import StaffForm


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


@admin_required
def staff_create_view(request):
    """Create a new staff member"""
    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES)
        if form.is_valid():
            staff = form.save()
            messages.success(request, f'Staff member {staff.user.get_full_name()} created successfully!')
            return redirect('staff:staff_detail', pk=staff.pk)
    else:
        form = StaffForm()
    
    context = {
        'form': form,
        'title': 'Add New Staff Member',
        'button_text': 'Create Staff'
    }
    return render(request, 'staff/staff_form.html', context)


@admin_required
def staff_update_view(request, pk):
    """Update an existing staff member"""
    staff = get_object_or_404(Staff, pk=pk)
    
    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES, instance=staff)
        if form.is_valid():
            staff = form.save()
            messages.success(request, f'Staff member {staff.user.get_full_name()} updated successfully!')
            return redirect('staff:staff_detail', pk=staff.pk)
    else:
        form = StaffForm(instance=staff)
    
    context = {
        'form': form,
        'staff': staff,
        'title': 'Edit Staff Member',
        'button_text': 'Update Staff'
    }
    return render(request, 'staff/staff_form.html', context)
