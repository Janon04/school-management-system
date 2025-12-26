"""
Non-Teaching Staff Management Models
"""
from django.db import models
from apps.accounts.models import User


class Staff(models.Model):
    """
    Non-teaching staff (Accountant, Librarian, Lab Assistant, etc.)
    """
    
    DEPARTMENT_CHOICES = (
        ('ADMIN', 'Administration'),
        ('ACCOUNTS', 'Accounts'),
        ('LIBRARY', 'Library'),
        ('LAB', 'Laboratory'),
        ('TRANSPORT', 'Transport'),
        ('SECURITY', 'Security'),
        ('MAINTENANCE', 'Maintenance'),
        ('CANTEEN', 'Canteen'),
        ('OTHER', 'Other'),
    )
    
    # Link to User account
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='staff_profile'
    )
    
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        help_text='Unique staff ID'
    )
    
    department = models.CharField(
        max_length=20,
        choices=DEPARTMENT_CHOICES
    )
    
    designation = models.CharField(
        max_length=100,
        help_text='Job title/position'
    )
    
    joining_date = models.DateField()
    
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['department', 'employee_id']
        verbose_name = 'Staff Member'
        verbose_name_plural = 'Staff Members'
    
    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()} ({self.designation})"
