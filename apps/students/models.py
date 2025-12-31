"""
Student Management Models
Handles student profiles, enrollment, and academic information
"""
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from apps.accounts.models import User
from apps.classes.models import ClassRoom, AcademicYear
from apps.parents.models import Parent
import random
import string


def generate_admission_number():
    """Generate unique admission number"""
    year = str(timezone.now().year)
    random_digits = ''.join(random.choices(string.digits, k=6))
    return f"ADM{year}{random_digits}"


class Student(models.Model):
    """
    Student profile with academic and personal information
    """
    
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    )
    
    # Link to User account
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    
    # Basic Information
    admission_number = models.CharField(
        max_length=20,
        unique=True,
        default=generate_admission_number,
        help_text='Unique student identification number'
    )

    middle_name = models.CharField(
        max_length=50,
        blank=True,
        help_text='Middle name (optional)'
    )

    roll_number = models.CharField(
        max_length=20,
        blank=True,
        help_text='Class roll number'
    )

    date_of_birth = models.DateField(help_text='Student date of birth')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(
        max_length=3,
        choices=BLOOD_GROUP_CHOICES,
        blank=True
    )
    
    # Contact Information
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=17)
    emergency_contact_relation = models.CharField(max_length=50)
    
    # Academic Information
    class_assigned = models.ForeignKey(
        ClassRoom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )
    
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='students'
    )
    
    admission_date = models.DateField(help_text='Date of admission')
    
    # Parent/Guardian Information
    parent = models.ForeignKey(
        'parents.Parent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    
    # Additional Information
    nationality = models.CharField(max_length=50, default='Kenya')
    religion = models.CharField(max_length=50, blank=True)
    previous_school = models.CharField(max_length=200, blank=True)
    medical_conditions = models.TextField(
        blank=True,
        help_text='Any medical conditions or allergies'
    )
    
    # Documents
    birth_certificate = models.FileField(
        upload_to='students/documents/',
        blank=True,
        null=True
    )
    photo = models.ImageField(
        upload_to='students/photos/',
        blank=True,
        null=True
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text='Is student currently enrolled?'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['admission_number']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        indexes = [
            models.Index(fields=['admission_number']),
            models.Index(fields=['class_assigned']),
        ]
    
    def __str__(self):
        return f"{self.admission_number} - {self.user.get_full_name()}"
    
    @property
    def age(self):
        """Calculate student age"""
        from django.utils import timezone
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def full_name(self):
        """Get student full name"""
        return self.user.get_full_name()


class StudentDocument(models.Model):
    """
    Additional documents for students
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    title = models.CharField(max_length=100)
    document = models.FileField(upload_to='students/documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Student Document'
        verbose_name_plural = 'Student Documents'
    
    def __str__(self):
        return f"{self.student.admission_number} - {self.title}"


from django.utils import timezone
