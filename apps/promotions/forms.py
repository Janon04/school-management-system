"""
Forms for Promotions
"""
from django import forms
from .models import Promotion
from apps.students.models import Student
from apps.classes.models import ClassRoom, AcademicYear


class PromotionForm(forms.ModelForm):
    """Form for creating and editing promotions"""
    
    class Meta:
        model = Promotion
        fields = ['student', 'from_class', 'to_class', 'from_academic_year', 'to_academic_year', 'status', 'remarks']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'from_class': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'to_class': forms.Select(attrs={
                'class': 'form-select'
            }),
            'from_academic_year': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'to_academic_year': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter any remarks or notes about this promotion'
            })
        }
        labels = {
            'student': 'Student',
            'from_class': 'From Class',
            'to_class': 'To Class',
            'from_academic_year': 'From Academic Year',
            'to_academic_year': 'To Academic Year',
            'status': 'Promotion Status',
            'remarks': 'Remarks (Optional)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter active students
        self.fields['student'].queryset = Student.objects.filter(is_active=True).select_related('user')
        # Filter active classes
        self.fields['from_class'].queryset = ClassRoom.objects.filter(is_active=True)
        self.fields['to_class'].queryset = ClassRoom.objects.filter(is_active=True)
        # Order academic years
        self.fields['from_academic_year'].queryset = AcademicYear.objects.all().order_by('-start_date')
        self.fields['to_academic_year'].queryset = AcademicYear.objects.all().order_by('-start_date')
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        to_class = cleaned_data.get('to_class')
        
        # If status is PROMOTED, to_class is required
        if status == 'PROMOTED' and not to_class:
            raise forms.ValidationError('Promoted students must have a destination class.')
        
        # If status is GRADUATED, to_class should be null
        if status == 'GRADUATED' and to_class:
            cleaned_data['to_class'] = None
        
        return cleaned_data
