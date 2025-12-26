"""
Views for Teacher Management
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import admin_required
from .models import Teacher


@login_required
def teacher_list_view(request):
    """List all active teachers"""
    teachers = Teacher.objects.filter(is_active=True).select_related('user')
    return render(request, 'teachers/teacher_list.html', {'teachers': teachers})


@login_required
def teacher_detail_view(request, pk):
    """View teacher details"""
    teacher = get_object_or_404(Teacher, pk=pk)
    classes = teacher.classes_as_teacher.all()
    subjects = teacher.subjects.all()
    
    context = {
        'teacher': teacher,
        'classes': classes,
        'subjects': subjects,
    }
    return render(request, 'teachers/teacher_detail.html', context)
