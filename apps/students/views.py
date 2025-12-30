"""
Views for Student Management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from apps.accounts.decorators import admin_required, teacher_required
from apps.classes.models import ClassRoom
from .models import Student
from .forms import StudentForm


@login_required
def student_list_view(request):
    """List all active students"""
    query = request.GET.get('q', '')
    class_filter = request.GET.get('class', '')

    students = Student.objects.filter(is_active=True).select_related('user', 'class_assigned', 'parent')
    classes = ClassRoom.objects.filter(is_active=True)

    if query:
        students = students.filter(
            Q(admission_number__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        )

    if class_filter:
        students = students.filter(class_assigned_id=class_filter)

    male_count = students.filter(gender='M').count()
    female_count = students.filter(gender='F').count()

    context = {
        'students': students,
        'classes': classes,
        'query': query,
        'class_filter': class_filter,
        'male_count': male_count,
        'female_count': female_count,
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
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            messages.success(
                request, 
                f'Student {student.user.get_full_name()} ({student.admission_number}) created successfully!'
            )
            return redirect('students:student_detail', pk=student.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentForm()
    
    context = {
        'form': form,
        'title': 'Add New Student',
        'button_text': 'Create Student',
    }
    return render(request, 'students/student_form.html', context)


@login_required
@admin_required
def student_update_view(request, pk):
    """Update student information (admin only)"""
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            student = form.save()
            messages.success(
                request,
                f'Student {student.user.get_full_name()} updated successfully!'
            )
            return redirect('students:student_detail', pk=student.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentForm(instance=student)
    
    context = {
        'form': form,
        'student': student,
        'title': f'Edit Student - {student.user.get_full_name()}',
        'button_text': 'Update Student',
    }
    return render(request, 'students/student_form.html', context)


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
