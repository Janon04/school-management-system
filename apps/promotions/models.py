"""
Student Promotion Management Models
"""
from django.db import models
from apps.students.models import Student
from apps.classes.models import ClassRoom, AcademicYear


class Promotion(models.Model):
    """
    Student class promotion records
    """
    
    STATUS_CHOICES = (
        ('PROMOTED', 'Promoted'),
        ('DETAINED', 'Detained/Repeated'),
        ('GRADUATED', 'Graduated'),
    )
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='promotions'
    )
    
    from_class = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name='promotions_from',
        help_text='Previous class'
    )
    
    to_class = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name='promotions_to',
        null=True,
        blank=True,
        help_text='New class (null if graduated)'
    )
    
    from_academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='promotions_from'
    )
    
    to_academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='promotions_to'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PROMOTED'
    )
    
    remarks = models.TextField(blank=True)
    promoted_on = models.DateField(auto_now_add=True)
    promoted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True
    )
    
    class Meta:
        ordering = ['-promoted_on']
        verbose_name = 'Promotion'
        verbose_name_plural = 'Promotions'
    
    def __str__(self):
        if self.status == 'GRADUATED':
            return f"{self.student.admission_number} - Graduated from {self.from_class}"
        return f"{self.student.admission_number} - {self.from_class} to {self.to_class}"
    
    def save(self, *args, **kwargs):
        """Update student's current class after promotion"""
        super().save(*args, **kwargs)
        if self.status == 'PROMOTED' and self.to_class:
            self.student.class_assigned = self.to_class
            self.student.academic_year = self.to_academic_year
            self.student.save()
