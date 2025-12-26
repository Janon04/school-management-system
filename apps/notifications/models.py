"""
Notifications and Notice Board Models
"""
from django.db import models
from apps.accounts.models import User


class Notice(models.Model):
    """
    School notice board
    """
    
    TARGET_CHOICES = (
        ('ALL', 'Everyone'),
        ('STUDENTS', 'Students Only'),
        ('TEACHERS', 'Teachers Only'),
        ('PARENTS', 'Parents Only'),
        ('STAFF', 'Staff Only'),
    )
    
    PRIORITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    target_audience = models.CharField(
        max_length=20,
        choices=TARGET_CHOICES,
        default='ALL'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='MEDIUM'
    )
    
    posted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='notices_posted'
    )
    
    attachment = models.FileField(
        upload_to='notices/',
        blank=True,
        null=True
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notice'
        verbose_name_plural = 'Notices'
    
    def __str__(self):
        return f"{self.title} ({self.get_priority_display()})"


class Notification(models.Model):
    """
    Personal notifications for users
    """
    
    TYPE_CHOICES = (
        ('INFO', 'Information'),
        ('SUCCESS', 'Success'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('REMINDER', 'Reminder'),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='INFO'
    )
    
    link = models.CharField(
        max_length=255,
        blank=True,
        help_text='URL to redirect when clicked'
    )
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class Message(models.Model):
    """
    Internal messaging system
    """
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='messages_sent'
    )
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='messages_received'
    )
    
    subject = models.CharField(max_length=200)
    body = models.TextField()
    
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
    
    def __str__(self):
        return f"From {self.sender} to {self.recipient} - {self.subject}"
