"""
Views for Attendance Management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from apps.accounts.decorators import teacher_required
from .models import Attendance
from apps.students.models import Student
from apps.classes.models import ClassRoom
import json


@login_required
@teacher_required
def mark_attendance_view(request, class_id):
    """Mark attendance for a class"""
    class_room = get_object_or_404(ClassRoom, pk=class_id)
    students = class_room.students.filter(is_active=True)
    today = timezone.now().date()
    
    # Get existing attendance for today
    existing_attendance = {}
    for record in Attendance.objects.filter(class_room=class_room, date=today):
        existing_attendance[record.student_id] = record.status
    
    if request.method == 'POST':
        # Process attendance marking
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            if status:
                Attendance.objects.update_or_create(
                    student=student,
                    date=today,
                    defaults={
                        'status': status,
                        'class_room': class_room,
                        'marked_by': request.user
                    }
                )
        messages.success(request, 'Attendance marked successfully!')
        return redirect('attendance:mark_attendance', class_id=class_id)
    
    context = {
        'class_room': class_room,
        'students': students,
        'existing_attendance': existing_attendance,
        'today': today,
    }
    return render(request, 'attendance/mark_attendance.html', context)


@login_required
def attendance_report_view(request, student_id=None):
    """View attendance report"""
    if student_id:
        student = get_object_or_404(Student, pk=student_id)
        attendance_records = Attendance.objects.filter(student=student).order_by('-date')
    else:
        attendance_records = Attendance.objects.all().order_by('-date')[:100]
        student = None
    
    context = {
        'student': student,
        'attendance_records': attendance_records,
    }
    return render(request, 'attendance/attendance_report.html', context)


@require_POST
@login_required
@teacher_required
def mark_attendance_ajax(request):
    """Mark attendance via AJAX"""
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        status = data.get('status')
        date = data.get('date', timezone.now().date())
        
        student = Student.objects.get(pk=student_id)
        
        Attendance.objects.update_or_create(
            student=student,
            date=date,
            defaults={
                'status': status,
                'class_room': student.class_assigned,
                'marked_by': request.user
            }
        )
        
        return JsonResponse({'success': True, 'message': 'Attendance marked'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
