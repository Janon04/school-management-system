"""
Exam Management Models
"""
from django.db import models
from apps.classes.models import ClassRoom, Subject, AcademicYear


class Exam(models.Model):
    """
    Exam/Test definition
    """
    EXAM_STATUS_CHOICES = (
        ('SCHEDULED', 'Scheduled'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
        ('POSTPONED', 'Postponed'),
    )

    status = models.CharField(
        max_length=12,
        choices=EXAM_STATUS_CHOICES,
        default='SCHEDULED',
        help_text='Current status of the exam.'
    )
    
    EXAM_TYPE_CHOICES = (
        ('MID_TERM', 'Mid Term'),
        ('FINAL', 'Final Exam'),
        ('QUIZ', 'Quiz'),
        ('ASSIGNMENT', 'Assignment'),
        ('PRACTICAL', 'Practical'),
        ('OTHER', 'Other'),
    )
    
    name = models.CharField(max_length=100)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES)
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='exams'
    )
    term = models.CharField(
        max_length=20,
        help_text='e.g., Term 1, Semester 1'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)
    is_published = models.BooleanField(
        default=False,
        help_text='Are results published to students?'
    )
    exam_file = models.FileField(
        upload_to='exams/files/',
        blank=True,
        null=True,
        help_text='Upload exam file (PDF or Word)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Exam'
        verbose_name_plural = 'Exams'
    
    def __str__(self):
        return f"{self.name} - {self.term} ({self.academic_year})"


class ExamSchedule(models.Model):
    """
    Schedule for individual exam papers
    """
    SCHEDULE_STATUS_CHOICES = (
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('POSTPONED', 'Postponed'),
        ('CANCELLED', 'Cancelled'),
    )

    status = models.CharField(
        max_length=12,
        choices=SCHEDULE_STATUS_CHOICES,
        default='SCHEDULED',
        help_text='Current status of the exam schedule.'
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    
    class_room = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE
    )
    
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )
    
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=20, blank=True)
    max_marks = models.IntegerField(default=100)
    pass_marks = models.IntegerField(default=40)
    
    class Meta:
        ordering = ['exam_date', 'start_time']
        unique_together = ['exam', 'class_room', 'subject']
        verbose_name = 'Exam Schedule'
        verbose_name_plural = 'Exam Schedules'
    
    def __str__(self):
        return f"{self.exam.name} - {self.subject.name} - {self.class_room}"
