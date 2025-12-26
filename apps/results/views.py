"""
Views for Results Management
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Avg, Sum, Q
from apps.accounts.decorators import teacher_required
from .models import Result, ReportCard
from apps.students.models import Student
from apps.exams.models import Exam, ExamSchedule
from apps.classes.models import ClassRoom, Subject
import json


@login_required
def student_results_view(request, student_id):
    """View all results for a student"""
    student = get_object_or_404(Student, pk=student_id)
    results = Result.objects.filter(student=student).order_by('-exam__start_date')
    report_cards = ReportCard.objects.filter(student=student).order_by('-exam__start_date')
    
    context = {
        'student': student,
        'results': results,
        'report_cards': report_cards,
    }
    return render(request, 'results/student_results.html', context)


@login_required
@teacher_required
def report_processing_view(request, exam_id):
    """Main report processing dashboard"""
    exam = get_object_or_404(Exam, pk=exam_id)
    
    # Get all exam schedules for this exam and unique class rooms
    schedules = ExamSchedule.objects.filter(exam=exam).select_related('class_room')
    
    # Get unique class rooms from schedules (SQLite-compatible)
    class_rooms = {}
    for schedule in schedules:
        if schedule.class_room.id not in class_rooms:
            class_rooms[schedule.class_room.id] = schedule.class_room
    
    # Calculate statistics
    schedule_data = []
    for class_room in class_rooms.values():
        total_students = class_room.students.count()
        total_subjects = ExamSchedule.objects.filter(exam=exam, class_room=class_room).count()
        
        # Calculate completion percentage
        expected_results = total_students * total_subjects
        actual_results = Result.objects.filter(exam=exam, student__current_class=class_room).count()
        completion_pct = (actual_results / expected_results * 100) if expected_results > 0 else 0
        
        schedule_data.append({
            'class_room': class_room,
            'subjects': ExamSchedule.objects.filter(exam=exam, class_room=class_room),
            'completion_percentage': completion_pct
        })
    
    total_classes = len(schedule_data)
    results_entered = Result.objects.filter(exam=exam).count()
    total_expected = sum([s['class_room'].students.count() * s['subjects'].count() for s in schedule_data])
    results_pending = total_expected - results_entered
    reports_generated = ReportCard.objects.filter(exam=exam).count()
    
    context = {
        'exam': exam,
        'schedules': schedule_data,
        'total_classes': total_classes,
        'results_entered': results_entered,
        'results_pending': results_pending,
        'reports_generated': reports_generated,
    }
    return render(request, 'results/report_processing.html', context)


@login_required
@teacher_required
def enter_results_view(request, exam_id, class_id):
    """Enter results for a class"""
    exam = get_object_or_404(Exam, pk=exam_id)
    class_room = get_object_or_404(ClassRoom, pk=class_id)
    
    # Get all students in the class
    students = class_room.students.all().order_by('admission_number')
    
    # Get all subjects for this exam and class
    exam_schedules = ExamSchedule.objects.filter(exam=exam, class_room=class_room)
    subjects = [schedule.subject for schedule in exam_schedules]
    
    # Calculate completion percentage
    total_expected = students.count() * len(subjects)
    total_entered = Result.objects.filter(exam=exam, student__in=students).count()
    completion_percentage = (total_entered / total_expected * 100) if total_expected > 0 else 0
    
    # Attach existing results to students
    for student in students:
        for subject in subjects:
            try:
                result = Result.objects.get(student=student, exam=exam, subject=subject)
                setattr(student, f'result_marks', result.marks_obtained if not result.is_absent else '')
                setattr(student, f'result_grade', result.grade)
                setattr(student, f'result_remarks', result.remarks)
            except Result.DoesNotExist:
                pass
    
    context = {
        'exam': exam,
        'class_room': class_room,
        'students': students,
        'subjects': subjects,
        'completion_percentage': completion_percentage,
    }
    return render(request, 'results/enter_results.html', context)


@login_required
@teacher_required
@require_POST
def save_results_view(request, exam_id, class_id):
    """Save results via AJAX"""
    try:
        exam = get_object_or_404(Exam, pk=exam_id)
        class_room = get_object_or_404(ClassRoom, pk=class_id)
        
        data = json.loads(request.body)
        subject_id = data.get('subject')
        results_data = data.get('results', [])
        
        subject = get_object_or_404(Subject, pk=subject_id)
        
        for result_data in results_data:
            student = Student.objects.get(pk=result_data['student'])
            
            # Get or create result
            result, created = Result.objects.get_or_create(
                student=student,
                exam=exam,
                subject=subject,
                defaults={'entered_by': request.user}
            )
            
            # Update result
            result.is_absent = result_data.get('is_absent', False)
            if not result.is_absent:
                result.marks_obtained = float(result_data.get('marks', 0))
                result.grade = result_data.get('grade', '')
            result.remarks = result_data.get('remarks', '')
            result.entered_by = request.user
            result.save()
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@teacher_required
def generate_reports_view(request, exam_id, class_id):
    """Generate report cards for a class"""
    exam = get_object_or_404(Exam, pk=exam_id)
    class_room = get_object_or_404(ClassRoom, pk=class_id)
    
    students = class_room.students.all().order_by('admission_number')
    report_cards = ReportCard.objects.filter(exam=exam, student__in=students)
    
    # Attach report cards to students
    for student in students:
        try:
            student.report_card = report_cards.get(student=student)
        except ReportCard.DoesNotExist:
            student.report_card = None
    
    context = {
        'exam': exam,
        'class_room': class_room,
        'students': students,
        'report_cards': report_cards,
    }
    return render(request, 'results/generate_reports.html', context)


@login_required
@teacher_required
@require_POST
def generate_all_reports_view(request, exam_id, class_id):
    """Generate all report cards for a class"""
    exam = get_object_or_404(Exam, pk=exam_id)
    class_room = get_object_or_404(ClassRoom, pk=class_id)
    
    students = class_room.students.all()
    count = 0
    
    for student in students:
        report_card, created = ReportCard.objects.get_or_create(
            student=student,
            exam=exam
        )
        report_card.calculate_totals()
        count += 1
    
    messages.success(request, f'Successfully generated {count} report cards!')
    return redirect('results:generate_reports', exam_id=exam_id, class_id=class_id)


@login_required
@teacher_required
@require_POST
def generate_single_report_view(request, exam_id, student_id):
    """Generate single report card"""
    exam = get_object_or_404(Exam, pk=exam_id)
    student = get_object_or_404(Student, pk=student_id)
    
    report_card, created = ReportCard.objects.get_or_create(
        student=student,
        exam=exam
    )
    report_card.calculate_totals()
    
    messages.success(request, f'Report card generated for {student.user.get_full_name}!')
    return redirect('results:generate_reports', exam_id=exam_id, class_id=student.current_class.pk)


@login_required
@teacher_required
@require_POST
def calculate_ranks_view(request, exam_id, class_id):
    """Calculate and assign ranks for a class"""
    exam = get_object_or_404(Exam, pk=exam_id)
    class_room = get_object_or_404(ClassRoom, pk=class_id)
    
    # Get all report cards for this class and exam, ordered by percentage
    report_cards = ReportCard.objects.filter(
        exam=exam, 
        student__current_class=class_room
    ).order_by('-percentage')
    
    # Assign ranks
    for index, report_card in enumerate(report_cards, start=1):
        report_card.rank = index
        report_card.save()
    
    messages.success(request, f'Ranks calculated for {report_cards.count()} students!')
    return redirect('results:generate_reports', exam_id=exam_id, class_id=class_id)


@login_required
def report_card_view(request, student_id, exam_id):
    """Generate and display report card"""
    student = get_object_or_404(Student, pk=student_id)
    exam = get_object_or_404(Exam, pk=exam_id)
    
    # Get or create report card
    report_card, created = ReportCard.objects.get_or_create(
        student=student,
        exam=exam
    )
    
    if created or request.GET.get('regenerate'):
        report_card.calculate_totals()
    
    results = Result.objects.filter(student=student, exam=exam).order_by('subject__name')
    total_students = student.current_class.students.count() if student.current_class else 1
    
    context = {
        'student': student,
        'exam': exam,
        'report_card': report_card,
        'results': results,
        'total_students': total_students,
    }
    return render(request, 'results/report_card.html', context)


@login_required
@teacher_required
@require_POST
def publish_results_view(request, exam_id, class_id):
    """Publish results to students and parents"""
    try:
        exam = get_object_or_404(Exam, pk=exam_id)
        exam.is_published = True
        exam.save()
        
        # Here you can add notification logic
        # from apps.notifications.models import Notification
        # Send notifications to students and parents
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
