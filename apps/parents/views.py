
"""
Views for Parent Management
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import admin_required
from .models import Parent
from .forms import ParentForm

@login_required
def parent_dashboard_view(request):
    """Dashboard for parent to view all their children"""
    # Get the parent object for the logged-in user
    parent = getattr(request.user, 'parent_profile', None)
    children = parent.children.filter(is_active=True) if parent else []
    # For each child, get all published exams and the latest published exam
    child_reports = []
    from apps.exams.models import Exam
    from apps.results.models import ReportCard
    for child in children:
        published_exams = Exam.objects.filter(results__student=child, is_published=True).distinct().order_by('-start_date')
        latest_exam = published_exams.first()
        # Get all report cards for published exams
        report_cards = ReportCard.objects.filter(student=child, exam__in=published_exams).select_related('exam').order_by('-exam__start_date')
        child_reports.append({
            'child': child,
            'latest_exam': latest_exam,
            'report_cards': report_cards,
        })
    return render(request, 'parents/parent_dashboard.html', {'child_reports': child_reports})


@login_required
def parent_list_view(request):
    """List all active parents"""
    parents = Parent.objects.filter(is_active=True).select_related('user')
    return render(request, 'parents/parent_list.html', {'parents': parents})


@login_required
def parent_detail_view(request, pk):
    """View parent details"""
    parent = get_object_or_404(Parent, pk=pk)
    children = parent.children.filter(is_active=True)
    
    context = {
        'parent': parent,
        'children': children,
    }
    return render(request, 'parents/parent_detail.html', context)


@admin_required
def parent_create_view(request):
    """Create a new parent"""
    if request.method == 'POST':
        form = ParentForm(request.POST, request.FILES)
        if form.is_valid():
            parent = form.save()
            messages.success(request, f'Parent {parent.user.get_full_name()} created successfully!')
            return redirect('parents:parent_detail', pk=parent.pk)
    else:
        form = ParentForm()
    
    context = {
        'form': form,
        'title': 'Add New Parent',
        'button_text': 'Create Parent'
    }
    return render(request, 'parents/parent_form.html', context)


@admin_required
def parent_update_view(request, pk):
    """Update an existing parent"""
    parent = get_object_or_404(Parent, pk=pk)
    
    if request.method == 'POST':
        form = ParentForm(request.POST, request.FILES, instance=parent)
        if form.is_valid():
            parent = form.save()
            messages.success(request, f'Parent {parent.user.get_full_name()} updated successfully!')
            return redirect('parents:parent_detail', pk=parent.pk)
    else:
        form = ParentForm(instance=parent)
    
    context = {
        'form': form,
        'parent': parent,
        'title': 'Edit Parent',
        'button_text': 'Update Parent'
    }
    return render(request, 'parents/parent_form.html', context)
