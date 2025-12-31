"""
Forms for Student Management
"""
from django import forms
from django.contrib.auth import get_user_model
from .models import Student
from apps.classes.models import ClassRoom, AcademicYear
from apps.parents.models import Parent

User = get_user_model()


class StudentForm(forms.ModelForm):
    """Form for creating and updating student records"""
    
    # User fields
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
            'placeholder': 'student@example.com'
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
        model = Student
        fields = [
            'middle_name',
            'date_of_birth', 'gender', 'blood_group', 'nationality', 'religion',
            'roll_number', 'class_assigned', 'academic_year', 'admission_date',
            'parent', 'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relation', 'previous_school', 'medical_conditions',
            'photo', 'is_active'
        ]
        widgets = {
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter middle name (optional)'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'blood_group': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nationality': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Kenya'
            }),
            'religion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Christian, Muslim, Hindu'
            }),
            'roll_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Class roll number'
            }),
            'class_assigned': forms.Select(attrs={
                'class': 'form-select'
            }),
            'academic_year': forms.Select(attrs={
                'class': 'form-select'
            }),
            'admission_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'parent': forms.Select(attrs={
                'class': 'form-select'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact name'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+254700000000'
            }),
            'emergency_contact_relation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Father, Mother, Guardian'
            }),
            'previous_school': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Previous school name'
            }),
            'medical_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any allergies, medical conditions, or special needs'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
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
            self.fields['password'].required = False
            self.fields['password_confirm'].required = False
        else:
            # Password required for new students
            self.fields['password'].required = True
            self.fields['password_confirm'].required = True
        
        # Filter active classrooms and academic years
        self.fields['class_assigned'].queryset = ClassRoom.objects.filter(is_active=True)
        self.fields['academic_year'].queryset = AcademicYear.objects.all()
        self.fields['parent'].queryset = Parent.objects.select_related('user').all()
        
        # Set default academic year
        current_year = AcademicYear.objects.filter(is_current=True).first()
        if current_year:
            self.fields['academic_year'].initial = current_year
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email exists for another user
            existing_user = User.objects.filter(email=email).exclude(
                student_profile__pk=self.instance_pk
            ).first()
            if existing_user:
                raise forms.ValidationError('A user with this email already exists.')
        return email
    
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
            raise forms.ValidationError('Password is required for new students.')
        
        return cleaned_data
    
    def save(self, commit=True):
        student = super().save(commit=False)
        
        # Create or update user
        if not student.pk:
            # Creating new student
            user = User.objects.create_user(
                username=self.cleaned_data['email'].split('@')[0],
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                password=self.cleaned_data['password'],
                role='STUDENT',
                phone_number=self.cleaned_data.get('phone_number', ''),
                address=self.cleaned_data.get('address', ''),
            )
            
            # Handle profile picture
            if self.cleaned_data.get('profile_picture'):
                user.profile_picture = self.cleaned_data['profile_picture']
                user.save()
            
            student.user = user
        else:
            # Updating existing student
            user = student.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.phone_number = self.cleaned_data.get('phone_number', '')
            user.address = self.cleaned_data.get('address', '')
            
            # Update password if provided
            if self.cleaned_data.get('password'):
                user.set_password(self.cleaned_data['password'])
            
            # Handle profile picture
            if self.cleaned_data.get('profile_picture'):
                user.profile_picture = self.cleaned_data['profile_picture']
            
            user.save()
        
        if commit:
            student.save()
        
        return student
