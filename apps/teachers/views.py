"""
Views for Teacher Management
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from apps.accounts.decorators import admin_required
from .models import Teacher
from .forms import TeacherForm


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


@login_required
@admin_required
def teacher_create_view(request):
    """Create a new teacher"""
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, _('Teacher %(name)s created successfully!') % {'name': teacher.user.get_full_name()})
            return redirect('teachers:teacher_detail', pk=teacher.pk)
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = TeacherForm()
    
    context = {
        'form': form,
        'title': _('Add New Teacher'),
        'button_text': _('Create Teacher'),
        'is_create': True
    }
    return render(request, 'teachers/teacher_form.html', context)


@login_required
@admin_required
def teacher_update_view(request, pk):
    """Update an existing teacher"""
    teacher = get_object_or_404(Teacher, pk=pk)
    
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, _('Teacher %(name)s updated successfully!') % {'name': teacher.user.get_full_name()})
            return redirect('teachers:teacher_detail', pk=teacher.pk)
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = TeacherForm(instance=teacher)
    
    context = {
        'form': form,
        'teacher': teacher,
        'title': _('Edit Teacher: %(name)s') % {'name': teacher.user.get_full_name()},
        'button_text': _('Update Teacher'),
        'is_create': False
    }
    return render(request, 'teachers/teacher_form.html', context)
