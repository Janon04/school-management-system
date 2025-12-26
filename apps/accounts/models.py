"""
Custom User Model with Role-Based Access Control
Supports multiple user types: Admin, Teacher, Student, Parent, Staff
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    Extended User model with role-based authentication
    Each user has a specific role that determines their permissions and interface
    """
    
    ROLE_CHOICES = (
        ('ADMIN', 'Administrator'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
        ('PARENT', 'Parent'),
        ('STAFF', 'Staff'),
    )
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES,
        help_text='User role determines access permissions'
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True,
        help_text='Contact phone number'
    )
    
    address = models.TextField(blank=True, help_text='Physical address')
    
    profile_picture = models.ImageField(
        upload_to='profiles/', 
        blank=True, 
        null=True,
        help_text='User profile photo'
    )
    
    date_of_birth = models.DateField(
        null=True, 
        blank=True,
        help_text='Date of birth'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user should be treated as active.'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def get_full_name(self):
        """Return the user's full name."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username
    
    @property
    def is_admin(self):
        """Check if user is an administrator"""
        return self.role == 'ADMIN'
    
    @property
    def is_teacher(self):
        """Check if user is a teacher"""
        return self.role == 'TEACHER'
    
    @property
    def is_student(self):
        """Check if user is a student"""
        return self.role == 'STUDENT'
    
    @property
    def is_parent(self):
        """Check if user is a parent"""
        return self.role == 'PARENT'
    
    @property
    def is_staff_member(self):
        """Check if user is a staff member (not Django staff)"""
        return self.role == 'STAFF'


class AuditLog(models.Model):
    """
    Track important actions performed by users
    Useful for security and accountability
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
    
    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"
