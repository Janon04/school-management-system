from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Exam, ExamSchedule


@login_required
def exam_list_view(request):
    """List all exams"""
    exams = Exam.objects.all().order_by('-start_date')
    return render(request, 'exams/exam_list.html', {'exams': exams})


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
