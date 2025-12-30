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
def attendance_home_view(request):
    """Attendance home page - list all classes (teachers see only their classes)"""
    if hasattr(request.user, 'teacher_profile'):
        classes = ClassRoom.objects.filter(is_active=True, class_teacher=request.user.teacher_profile).select_related('class_teacher__user', 'academic_year').prefetch_related('students')
    else:
        classes = ClassRoom.objects.all().select_related('class_teacher__user', 'academic_year').prefetch_related('students')
    today = timezone.now().date()

    # Get classes that have attendance marked today
    marked_today = Attendance.objects.filter(date=today).values_list('class_room_id', flat=True).distinct()
    marked_classes = set(marked_today)

    # Count total students
    total_students = sum(class_room.students.filter(is_active=True).count() for class_room in classes)

    context = {
        'classes': classes,
        'today': today,
        'marked_classes': marked_classes,
        'marked_today_count': len(marked_classes),
        'total_students': total_students,
    }
    return render(request, 'attendance/attendance_home.html', context)


@login_required
@teacher_required
def mark_attendance_view(request, class_id):
    """Mark attendance for a class (teachers only for their classes)"""
    class_room = get_object_or_404(ClassRoom, pk=class_id)
    # If teacher, restrict access
    if hasattr(request.user, 'teacher_profile') and class_room.class_teacher != request.user.teacher_profile:
        messages.error(request, 'You do not have permission to mark attendance for this class.')
        return redirect('attendance:attendance_home')
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
    from datetime import datetime, timedelta
    
    # Get date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    class_filter = request.GET.get('class')
    
    # Default date range (last 30 days)
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    if not start_date:
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    # Get attendance records
    if student_id:
        student = get_object_or_404(Student, pk=student_id)
        attendance_records = Attendance.objects.filter(
            student=student,
            date__range=[start_date, end_date]
        ).order_by('-date')
    else:
        attendance_records = Attendance.objects.filter(
            date__range=[start_date, end_date]
        ).select_related('student__user', 'student__class_assigned', 'marked_by')
        
        if class_filter:
            attendance_records = attendance_records.filter(student__class_assigned_id=class_filter)
        
        attendance_records = attendance_records.order_by('-date')
        student = None
    
    # Calculate statistics
    total_days = attendance_records.count()
    present_count = attendance_records.filter(status='Present').count()
    absent_count = attendance_records.filter(status='Absent').count()
    late_count = attendance_records.filter(status='Late').count()
    excused_count = attendance_records.filter(status='Excused').count()
    
    attendance_percentage = (present_count / total_days * 100) if total_days > 0 else 0
    
    context = {
        'student': student,
        'attendance_records': attendance_records,
        'total_days': total_days,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'excused_count': excused_count,
        'attendance_percentage': attendance_percentage,
        'start_date': start_date,
        'end_date': end_date,
        'today': timezone.now().date(),
        'classes': ClassRoom.objects.all() if not student else None,
        'selected_class': class_filter,
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
