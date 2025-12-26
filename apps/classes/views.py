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
    """List all classes"""
    classes = ClassRoom.objects.filter(is_active=True).select_related('class_teacher', 'academic_year')
    return render(request, 'classes/class_list.html', {'classes': classes})


@login_required
def class_detail_view(request, pk):
    """View class details"""
    class_room = get_object_or_404(ClassRoom, pk=pk)
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
