"""
Forms for Exam Management
"""
from django import forms
from .models import Exam, ExamSchedule
from apps.classes.models import AcademicYear


class ExamForm(forms.ModelForm):
    """Form for creating and updating exam records"""
    
    class Meta:
        model = Exam
        fields = [
            'name', 'exam_type', 'academic_year', 'term',
            'start_date', 'end_date', 'description', 'is_published', 'exam_file', 'status'
        ]
        widgets = {
            'exam_file': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            # ...existing code...
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., End Term 1 Examination 2024'
            }),
            'exam_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'academic_year': forms.Select(attrs={
                'class': 'form-select'
            }),
            'term': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Term 1, Semester 1'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of the exam (optional)'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get current academic years
        self.fields['academic_year'].queryset = AcademicYear.objects.filter(
            is_current=True
        ).order_by('-start_date')
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        # Validate that end_date is after start_date
        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError('End date must be after start date.')
        
        return cleaned_data


class ExamScheduleForm(forms.ModelForm):
    """Form for creating and updating exam schedules"""

    def __init__(self, *args, **kwargs):
        class_room = None
        if 'class_room' in kwargs:
            class_room = kwargs.pop('class_room')
        super().__init__(*args, **kwargs)
        # If class_room is provided, filter subjects to only those registered for the class
        if class_room:
            from apps.classes.models import ClassSubject
            self.fields['subject'].queryset = ClassSubject.objects.filter(class_room=class_room, is_active=True).values_list('subject', flat=True)
            self.fields['subject'].queryset = self.fields['subject'].queryset.model.objects.filter(id__in=self.fields['subject'].queryset)

    class Meta:
        model = ExamSchedule
        fields = [
            'exam', 'class_room', 'subject', 'exam_date',
            'start_time', 'end_time', 'room_number',
            'max_marks', 'pass_marks', 'status'
        ]
        widgets = {
            'exam': forms.Select(attrs={
                'class': 'form-select'
            }),
            'class_room': forms.Select(attrs={
                'class': 'form-select'
            }),
            'subject': forms.Select(attrs={
                'class': 'form-select'
            }),
            'exam_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'room_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Room 101, Hall A'
            }),
            'max_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '100'
            }),
            'pass_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '40'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        max_marks = cleaned_data.get('max_marks')
        pass_marks = cleaned_data.get('pass_marks')

        # Validate that end_time is after start_time
        if start_time and end_time:
            if end_time <= start_time:
                raise forms.ValidationError('End time must be after start time.')
        
        # Validate that pass_marks is less than max_marks
        if max_marks and pass_marks:
            if pass_marks > max_marks:
                raise forms.ValidationError('Pass marks cannot be greater than maximum marks.')
        
        return cleaned_data
