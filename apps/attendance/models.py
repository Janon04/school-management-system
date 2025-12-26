"""
Attendance Management Models
"""
from django.db import models
from apps.students.models import Student
from apps.classes.models import ClassRoom


class Attendance(models.Model):
    """
    Daily attendance records for students
    """
    
    STATUS_CHOICES = (
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Excused', 'Excused'),
    )
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    
    class_room = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    remarks = models.TextField(blank=True)
    marked_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True
    )
    marked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', 'student']
        unique_together = ['student', 'date']
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendance Records'
        indexes = [
            models.Index(fields=['date', 'class_room']),
            models.Index(fields=['student', 'date']),
        ]
    
    def __str__(self):
        return f"{self.student.admission_number} - {self.date} - {self.status}"


class AttendanceSummary(models.Model):
    """
    Monthly attendance summary for students
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendance_summaries'
    )
    month = models.DateField(help_text='First day of the month')
    total_days = models.IntegerField(default=0)
    present_days = models.IntegerField(default=0)
    absent_days = models.IntegerField(default=0)
    late_days = models.IntegerField(default=0)
    excused_days = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['student', 'month']
        verbose_name = 'Attendance Summary'
        verbose_name_plural = 'Attendance Summaries'
    
    def __str__(self):
        return f"{self.student.admission_number} - {self.month.strftime('%B %Y')}"
    
    @property
    def attendance_percentage(self):
        if self.total_days == 0:
            return 0
        return (self.present_days / self.total_days) * 100
