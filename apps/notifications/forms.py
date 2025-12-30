"""
Forms for Notifications and Notices
"""
from django import forms
from .models import Notice, Notification, Message
from apps.accounts.models import User


class NoticeForm(forms.ModelForm):
    """Form for creating and editing notices"""
    
    class Meta:
        model = Notice
        fields = ['title', 'message', 'target_audience', 'priority', 'attachment', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter notice title',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter notice message',
                'rows': 6,
                'required': True
            }),
            'target_audience': forms.Select(attrs={
                'class': 'form-select'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'title': 'Notice Title',
            'message': 'Message',
            'target_audience': 'Target Audience',
            'priority': 'Priority Level',
            'attachment': 'Attachment (Optional)',
            'is_active': 'Active (Visible to users)'
        }


class NotificationForm(forms.ModelForm):
    """Form for creating notifications for users"""
    
    RECIPIENT_CHOICES = (
        ('', 'Select recipient type...'),
        ('ALL', 'Everyone (All Users)'),
        ('ADMIN', 'All Administrators'),
        ('TEACHER', 'All Teachers'),
        ('STUDENT', 'All Students'),
        ('PARENT', 'All Parents'),
        ('STAFF', 'All Staff Members'),
        ('CUSTOM', 'Custom Selection'),
    )
    
    recipient_type = forms.ChoiceField(
        choices=RECIPIENT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'handleRecipientTypeChange()'
        }),
        required=True,
        label='Send To'
    )
    
    # Custom users selection (only shown when CUSTOM is selected)
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all().order_by('role', 'first_name', 'last_name'),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'size': '12',
            'id': 'customUsersSelect'
        }),
        required=False,
        label='Select Specific Users'
    )
    
    class Meta:
        model = Notification
        fields = ['title', 'message', 'notification_type', 'link']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter notification title',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter notification message',
                'rows': 4,
                'required': True
            }),
            'notification_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional: URL to redirect when clicked'
            })
        }
        labels = {
            'title': 'Notification Title',
            'message': 'Message',
            'notification_type': 'Type',
            'link': 'Link (Optional)'
        }
