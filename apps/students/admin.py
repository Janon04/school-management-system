"""
Admin configuration for Students app
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from django import forms
from .models import Student, StudentDocument
from apps.accounts.models import User


class StudentAdminForm(forms.ModelForm):
    """Custom form for Student admin with better field organization"""
    
    # Add fields for creating a new user directly
    first_name = forms.CharField(
        max_length=150,
        required=False,
        help_text='Student first name (leave User field empty to create new user)'
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        help_text='Student last name'
    )
    email = forms.EmailField(
        required=False,
        help_text='Student email address'
    )
    username = forms.CharField(
        max_length=150,
        required=False,
        help_text='Login username (will be auto-generated if empty)'
    )
    
    middle_name = forms.CharField(
        max_length=50,
        required=False,
        help_text='Student middle name (optional)'
    )
    class Meta:
        model = Student
        fields = '__all__'
        widgets = {
            'medical_conditions': forms.Textarea(attrs={'rows': 3}),
            'previous_school': forms.TextInput(attrs={'size': 50}),
            'middle_name': forms.TextInput(attrs={'size': 30, 'placeholder': 'Middle name (optional)'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add helpful labels and help texts
        if 'user' in self.fields:
            self.fields['user'].required = False
            self.fields['user'].help_text = (
                '⚠️ Select existing user account OR fill in First Name, Last Name, '
                'Email below to create a new user automatically'
            )
        
        if 'date_of_birth' in self.fields:
            self.fields['date_of_birth'].help_text = 'Format: YYYY-MM-DD (e.g., 2010-01-15)'
            
        if 'admission_date' in self.fields:
            self.fields['admission_date'].help_text = 'Format: YYYY-MM-DD'
    
    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        email = cleaned_data.get('email')
        
        # If no user is selected, require the new user fields
        if not user and not first_name:
            raise forms.ValidationError(
                'Please either select an existing User OR provide First Name, '
                'Last Name, and Email to create a new user.'
            )
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Create new user if not provided
        if not instance.user:
            first_name = self.cleaned_data.get('first_name')
            last_name = self.cleaned_data.get('last_name')
            email = self.cleaned_data.get('email')
            username = self.cleaned_data.get('username')
            
            if first_name:
                # Generate username if not provided
                if not username:
                    base_username = f"{first_name.lower()}.{last_name.lower()}"
                    username = base_username
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}{counter}"
                        counter += 1
                
                # Create new user
                user = User.objects.create_user(
                    username=username,
                    email=email or f"{username}@school.local",
                    first_name=first_name,
                    last_name=last_name,
                    role='student',
                    password='student123'  # Default password
                )
                instance.user = user
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance


class StudentDocumentInline(admin.TabularInline):
    model = StudentDocument
    extra = 1
    classes = ['collapse']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentAdminForm
    list_display = [
        'photo_thumbnail',
        'admission_number_display',
        'full_name_display',
        'middle_name',
        'class_assigned_display',
        'gender_display',
        'age_display',
        'contact_display',
        'parent_display',
        'status_display'
    ]
    list_filter = [
        'gender',
        'is_active',
        'class_assigned',
        'academic_year',
        'blood_group',
        'nationality'
    ]
    search_fields = [
        'admission_number',
        'user__first_name',
        'middle_name',
        'user__last_name',
        'user__email',
        'roll_number',
        'parent__user__first_name',
        'parent__user__last_name'
    ]
    autocomplete_fields = ['user', 'parent', 'class_assigned', 'academic_year']
    readonly_fields = [
        'admission_number',
        'created_at',
        'updated_at',
        'photo_preview',
        'full_details_display'
    ]
    filter_horizontal = []
    inlines = [StudentDocumentInline]
    list_per_page = 25
    date_hierarchy = 'admission_date'
    
    fieldsets = (
        ('� User Account (Select existing OR create new below)', {
            'fields': ('user', 'admission_number', 'roll_number'),
            'classes': ('wide',),
            'description': '⬇️ If you don\'t have a user account, fill the fields below to create one automatically'
        }),
        ('➕ Create New User (Optional - only if User field above is empty)', {
            'fields': ('first_name', 'last_name', 'email', 'username'),
            'classes': ('wide', 'collapse'),
            'description': '✏️ Fill these fields to automatically create a new user account'
        }),
        ('📋 Personal Information', {
            'fields': (
                'date_of_birth',
                'gender',
                'blood_group',
                'nationality',
                'religion',
                'photo'
            ),
            'classes': ('wide',)
        }),
        ('🎓 Academic Information', {
            'fields': (
                'class_assigned',
                'academic_year',
                'admission_date',
                'previous_school'
            ),
            'classes': ('wide',)
        }),
        ('👨‍👩‍👧‍👦 Family Information', {
            'fields': ('parent',),
            'classes': ('wide',)
        }),
        ('🚨 Emergency Contact', {
            'fields': (
                'emergency_contact_name',
                'emergency_contact_phone',
                'emergency_contact_relation'
            ),
            'classes': ('wide',)
        }),
        ('🏥 Medical Information', {
            'fields': ('medical_conditions',),
            'classes': ('wide',)
        }),
        ('📄 Documents', {
            'fields': ('birth_certificate',),
            'classes': ('wide',)
        }),
        ('✅ Status & Timeline', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('wide',)
        }),
    )
    
    # Override fieldsets for change form (editing existing student)
    def get_fieldsets(self, request, obj=None):
        if obj:  # Editing existing student
            return (
                ('📸 Photo Preview', {
                    'fields': ('photo_preview',),
                    'classes': ('wide',)
                }),
                ('👤 User Account', {
                    'fields': ('user', 'admission_number', 'roll_number'),
                    'classes': ('wide',)
                }),
                ('📋 Personal Information', {
                    'fields': (
                        'date_of_birth',
                        'gender',
                        'blood_group',
                        'nationality',
                        'religion',
                        'photo'
                    ),
                    'classes': ('wide',)
                }),
                ('🎓 Academic Information', {
                    'fields': (
                        'class_assigned',
                        'academic_year',
                        'admission_date',
                        'previous_school'
                    ),
                    'classes': ('wide',)
                }),
                ('👨‍👩‍👧‍👦 Family Information', {
                    'fields': ('parent',),
                    'classes': ('wide',)
                }),
                ('🚨 Emergency Contact', {
                    'fields': (
                        'emergency_contact_name',
                        'emergency_contact_phone',
                        'emergency_contact_relation'
                    ),
                    'classes': ('wide',)
                }),
                ('🏥 Medical Information', {
                    'fields': ('medical_conditions',),
                    'classes': ('wide',)
                }),
                ('📄 Documents', {
                    'fields': ('birth_certificate',),
                    'classes': ('wide',)
                }),
                ('✅ Status & Timeline', {
                    'fields': ('is_active', 'created_at', 'updated_at'),
                    'classes': ('wide',)
                }),
            )
        return super().get_fieldsets(request, obj)
    
    def photo_thumbnail(self, obj):
        """Display photo thumbnail in list"""
        if obj.photo:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%; border: 3px solid #667eea; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.photo.url
            )
        return format_html(
            '<div style="width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
            'display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 18px;">'
            '{}</div>',
            obj.user.first_name[0] if obj.user.first_name else 'S'
        )
    photo_thumbnail.short_description = '📷'
    
    def photo_preview(self, obj):
        """Display large photo preview in detail view"""
        if obj.photo:
            return format_html(
                '<div style="text-align: center;">'
                '<img src="{}" style="max-width: 300px; max-height: 300px; border-radius: 12px; '
                'box-shadow: 0 4px 12px rgba(0,0,0,0.15); border: 4px solid #667eea;" />'
                '</div>',
                obj.photo.url
            )
        return format_html(
            '<div style="text-align: center; padding: 60px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
            'border-radius: 12px; color: white; font-size: 80px;">{}</div>',
            obj.user.first_name[0] if obj.user.first_name else 'S'
        )
    photo_preview.short_description = 'Student Photo'
    
    def admission_number_display(self, obj):
        """Enhanced admission number display"""
        return format_html(
            '<strong style="color: #667eea; font-size: 13px; font-family: monospace;">{}</strong>',
            obj.admission_number
        )
    admission_number_display.short_description = 'Admission #'
    admission_number_display.admin_order_field = 'admission_number'
    
    def full_name_display(self, obj):
        """Enhanced full name display"""
        return format_html(
            '<div style="color: #2d3748; font-weight: 600; font-size: 14px;">{}</div>'
            '<div style="color: #718096; font-size: 11px;">📧 {}</div>',
            obj.full_name,
            obj.user.email
        )
    full_name_display.short_description = 'Student Name'
    full_name_display.admin_order_field = 'user__first_name'
    
    def class_assigned_display(self, obj):
        """Enhanced class display"""
        if obj.class_assigned:
            return format_html(
                '<span style="background: #667eea; color: white; padding: 5px 12px; '
                'border-radius: 20px; font-size: 12px; font-weight: 600;">{}</span>',
                obj.class_assigned.name
            )
        return format_html('<span style="color: #cbd5e0;">Not Assigned</span>')
    class_assigned_display.short_description = 'Class'
    class_assigned_display.admin_order_field = 'class_assigned'
    
    def gender_display(self, obj):
        """Enhanced gender display with icons"""
        gender_map = {
            'M': ('👦', 'Male', '#4299e1'),
            'F': ('👧', 'Female', '#ed64a6'),
            'O': ('👤', 'Other', '#9f7aea')
        }
        icon, label, color = gender_map.get(obj.gender, ('👤', 'Unknown', '#a0aec0'))
        return format_html(
            '<span style="color: {}; font-weight: 600; font-size: 13px;">{} {}</span>',
            color, icon, label
        )
    gender_display.short_description = 'Gender'
    gender_display.admin_order_field = 'gender'
    
    def age_display(self, obj):
        """Enhanced age display"""
        age = obj.age
        return format_html(
            '<span style="background: #edf2f7; color: #2d3748; padding: 4px 10px; '
            'border-radius: 12px; font-size: 12px; font-weight: 600;">{} yrs</span>',
            age
        )
    age_display.short_description = '🎂 Age'
    
    def contact_display(self, obj):
        """Display contact information"""
        return format_html(
            '<div style="color: #2d3748; font-size: 12px;">📱 {}</div>',
            obj.emergency_contact_phone
        )
    contact_display.short_description = 'Emergency Contact'
    
    def parent_display(self, obj):
        """Enhanced parent display"""
        if obj.parent:
            return format_html(
                '<div style="color: #2d3748; font-weight: 500; font-size: 12px;">👨‍👩‍👧‍👦 {}</div>',
                obj.parent.user.get_full_name()
            )
        return format_html('<span style="color: #cbd5e0;">No Parent Linked</span>')
    parent_display.short_description = 'Parent/Guardian'
    parent_display.admin_order_field = 'parent'
    
    def status_display(self, obj):
        """Enhanced status display"""
        if obj.is_active:
            return format_html(
                '<span style="background: #c6f6d5; color: #22543d; padding: 5px 12px; '
                'border-radius: 20px; font-size: 11px; font-weight: 700;">✓ ACTIVE</span>'
            )
        return format_html(
            '<span style="background: #fed7d7; color: #742a2a; padding: 5px 12px; '
            'border-radius: 20px; font-size: 11px; font-weight: 700;">✗ INACTIVE</span>'
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'is_active'
    
    def full_details_display(self, obj):
        """Display comprehensive student details"""
        return format_html(
            '<div style="background: white; padding: 20px; border-radius: 12px; border: 2px solid #e2e8f0;">'
            '<h3 style="color: #2d3748; margin-top: 0;">Quick Overview</h3>'
            '<table style="width: 100%; color: #2d3748;">'
            '<tr><td style="padding: 8px; font-weight: 600;">Full Name:</td><td style="padding: 8px;">{}</td></tr>'
            '<tr><td style="padding: 8px; font-weight: 600;">Admission Number:</td><td style="padding: 8px;">{}</td></tr>'
            '<tr><td style="padding: 8px; font-weight: 600;">Class:</td><td style="padding: 8px;">{}</td></tr>'
            '<tr><td style="padding: 8px; font-weight: 600;">Age:</td><td style="padding: 8px;">{} years</td></tr>'
            '<tr><td style="padding: 8px; font-weight: 600;">Blood Group:</td><td style="padding: 8px;">{}</td></tr>'
            '</table>'
            '</div>',
            obj.full_name,
            obj.admission_number,
            obj.class_assigned.name if obj.class_assigned else 'Not Assigned',
            obj.age,
            obj.blood_group or 'Not Specified'
        )
    full_details_display.short_description = 'Student Overview'
    
    actions = ['activate_students', 'deactivate_students', 'export_student_list']
    
    def activate_students(self, request, queryset):
        """Activate selected students"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'✅ Successfully activated {updated} student(s).',
            level='success'
        )
    activate_students.short_description = '✓ Activate selected students'
    
    def deactivate_students(self, request, queryset):
        """Deactivate selected students"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'⚠️ Successfully deactivated {updated} student(s).',
            level='warning'
        )
    deactivate_students.short_description = '✗ Deactivate selected students'
    
    def export_student_list(self, request, queryset):
        """Export student list information"""
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Admission Number', 'Full Name', 'Email', 'Class', 
            'Gender', 'Age', 'Blood Group', 'Contact', 'Status'
        ])
        
        for student in queryset:
            writer.writerow([
                student.admission_number,
                student.full_name,
                student.user.email,
                student.class_assigned.name if student.class_assigned else '',
                student.get_gender_display(),
                student.age,
                student.blood_group,
                student.emergency_contact_phone,
                'Active' if student.is_active else 'Inactive'
            ])
        
        self.message_user(request, f'📥 Exported {queryset.count()} student(s) to CSV.')
        return response
    export_student_list.short_description = '📥 Export selected students to CSV'


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ['document_icon', 'student_display', 'title_display', 'uploaded_display']
    list_filter = ['uploaded_at']
    search_fields = ['student__admission_number', 'student__user__first_name', 'student__user__last_name', 'title']
    autocomplete_fields = ['student']
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('👨‍🎓 Student', {
            'fields': ('student',),
        }),
        ('📄 Document Details', {
            'fields': ('title', 'document'),
        }),
    )
    
    def document_icon(self, obj):
        """Display document icon"""
        return format_html(
            '<span style="font-size: 24px;">📄</span>'
        )
    document_icon.short_description = ''
    
    def student_display(self, obj):
        """Enhanced student display"""
        return format_html(
            '<div style="color: #2d3748; font-weight: 600;">{}</div>'
            '<div style="color: #718096; font-size: 11px;">{}</div>',
            obj.student.full_name,
            obj.student.admission_number
        )
    student_display.short_description = 'Student'
    student_display.admin_order_field = 'student'
    
    def title_display(self, obj):
        """Enhanced title display"""
        return format_html(
            '<strong style="color: #667eea;">{}</strong>',
            obj.title
        )
    title_display.short_description = 'Document Title'
    title_display.admin_order_field = 'title'
    
    def uploaded_display(self, obj):
        """Enhanced upload date display"""
        return format_html(
            '<span style="color: #2d3748; font-size: 12px;">📅 {}</span>',
            obj.uploaded_at.strftime('%b %d, %Y %I:%M %p')
        )
    uploaded_display.short_description = 'Uploaded'
    uploaded_display.admin_order_field = 'uploaded_at'
