"""
Results Management Models
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.students.models import Student
from apps.classes.models import Subject
from apps.exams.models import Exam, ExamSchedule


class Result(models.Model):
    """
    Individual exam results/marks
    """
    
    GRADE_CHOICES = (
        ('A', 'A - Excellent'),
        ('B', 'B - Very Good'),
        ('C', 'C - Good'),
        ('D', 'D - Satisfactory'),
        ('E', 'E - Pass'),
        ('F', 'F - Fail'),
    )
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='results'
    )
    
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='results'
    )
    
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='results'
    )
    
    marks_obtained = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    max_marks = models.IntegerField(default=100)
    
    grade = models.CharField(
        max_length=1,
        choices=GRADE_CHOICES,
        blank=True
    )
    
    remarks = models.TextField(blank=True)
    
    is_absent = models.BooleanField(
        default=False,
        help_text='Was student absent for this exam?'
    )
    
    entered_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-exam__start_date', 'student', 'subject']
        unique_together = ['student', 'exam', 'subject']
        verbose_name = 'Result'
        verbose_name_plural = 'Results'
        indexes = [
            models.Index(fields=['student', 'exam']),
        ]
    
    def __str__(self):
        return f"{self.student.admission_number} - {self.subject.name} - {self.marks_obtained}/{self.max_marks}"
    
    @property
    def percentage(self):
        """Calculate percentage"""
        if self.max_marks == 0:
            return 0
        return (float(self.marks_obtained) / self.max_marks) * 100
    
    @property
    def is_pass(self):
        """Check if student passed"""
        return self.marks_obtained >= self.subject.pass_mark
    
    def calculate_grade(self):
        """Auto-calculate grade based on percentage"""
        pct = self.percentage
        if pct >= 80:
            return 'A'
        elif pct >= 70:
            return 'B'
        elif pct >= 60:
            return 'C'
        elif pct >= 50:
            return 'D'
        elif pct >= 40:
            return 'E'
        else:
            return 'F'
    
    def save(self, *args, **kwargs):
        """Auto-calculate grade before saving"""
        if not self.is_absent and not self.grade:
            self.grade = self.calculate_grade()
        super().save(*args, **kwargs)


class ReportCard(models.Model):
    """
    Consolidated report card for a student for an exam
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='report_cards'
    )
    
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='report_cards'
    )
    
    total_marks = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    marks_obtained = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overall_grade = models.CharField(max_length=1, blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, help_text='For university level')
    rank = models.IntegerField(null=True, blank=True)
    class_position = models.IntegerField(null=True, blank=True, help_text='Position in class')
    remarks = models.TextField(blank=True)
    teacher_comment = models.TextField(blank=True, help_text='Class teacher comment')
    principal_comment = models.TextField(blank=True, help_text='Principal/Head comment')
    attendance_days = models.IntegerField(null=True, blank=True, help_text='Days attended')
    total_school_days = models.IntegerField(null=True, blank=True, help_text='Total school days')
    generated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'exam']
        ordering = ['-exam__start_date', 'rank']
        verbose_name = 'Report Card'
        verbose_name_plural = 'Report Cards'
    
    def __str__(self):
        return f"{self.student.admission_number} - {self.exam.name} - {self.percentage}%"
    
    def calculate_totals(self):
        """Calculate totals from individual results"""
        results = Result.objects.filter(student=self.student, exam=self.exam, is_absent=False)
        self.total_marks = sum([r.max_marks for r in results])
        self.marks_obtained = sum([r.marks_obtained for r in results])
        if self.total_marks > 0:
            self.percentage = (float(self.marks_obtained) / float(self.total_marks)) * 100
        
        # Calculate GPA for university level (4.0 scale)
        if self.student.class_assigned and self.student.class_assigned.level == 'UNIVERSITY':
            self.gpa = self.calculate_gpa(results)
        
        self.save()
    
    def calculate_gpa(self, results):
        """Calculate GPA on a 4.0 scale for university level"""
        if not results:
            return 0.0
        
        total_credit_points = 0
        total_credits = 0
        
        for result in results:
            # Assume each subject has equal credits (can be customized)
            credits = 3  # Default credit hours
            percentage = result.percentage
            
            # Convert percentage to grade points (4.0 scale)
            if percentage >= 80:
                grade_point = 4.0
            elif percentage >= 70:
                grade_point = 3.5
            elif percentage >= 60:
                grade_point = 3.0
            elif percentage >= 50:
                grade_point = 2.5
            elif percentage >= 40:
                grade_point = 2.0
            else:
                grade_point = 0.0
            
            total_credit_points += (grade_point * credits)
            total_credits += credits
        
        return round(total_credit_points / total_credits, 2) if total_credits > 0 else 0.0
