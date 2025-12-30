"""
Forms for Teacher Management
"""
from django import forms
from django.contrib.auth import get_user_model
from .models import Teacher
from apps.classes.models import Subject

User = get_user_model()


class TeacherForm(forms.ModelForm):
    """Form for creating and updating teacher records"""
    
    # User fields
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
    )
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'teacher@example.com'
        })
    )
    phone_number = forms.CharField(
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+254700000000'
        })
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Enter physical address'
        })
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    # Password fields (only for create)
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        }),
        help_text='Leave blank to keep current password (when editing)'
    )
    password_confirm = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    class Meta:
        model = Teacher
        fields = [
            'employee_id', 'qualification', 'specialization', 'experience_years',
            'employment_type', 'joining_date', 'salary', 'subjects',
            'certifications', 'bio', 'resume', 'certificates', 'is_active'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., TCH001'
            }),
            'qualification': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., B.Ed, M.Ed, PhD'
            }),
            'specialization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Mathematics, Science'
            }),
            'experience_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Years of experience'
            }),
            'employment_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'joining_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Monthly salary'
            }),
            'subjects': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
            'certifications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List professional certifications'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Short biography'
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
            'certificates': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.instance_pk = kwargs.get('instance').pk if kwargs.get('instance') else None
        super().__init__(*args, **kwargs)
        
        # Populate user fields if editing
        if self.instance and self.instance.pk:
            user = self.instance.user
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['phone_number'].initial = user.phone_number
            self.fields['address'].initial = user.address
            self.fields['date_of_birth'].initial = user.date_of_birth
            self.fields['password'].required = False
            self.fields['password_confirm'].required = False
        else:
            # Password required for new teachers
            self.fields['password'].required = True
            self.fields['password_confirm'].required = True
        
        # Filter active subjects
        self.fields['subjects'].queryset = Subject.objects.filter(is_active=True)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email exists for another user
            existing_user = User.objects.filter(email=email).exclude(
                teacher_profile__pk=self.instance_pk
            ).first()
            if existing_user:
                raise forms.ValidationError('A user with this email already exists.')
        return email
    
    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if employee_id:
            # Check if employee_id exists for another teacher
            existing_teacher = Teacher.objects.filter(employee_id=employee_id).exclude(
                pk=self.instance_pk
            ).first()
            if existing_teacher:
                raise forms.ValidationError('A teacher with this employee ID already exists.')
        return employee_id
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        # Validate password match
        if password or password_confirm:
            if password != password_confirm:
                raise forms.ValidationError('Passwords do not match.')
        
        # Validate password for new users
        if not self.instance_pk and not password:
            raise forms.ValidationError('Password is required for new teachers.')
        
        return cleaned_data
    
    def save(self, commit=True):
        teacher = super().save(commit=False)
        
        # Create or update user
        if not teacher.pk:
            # Creating new teacher
            user = User.objects.create_user(
                username=self.cleaned_data['email'].split('@')[0],
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                password=self.cleaned_data['password'],
                role='TEACHER',
                phone_number=self.cleaned_data.get('phone_number', ''),
                address=self.cleaned_data.get('address', ''),
                date_of_birth=self.cleaned_data.get('date_of_birth'),
            )
            
            # Handle profile picture
            if self.cleaned_data.get('profile_picture'):
                user.profile_picture = self.cleaned_data['profile_picture']
                user.save()
            
            teacher.user = user
        else:
            # Updating existing teacher
            user = teacher.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.phone_number = self.cleaned_data.get('phone_number', '')
            user.address = self.cleaned_data.get('address', '')
            user.date_of_birth = self.cleaned_data.get('date_of_birth')
            
            # Update password if provided
            if self.cleaned_data.get('password'):
                user.set_password(self.cleaned_data['password'])
            
            # Handle profile picture
            if self.cleaned_data.get('profile_picture'):
                user.profile_picture = self.cleaned_data['profile_picture']
            
            user.save()
        
        if commit:
            teacher.save()
            # Save many-to-many relationships
            self.save_m2m()
        
        return teacher
