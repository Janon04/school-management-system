"""
Forms for Parent Management
"""
from django import forms
from django.contrib.auth import get_user_model
from .models import Parent

User = get_user_model()
from apps.students.models import Student

class ParentForm(forms.ModelForm):
    def student_label(self, student):
        return f"{student.admission_number} - {student.user.get_full_name()}"

    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.filter(is_active=True, parent__isnull=True),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'dropdown-menu show', 'style': 'max-height: 300px; overflow-y: auto;'}),
        help_text='Assign students to this parent',
        label='Select Students to Assign',
        to_field_name=None,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['students'].label_from_instance = self.student_label
    """Form for creating and updating parent records"""
    
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
            'placeholder': 'parent@example.com'
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
            'placeholder': 'Enter residential address'
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
        model = Parent
        fields = [
            'relation', 'occupation', 'employer', 'office_address',
            'annual_income', 'alt_contact_name', 'alt_contact_phone',
            'alt_contact_relation', 'is_active', 'students'
        ]
        widgets = {
            'relation': forms.Select(attrs={
                'class': 'form-select'
            }),
            'occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Engineer, Teacher'
            }),
            'employer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company/Organization name'
            }),
            'office_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Office address'
            }),
            'annual_income': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Annual income (optional)',
                'step': '0.01'
            }),
            'alt_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Alternative contact person name'
            }),
            'alt_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+254700000000'
            }),
            'alt_contact_relation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Uncle, Aunt, Friend'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)
        
        # If editing, populate user fields
        if self.instance and self.instance.pk and hasattr(self.instance, 'user'):
            user = self.instance.user
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['phone_number'].initial = user.phone_number
            self.fields['address'].initial = user.address
            # Password not required when editing
            self.fields['password'].required = False
            self.fields['password_confirm'].required = False
            # Pre-select students already assigned to this parent
            self.fields['students'].queryset = self.fields['students'].queryset | self.instance.children.all()
            self.fields['students'].initial = self.instance.children.values_list('pk', flat=True)
        else:
            # Password required when creating
            self.fields['password'].required = True
            self.fields['password_confirm'].required = True
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if email already exists (excluding current user if editing)
        qs = User.objects.filter(email=email)
        current_user = getattr(self.instance, 'user', None)
        if current_user and current_user.pk:
            qs = qs.exclude(pk=current_user.pk)
        # Only raise error if another user (not the current one) has this email
        if qs.exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        # Validate passwords match
        if password or password_confirm:
            if password != password_confirm:
                raise forms.ValidationError('Passwords do not match.')
        
        return cleaned_data
    
    def save(self, commit=True):
        parent = super().save(commit=False)

        # Handle user creation or update
        if self.instance.pk:
            # Update existing user
            user = parent.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.phone_number = self.cleaned_data.get('phone_number', '')
            user.address = self.cleaned_data.get('address', '')

            # Update password if provided
            password = self.cleaned_data.get('password')
            if password:
                user.set_password(password)

            # Update profile picture if provided
            profile_picture = self.cleaned_data.get('profile_picture')
            if profile_picture:
                user.profile_picture = profile_picture

            if commit:
                user.save()
        else:
            # Create new user
            user = User.objects.create_user(
                username=self.cleaned_data['email'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                phone_number=self.cleaned_data.get('phone_number', ''),
                address=self.cleaned_data.get('address', ''),
                role='PARENT'
            )

            # Add profile picture if provided
            profile_picture = self.cleaned_data.get('profile_picture')
            if profile_picture:
                user.profile_picture = profile_picture
                user.save()

            parent.user = user

        if commit:
            parent.save()

        # Assign selected students to this parent
        if 'students' in self.cleaned_data:
            selected_students = self.cleaned_data['students']
            # Remove this parent from students not selected
            parent.children.exclude(pk__in=selected_students).update(parent=None)
            # Assign this parent to selected students
            selected_students.update(parent=parent)

        return parent
