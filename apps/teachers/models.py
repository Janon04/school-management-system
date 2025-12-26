"""
Teacher Management Models
"""
from django.db import models
from apps.accounts.models import User
from apps.classes.models import Subject


class Teacher(models.Model):
    """
    Teacher profile with professional information
    """
    
    EMPLOYMENT_TYPE_CHOICES = (
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'),
    )
    
    # Link to User account
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile'
    )
    
    # Professional Information
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        help_text='Unique teacher ID'
    )
    
    qualification = models.CharField(
        max_length=200,
        help_text='Highest educational qualification'
    )
    
    specialization = models.CharField(
        max_length=200,
        blank=True,
        help_text='Area of specialization'
    )
    
    experience_years = models.IntegerField(
        default=0,
        help_text='Years of teaching experience'
    )
    
    # Employment Details
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='FULL_TIME'
    )
    
    joining_date = models.DateField(help_text='Date of joining')
    
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Monthly salary'
    )
    
    # Subjects taught
    subjects = models.ManyToManyField(
        Subject,
        related_name='teachers',
        blank=True,
        help_text='Subjects this teacher can teach'
    )
    
    # Additional Information
    certifications = models.TextField(
        blank=True,
        help_text='Professional certifications'
    )
    
    bio = models.TextField(
        blank=True,
        help_text='Short biography'
    )
    
    # Documents
    resume = models.FileField(
        upload_to='teachers/resumes/',
        blank=True,
        null=True
    )
    
    certificates = models.FileField(
        upload_to='teachers/certificates/',
        blank=True,
        null=True
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['employee_id']
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'
    
    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def total_classes(self):
        """Count total classes assigned"""
        return self.classes_as_teacher.count()
