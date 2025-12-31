from django import forms
from .models import ClassRoom, ClassSubject
from apps.teachers.models import Teacher

class ClassRoomForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        fields = [
            'name', 'level', 'stream', 'capacity', 'room_number',
            'academic_year', 'class_teacher', 'description', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Grade 10, Form 4'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'stream': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., A, B, Science, Arts'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Room 101'}),
            'academic_year': forms.Select(attrs={'class': 'form-select'}),
            'class_teacher': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ModelForm for ClassSubject with teacher dropdown
class ClassSubjectForm(forms.Form):
    class_room = forms.ModelChoiceField(
        queryset=ClassRoom.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Class'
    )
    subjects = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        label='Subjects'
    )
    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Assign Teacher'
    )
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Active'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Subject
        self.fields['subjects'].queryset = Subject.objects.filter(is_active=True)
