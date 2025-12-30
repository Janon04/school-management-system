"""
Views for Class and Subject Management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import admin_required, teacher_required
from .models import ClassRoom, Subject, ClassSubject, TimeTable, AcademicYear


@login_required
def class_list_view(request):
    """List all classes (teachers see only their classes)"""
    if hasattr(request.user, 'teacher_profile'):
        # Only show classes where this teacher is assigned
        classes = ClassRoom.objects.filter(is_active=True, class_teacher=request.user.teacher_profile).select_related('class_teacher', 'academic_year')
    else:
        classes = ClassRoom.objects.filter(is_active=True).select_related('class_teacher', 'academic_year')
    return render(request, 'classes/class_list.html', {'classes': classes})


@login_required
def class_detail_view(request, pk):
    """View class details (teachers only see their own classes)"""
    class_room = get_object_or_404(ClassRoom, pk=pk)
    # If teacher, restrict access
    if hasattr(request.user, 'teacher_profile') and class_room.class_teacher != request.user.teacher_profile:
        messages.error(request, 'You do not have permission to view this class.')
        return redirect('classes:class_list')
    students = class_room.students.filter(is_active=True)
    subjects = class_room.class_subjects.filter(is_active=True)
    timetable = class_room.timetable_entries.all()
    context = {
        'class_room': class_room,
        'students': students,
        'subjects': subjects,
        'timetable': timetable,
    }
    return render(request, 'classes/class_detail.html', context)


@login_required
def subject_list_view(request):
    """List all subjects"""
    subjects = Subject.objects.filter(is_active=True)
    return render(request, 'classes/subject_list.html', {'subjects': subjects})


@login_required
@admin_required
def subject_create_view(request):
    """Create a new subject"""
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        category = request.POST.get('category')
        description = request.POST.get('description', '')
        pass_mark = request.POST.get('pass_mark', 40)
        total_marks = request.POST.get('total_marks', 100)
        
        try:
            subject = Subject.objects.create(
                name=name,
                code=code,
                category=category,
                description=description,
                pass_mark=int(pass_mark),
                total_marks=int(total_marks)
            )
            messages.success(request, f'Subject "{subject.name}" created successfully!')
            return redirect('classes:subject_detail', pk=subject.pk)
        except Exception as e:
            messages.error(request, f'Error creating subject: {str(e)}')
    
    return render(request, 'classes/subject_form.html', {'action': 'Create'})


@login_required
@admin_required
def subject_update_view(request, pk):
    """Update an existing subject"""
    subject = get_object_or_404(Subject, pk=pk)
    
    if request.method == 'POST':
        subject.name = request.POST.get('name')
        subject.code = request.POST.get('code')
        subject.category = request.POST.get('category')
        subject.description = request.POST.get('description', '')
        subject.pass_mark = int(request.POST.get('pass_mark', 40))
        subject.total_marks = int(request.POST.get('total_marks', 100))
        
        try:
            subject.save()
            messages.success(request, f'Subject "{subject.name}" updated successfully!')
            return redirect('classes:subject_detail', pk=subject.pk)
        except Exception as e:
            messages.error(request, f'Error updating subject: {str(e)}')
    
    return render(request, 'classes/subject_form.html', {
        'subject': subject,
        'action': 'Update'
    })


@login_required
def subject_detail_view(request, pk):
    """View subject details"""
    subject = get_object_or_404(Subject, pk=pk)
    classes = subject.class_subjects.filter(is_active=True)
    
    context = {
        'subject': subject,
        'classes': classes,
    }
    return render(request, 'classes/subject_detail.html', context)


@login_required
@teacher_required
def timetable_view(request, class_id):
    """View timetable for a class"""
    class_room = get_object_or_404(ClassRoom, pk=class_id)
    timetable = TimeTable.objects.filter(class_room=class_room).order_by('day', 'start_time')
    
    # Organize by day
    days = {}
    for entry in timetable:
        if entry.day not in days:
            days[entry.day] = []
        days[entry.day].append(entry)
    
    context = {
        'class_room': class_room,
        'timetable': days,
    }
    return render(request, 'classes/timetable.html', context)
