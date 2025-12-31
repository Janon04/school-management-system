from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from xhtml2pdf import pisa
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Count, Avg, Sum, Q
from apps.accounts.decorators import teacher_required, admin_required
from .models import Result, ReportCard
from apps.accounts.models import User
from apps.students.models import Student
from apps.exams.models import Exam, ExamSchedule
from apps.classes.models import ClassRoom, Subject
from apps.notifications.models import Notification
from apps.parents.models import Parent
import json

# PDF report card view (xhtml2pdf)
@login_required
def report_card_pdf(request, student_id, exam_id):
    student = get_object_or_404(Student, pk=student_id)
    exam = get_object_or_404(Exam, pk=exam_id)
    report_card, _ = ReportCard.objects.get_or_create(student=student, exam=exam)
    report_card.calculate_totals()
    results = Result.objects.filter(student=student, exam=exam).order_by('subject__name')
    # School info from DB
    from apps.config.models import SchoolInfo
    school_info_obj = SchoolInfo.objects.order_by('-updated_at').first()
    school_info = {
        'name': school_info_obj.name if school_info_obj else '',
        'address': school_info_obj.address if school_info_obj else '',
        'phone': school_info_obj.phone if school_info_obj else '',
        'email': school_info_obj.email if school_info_obj else '',
        'motto': school_info_obj.motto if school_info_obj else '',
        'logo': school_info_obj.logo if school_info_obj and school_info_obj.logo else None,
    }
    headmaster = school_info_obj.headmaster if school_info_obj and school_info_obj.headmaster else None
    class_teacher = student.class_assigned.class_teacher if student.class_assigned and student.class_assigned.class_teacher else None
    # Per-subject ranking
    subject_ranks = {}
    for result in results:
        subject_results = Result.objects.filter(
            exam=exam,
            subject=result.subject,
            student__class_assigned=student.class_assigned
        ).order_by('-marks_obtained')
        rank = None
        for idx, r in enumerate(subject_results, start=1):
            if r.student_id == student.id:
                rank = idx
                break
        subject_ranks[result.subject.id] = {
            'rank': rank,
            'total': subject_results.count()
        }
    context = {
        'student': student,
        'exam': exam,
        'report_card': report_card,
        'results': results,
        'school_info': school_info,
        'headmaster': headmaster,
        'class_teacher': class_teacher,
        'subject_ranks': subject_ranks,
    }
    html = render_to_string('results/report_card_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_card_{student.admission_number}_{exam.name}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response

# Utility: Send notification to user
def send_result_notification(user, title, message, link=None, notification_type='INFO'):
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link or ''
    )

"""
Views for Results Management
"""
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Avg, Sum, Q
from apps.accounts.decorators import teacher_required, admin_required
from .models import Result, ReportCard
from apps.students.models import Student
from apps.exams.models import Exam, ExamSchedule
from apps.classes.models import ClassRoom, Subject
import json


@login_required
def result_list_view(request):
    """List all results with filters"""
    results = Result.objects.select_related('student__user', 'exam', 'subject').all()
    
    # Filters
    exam_id = request.GET.get('exam')
    class_id = request.GET.get('class')
    subject_id = request.GET.get('subject')
    student_id = request.GET.get('student')
    
    if exam_id:
        results = results.filter(exam_id=exam_id)
    if class_id:
        results = results.filter(student__class_assigned_id=class_id)
    if subject_id:
        results = results.filter(subject_id=subject_id)
    if student_id:
        results = results.filter(student_id=student_id)
    
    results = results.order_by('-created_at')[:200]  # Limit for performance
    
    # Get filter options
    exams = Exam.objects.all().order_by('-start_date')[:10]
    classes = ClassRoom.objects.filter(is_active=True)
    subjects = Subject.objects.filter(is_active=True)
    
    # Calculate statistics
    total_results = results.count()
    avg_score = results.aggregate(avg=Avg('marks_obtained'))['avg'] or 0
    pass_count = sum(1 for r in results if r.is_pass)
    pass_rate = (pass_count / total_results * 100) if total_results > 0 else 0
    
    context = {
        'results': results,
        'exams': exams,
        'classes': classes,
        'subjects': subjects,
        'total_results': total_results,
        'avg_score': avg_score,
        'pass_count': pass_count,
        'pass_rate': pass_rate,
        'selected_exam': exam_id,
        'selected_class': class_id,
        'selected_subject': subject_id,
    }
    return render(request, 'results/result_list.html', context)


@login_required
def get_students_by_class(request):
    """AJAX endpoint to get students by class"""
    class_id = request.GET.get('class_id')
    if not class_id:
        return JsonResponse({'error': 'Class ID required'}, status=400)
    
    try:
        students = Student.objects.filter(
            class_assigned_id=class_id,
            is_active=True
        ).select_related('user').order_by('user__first_name', 'user__last_name')
        
        students_data = [
            {
                'id': student.id,
                'name': f"{student.user.get_full_name()} ({student.admission_number})"
            }
            for student in students
        ]
        
        return JsonResponse({'students': students_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@teacher_required
def result_create_view(request):
    """Create a new result entry"""
    if request.method == 'POST':
        student_id = request.POST.get('student')
        exam_id = request.POST.get('exam')
        subject_id = request.POST.get('subject')
        marks_obtained = request.POST.get('marks_obtained')
        max_marks = request.POST.get('max_marks', 100)
        is_absent = request.POST.get('is_absent') == 'on'
        remarks = request.POST.get('remarks', '')
        action = request.POST.get('action', 'save')  # 'save' or 'submit'

        try:
            student = Student.objects.get(pk=student_id)
            exam = Exam.objects.get(pk=exam_id)
            subject = Subject.objects.get(pk=subject_id)

            # Check if result already exists
            result, created = Result.objects.get_or_create(
                student=student,
                exam=exam,
                subject=subject,
                defaults={
                    'marks_obtained': float(marks_obtained) if not is_absent else 0,
                    'max_marks': int(max_marks),
                    'is_absent': is_absent,
                    'remarks': remarks,
                    'entered_by': request.user,
                    'status': 'DRAFT'
                }
            )

            # Update fields
            result.marks_obtained = float(marks_obtained) if not is_absent else 0
            result.max_marks = int(max_marks)
            result.is_absent = is_absent
            result.remarks = remarks

            # Status logic
            if action == 'submit':
                result.status = 'SUBMITTED'
            else:
                result.status = 'DRAFT'

            result.calculate_grade()
            result.save()

            if action == 'submit':
                # Notify HOD/Admin for approval
                admin_users = User.objects.filter(role='ADMIN')
                for admin in admin_users:
                    send_result_notification(
                        admin,
                        title='Result Submitted for Approval',
                        message=f'Result for {student.user.get_full_name()} ({subject.name}) has been submitted by {request.user.get_full_name()}.',
                        link='/results/'
                    )
                messages.success(request, f'Result submitted for approval for {student.user.get_full_name()}')
            elif created:
                messages.success(request, f'Result created for {student.user.get_full_name()}')
            else:
                messages.warning(request, f'Result updated for {student.user.get_full_name()}')

            return redirect('results:result_list')
        except Exception as e:
            messages.error(request, f'Error creating result: {str(e)}')
    
    # Get form data
    exams = Exam.objects.all().order_by('-start_date')[:10]
    classes = ClassRoom.objects.filter(is_active=True)
    subjects = Subject.objects.filter(is_active=True)

    # Prefill exam if provided in query params
    prefill_exam_id = request.GET.get('exam')

    context = {
        'exams': exams,
        'classes': classes,
        'subjects': subjects,
        'action': 'Create',
        'prefill_exam_id': prefill_exam_id
    }
    return render(request, 'results/result_form.html', context)


@login_required
@teacher_required
def result_update_view(request, pk):
    """Update an existing result"""
    result = get_object_or_404(Result, pk=pk)
    
    if request.method == 'POST':
        marks_obtained = request.POST.get('marks_obtained')
        if marks_obtained in [None, '']:
            marks_obtained = 0
        max_marks = request.POST.get('max_marks', 100)
        is_absent = request.POST.get('is_absent') == 'on'
        remarks = request.POST.get('remarks', '')
        action = request.POST.get('action', 'save')  # 'save', 'submit', 'approve', 'publish'

        try:
            result.marks_obtained = float(marks_obtained) if not is_absent else 0
            result.max_marks = int(max_marks)
            result.is_absent = is_absent
            result.remarks = remarks

            # Status logic
            if action == 'submit':
                result.status = 'SUBMITTED'
            elif action == 'approve':
                result.status = 'APPROVED'
            elif action == 'publish':
                result.status = 'PUBLISHED'
            else:
                result.status = 'DRAFT'

            result.calculate_grade()
            result.save()

            if action == 'submit':
                # Notify HOD/Admin for approval
                admin_users = User.objects.filter(role='ADMIN')
                for admin in admin_users:
                    send_result_notification(
                        admin,
                        title='Result Submitted for Approval',
                        message=f'Result for {result.student.user.get_full_name()} ({result.subject.name}) has been submitted by {request.user.get_full_name()}.',
                        link='/results/'
                    )
                messages.success(request, 'Result submitted for approval')
            elif action == 'approve':
                # Notify teacher who entered the result
                if result.entered_by:
                    send_result_notification(
                        result.entered_by,
                        title='Result Approved',
                        message=f'Result for {result.student.user.get_full_name()} ({result.subject.name}) has been approved.',
                        link='/results/'
                    )
                messages.success(request, 'Result approved')
            elif action == 'publish':
                # Notify student and parent
                send_result_notification(
                    result.student.user,
                    title='Result Published',
                    message=f'Your result for {result.subject.name} ({result.exam.name}) has been published.',
                    link='/results/'
                )
                if result.student.parent and result.student.parent.user:
                    send_result_notification(
                        result.student.parent.user,
                        title='Result Published',
                        message=f'Result for your child {result.student.user.get_full_name()} ({result.subject.name}) has been published.',
                        link='/results/'
                    )
                messages.success(request, 'Result published')
            else:
                messages.success(request, 'Result updated successfully')
            return redirect('results:result_list')
        except Exception as e:
            messages.error(request, f'Error updating result: {str(e)}')
    
    context = {
        'result': result,
        'action': 'Update'
    }
    return render(request, 'results/result_form.html', context)


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
    
    # Get all exam schedules for this exam
    schedules = ExamSchedule.objects.filter(exam=exam).select_related('class_room')

    # Restrict to only classes assigned to this teacher (unless admin)
    if request.user.is_teacher and not request.user.is_admin:
        teacher = getattr(request.user, 'teacher_profile', None)
        if teacher:
            # Classes where teacher is class_teacher
            class_teacher_ids = set(teacher.classes_as_teacher.values_list('id', flat=True))
            # Classes where teacher teaches at least one subject
            subject_class_ids = set(teacher.teaching_subjects.values_list('class_room_id', flat=True))
            allowed_class_ids = class_teacher_ids.union(subject_class_ids)
            schedules = schedules.filter(class_room_id__in=allowed_class_ids)

    # Get unique class rooms from filtered schedules
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
        actual_results = Result.objects.filter(exam=exam, student__class_assigned=class_room).count()
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
    # Restrict teacher access to only their assigned classes
    if request.user.is_teacher and not request.user.is_admin:
        teacher = getattr(request.user, 'teacher_profile', None)
        if teacher:
            allowed_class_ids = set(teacher.classes_as_teacher.values_list('id', flat=True)).union(
                set(teacher.teaching_subjects.values_list('class_room_id', flat=True))
            )
            if class_room.id not in allowed_class_ids:
                messages.error(request, 'You do not have permission to access this class.')
                return redirect('dashboard')
    
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
@require_POST
def save_results_view(request, exam_id, class_id):
    """Save results via AJAX"""
    import logging
    logger = logging.getLogger('django')
    try:
        exam = get_object_or_404(Exam, pk=exam_id)
        class_room = get_object_or_404(ClassRoom, pk=class_id)

        # Restrict teacher access to only their assigned classes
        if request.user.is_teacher and not request.user.is_admin:
            teacher = getattr(request.user, 'teacher_profile', None)
            if teacher:
                allowed_class_ids = set(teacher.classes_as_teacher.values_list('id', flat=True)).union(
                    set(teacher.teaching_subjects.values_list('class_room_id', flat=True))
                )
                if class_room.id not in allowed_class_ids:
                    logger.warning(f"User {request.user} tried to save results for unassigned class {class_room.id}")
                    return JsonResponse({'success': False, 'error': 'You do not have permission to save results for this class.'})

        data = json.loads(request.body)
        logger.info(f"Received save results data: {data}")
        subject_id = data.get('subject')
        results_data = data.get('results', [])

        subject = get_object_or_404(Subject, pk=subject_id)

        for result_data in results_data:
            student = Student.objects.get(pk=result_data['student'])
            result, created = Result.objects.get_or_create(
                student=student,
                exam=exam,
                subject=subject,
                defaults={'entered_by': request.user}
            )
            logger.info(f"Result for student {student.id}, subject {subject.id}: created={created}")
            # Always update all fields and save, even if unchanged
            result.is_absent = result_data.get('is_absent', False)
            if not result.is_absent:
                result.marks_obtained = float(result_data.get('marks', 0))
                result.grade = result_data.get('grade', '')
            else:
                result.marks_obtained = 0
                result.grade = 'ABS'
            result.remarks = result_data.get('remarks', '')
            result.entered_by = request.user
            result.save(force_update=not created)
            logger.info(f"Saved result: {result}")

        return JsonResponse({'success': True})

    except Exception as e:
        logger.error(f"Error saving results: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@teacher_required
def generate_reports_view(request, exam_id, class_id):
    """Generate report cards for a class"""
    exam = get_object_or_404(Exam, pk=exam_id)
    class_room = get_object_or_404(ClassRoom, pk=class_id)
    # Restrict teacher access to only their assigned classes
    if request.user.is_teacher and not request.user.is_admin:
        teacher = getattr(request.user, 'teacher_profile', None)
        if teacher:
            allowed_class_ids = set(teacher.classes_as_teacher.values_list('id', flat=True)).union(
                set(teacher.teaching_subjects.values_list('class_room_id', flat=True))
            )
            if class_room.id not in allowed_class_ids:
                messages.error(request, 'You do not have permission to access this class.')
                return redirect('dashboard')
    
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
    
    # Calculate class positions
    report_cards = ReportCard.objects.filter(
        exam=exam,
        student__class_assigned=class_room
    ).order_by('-percentage')
    
    for index, report_card in enumerate(report_cards, start=1):
        report_card.class_position = index
        report_card.save()
    
    messages.success(request, f'Successfully generated {count} report cards with positions!')
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
    return redirect('results:generate_reports', exam_id=exam_id, class_id=student.class_assigned.pk)


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
        student__class_assigned=class_room
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

    # Calculate class position if not set
    if not report_card.class_position and student.class_assigned:
        class_reports = ReportCard.objects.filter(
            exam=exam,
            student__class_assigned=student.class_assigned
        ).order_by('-percentage')
        for index, rc in enumerate(class_reports, start=1):
            if rc.id == report_card.id:
                report_card.class_position = index
                report_card.save()
                break

    total_students = student.class_assigned.students.count() if student.class_assigned else 1

    # School info from DB
    from apps.config.models import SchoolInfo
    school_info_obj = SchoolInfo.objects.order_by('-updated_at').first()
    school_info = {
        'name': school_info_obj.name if school_info_obj else '',
        'address': school_info_obj.address if school_info_obj else '',
        'phone': school_info_obj.phone if school_info_obj else '',
        'email': school_info_obj.email if school_info_obj else '',
        'motto': school_info_obj.motto if school_info_obj else '',
        'logo': school_info_obj.logo if school_info_obj and school_info_obj.logo else None,
    }
    headmaster = school_info_obj.headmaster if school_info_obj and school_info_obj.headmaster else None
    class_teacher = student.class_assigned.class_teacher if student.class_assigned and student.class_assigned.class_teacher else None

    # Per-subject ranking
    subject_ranks = {}
    for result in results:
        subject_results = Result.objects.filter(
            exam=exam,
            subject=result.subject,
            student__class_assigned=student.class_assigned
        ).order_by('-marks_obtained')
        rank = None
        for idx, r in enumerate(subject_results, start=1):
            if r.student_id == student.id:
                rank = idx
                break
        subject_ranks[result.subject.id] = {
            'rank': rank,
            'total': subject_results.count()
        }

    # Determine which template to use based on education level
    template_name = 'results/report_card.html'  # Default
    if student.class_assigned:
        level = student.class_assigned.level
        if level == 'PRIMARY':
            template_name = 'results/report_card_primary.html'
        elif level in ['SECONDARY', 'HIGH_SCHOOL']:
            template_name = 'results/report_card_secondary.html'
        elif level == 'UNIVERSITY':
            template_name = 'results/report_card_university.html'

    context = {
        'student': student,
        'exam': exam,
        'report_card': report_card,
        'results': results,
        'total_students': total_students,
        'school_info': school_info,
        'headmaster': headmaster,
        'class_teacher': class_teacher,
        'subject_ranks': subject_ranks,
    }
    return render(request, template_name, context)


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


@login_required
@teacher_required
@require_POST
def update_report_comments_view(request, report_id):
    """Update teacher and principal comments on a report card"""
    try:
        report_card = get_object_or_404(ReportCard, pk=report_id)
        data = json.loads(request.body)
        
        if 'teacher_comment' in data:
            report_card.teacher_comment = data['teacher_comment']
        if 'principal_comment' in data:
            report_card.principal_comment = data['principal_comment']
        if 'attendance_days' in data:
            report_card.attendance_days = data['attendance_days']
        if 'total_school_days' in data:
            report_card.total_school_days = data['total_school_days']
        
        report_card.save()
        
        return JsonResponse({'success': True, 'message': 'Comments updated successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@teacher_required
def bulk_print_reports_view(request, exam_id, class_id):
    """Generate a page with all report cards for printing"""
    exam = get_object_or_404(Exam, pk=exam_id)
    class_room = get_object_or_404(ClassRoom, pk=class_id)
    
    students = class_room.students.all().order_by('roll_number', 'user__last_name')
    
    # Prepare data for all students
    student_reports = []
    for student in students:
        report_card, created = ReportCard.objects.get_or_create(
            student=student,
            exam=exam
        )
        if created:
            report_card.calculate_totals()
        
        results = Result.objects.filter(student=student, exam=exam).order_by('subject__name')
        student_reports.append({
            'student': student,
            'report_card': report_card,
            'results': results,
        })
    
    # Determine template based on level
    template_name = 'results/bulk_print_reports.html'
    if class_room.level == 'PRIMARY':
        template_name = 'results/bulk_print_primary.html'
    elif class_room.level in ['SECONDARY', 'HIGH_SCHOOL']:
        template_name = 'results/bulk_print_secondary.html'
    elif class_room.level == 'UNIVERSITY':
        template_name = 'results/bulk_print_university.html'
    
    total_students = class_room.students.count()
    
    context = {
        'exam': exam,
        'class_room': class_room,
        'student_reports': student_reports,
        'total_students': total_students,
    }
    return render(request, template_name, context)
