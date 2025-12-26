"""
Parent/Guardian Management Models
"""
from django.db import models
from apps.accounts.models import User


class Parent(models.Model):
    """
    Parent/Guardian profile
    """
    
    RELATION_CHOICES = (
        ('FATHER', 'Father'),
        ('MOTHER', 'Mother'),
        ('GUARDIAN', 'Legal Guardian'),
        ('OTHER', 'Other'),
    )
    
    # Link to User account
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='parent_profile'
    )
    
    # Personal Information
    relation = models.CharField(
        max_length=20,
        choices=RELATION_CHOICES,
        help_text='Relationship to student'
    )
    
    occupation = models.CharField(
        max_length=100,
        blank=True,
        help_text='Current occupation'
    )
    
    employer = models.CharField(
        max_length=200,
        blank=True,
        help_text='Employer name'
    )
    
    office_address = models.TextField(
        blank=True,
        help_text='Office address'
    )
    
    annual_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Annual income (optional)'
    )
    
    # Emergency Contact (alternative person)
    alt_contact_name = models.CharField(
        max_length=100,
        blank=True,
        help_text='Alternative contact person'
    )
    alt_contact_phone = models.CharField(
        max_length=17,
        blank=True
    )
    alt_contact_relation = models.CharField(
        max_length=50,
        blank=True
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__last_name', 'user__first_name']
        verbose_name = 'Parent'
        verbose_name_plural = 'Parents'
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_relation_display()})"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def total_children(self):
        """Count children linked to this parent"""
        return self.children.filter(is_active=True).count()
