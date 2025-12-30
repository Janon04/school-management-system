from django.contrib import messages
from apps.accounts.decorators import teacher_required
@teacher_required
def exam_schedule_edit_view(request, pk):
    schedule = get_object_or_404(ExamSchedule, pk=pk)
    if request.method == 'POST':
        form = ExamScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule updated successfully!')
            return redirect('exams:exam_schedule_list')
    else:
        form = ExamScheduleForm(instance=schedule)
    return render(request, 'exams/exam_schedule_form.html', {'form': form, 'exam': schedule.exam})

# --- Delete Exam Schedule View ---
@teacher_required
def exam_schedule_delete_view(request, pk):
    schedule = get_object_or_404(ExamSchedule, pk=pk)
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Schedule deleted successfully!')
        return redirect('exams:exam_schedule_list')
    return render(request, 'exams/exam_schedule_confirm_delete.html', {'schedule': schedule})
# --- Exam Schedule List View (Timetable) ---
from django.contrib.auth.decorators import login_required
@login_required
def exam_schedule_list_view(request):
    from .models import ExamSchedule
    schedules = ExamSchedule.objects.select_related('class_room', 'subject').order_by('exam_date', 'start_time')
    return render(request, 'exams/exam_schedule_list.html', {'schedules': schedules})
from .forms import ExamScheduleForm
from apps.accounts.decorators import teacher_required
# --- Add Exam Schedule View ---
@teacher_required
def exam_schedule_create_view(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    from django.contrib import messages
    if request.method == 'POST':
        form = ExamScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.exam = exam
            schedule.save()
            messages.success(request, 'Exam schedule added successfully!')
            return redirect('exams:exam_schedule_add', exam_id=exam.id)
    else:
        form = ExamScheduleForm(initial={'exam': exam})
    return render(request, 'exams/exam_schedule_form.html', {'form': form, 'exam': exam})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Exam, ExamSchedule
from .forms import ExamForm


@login_required
def exam_list_view(request):
    """List all exams (teachers see only exams for their classes)"""
    if hasattr(request.user, 'teacher_profile'):
        # Get all class IDs this teacher is assigned to
        class_ids = request.user.teacher_profile.classes_as_teacher.values_list('id', flat=True)
        # Exams that have schedules for these classes
        exams = Exam.objects.filter(schedules__class_room_id__in=class_ids).distinct().order_by('-start_date')
    else:
        exams = Exam.objects.all().order_by('-start_date')
    return render(request, 'exams/exam_list.html', {'exams': exams})


from apps.accounts.decorators import teacher_required

# --- Create Exam View ---
@teacher_required
def exam_create_view(request):
    """Create a new exam"""
    if request.method == 'POST':
        form = ExamForm(request.POST, request.FILES)
        if form.is_valid():
            exam = form.save()
            return redirect('exams:exam_detail', exam_id=exam.id)
    else:
        form = ExamForm()
    return render(request, 'exams/exam_form.html', {'form': form})


# --- Update Exam View ---
@login_required
def exam_update_view(request, exam_id):
    """Update an existing exam"""
    exam = get_object_or_404(Exam, pk=exam_id)
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            return redirect('exams:exam_detail', exam_id=exam.id)
    else:
        form = ExamForm(instance=exam)
    return render(request, 'exams/exam_form.html', {'form': form, 'exam': exam})


@login_required
def exam_detail_view(request, exam_id):
    """View exam details"""
    exam = get_object_or_404(Exam, pk=exam_id)
    schedules = ExamSchedule.objects.filter(exam=exam).order_by('exam_date', 'start_time')
    return render(request, 'exams/exam_detail.html', {'exam': exam, 'schedules': schedules})


@login_required
def exam_schedule_view(request, exam_id):
    """View exam schedule"""
    exam = Exam.objects.get(pk=exam_id)
    schedules = ExamSchedule.objects.filter(exam=exam).order_by('exam_date', 'start_time')
    return render(request, 'exams/exam_schedule.html', {'exam': exam, 'schedules': schedules})
