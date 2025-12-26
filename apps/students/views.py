"""
Views for Student Management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from apps.accounts.decorators import admin_required, teacher_required
from .models import Student


@login_required
def student_list_view(request):
    """List all active students"""
    query = request.GET.get('q', '')
    class_filter = request.GET.get('class', '')
    
    students = Student.objects.filter(is_active=True).select_related('user', 'class_assigned', 'parent')
    
    if query:
        students = students.filter(
            Q(admission_number__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        )
    
    if class_filter:
        students = students.filter(class_assigned_id=class_filter)
    
    context = {
        'students': students,
        'query': query,
        'class_filter': class_filter,
    }
    return render(request, 'students/student_list.html', context)


@login_required
def student_detail_view(request, pk):
    """View student details"""
    student = get_object_or_404(Student, pk=pk)
    
    # Check permission - students can only view their own profile
    if request.user.is_student and student.user != request.user:
        messages.error(request, 'You can only view your own profile.')
        return redirect('dashboard')
    
    context = {
        'student': student,
    }
    return render(request, 'students/student_detail.html', context)


@login_required
@admin_required
def student_create_view(request):
    """Create new student (admin only)"""
    # Form handling would go here
    return render(request, 'students/student_form.html')


@login_required
@admin_required
def student_update_view(request, pk):
    """Update student information (admin only)"""
    student = get_object_or_404(Student, pk=pk)
    # Form handling would go here
    return render(request, 'students/student_form.html', {'student': student})


@login_required
@admin_required
def student_delete_view(request, pk):
    """Deactivate student (admin only)"""
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.is_active = False
        student.save()
        messages.success(request, f'Student {student.admission_number} deactivated.')
        return redirect('students:student_list')
    
    return render(request, 'students/student_confirm_delete.html', {'student': student})
