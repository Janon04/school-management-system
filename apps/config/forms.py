from django import forms
from .models import SchoolInfo

class SchoolInfoForm(forms.ModelForm):
    class Meta:
        model = SchoolInfo
        fields = [
            'name', 'address', 'phone', 'email', 'motto', 'headmaster', 'logo',
            'principal_signature', 'class_teacher_signature', 'school_stamp',
            'principal_name', 'class_teacher_name',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'School Name'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123 School Street, City, Country'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'info@school.com'}),
            'motto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'School Motto'}),
            'headmaster': forms.Select(attrs={'class': 'form-select'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'principal_signature': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'class_teacher_signature': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'school_stamp': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'principal_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Principal Name (Override)'}),
            'class_teacher_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Class Teacher Name (Override)'}),
        }
