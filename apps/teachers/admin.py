"""
Admin configuration for Teachers app
"""
from django.contrib import admin
from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = [
        'employee_id',
        'full_name',
        'qualification',
        'employment_type',
        'experience_years',
        'is_active'
    ]
    list_filter = ['employment_type', 'is_active', 'joining_date']
    search_fields = [
        'employee_id',
        'user__first_name',
        'user__last_name',
        'qualification'
    ]
    autocomplete_fields = ['user']
    filter_horizontal = ['subjects']
    
    fieldsets = (
        ('User Account', {
            'fields': ('user', 'employee_id')
        }),
        ('Professional Information', {
            'fields': (
                'qualification',
                'specialization',
                'experience_years',
                'subjects'
            )
        }),
        ('Employment Details', {
            'fields': (
                'employment_type',
                'joining_date',
                'salary'
            )
        }),
        ('Additional Information', {
            'fields': ('certifications', 'bio')
        }),
        ('Documents', {
            'fields': ('resume', 'certificates')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    actions = ['activate_teachers', 'deactivate_teachers']
    
    def activate_teachers(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} teacher(s) activated.')
    activate_teachers.short_description = 'Activate selected teachers'
    
    def deactivate_teachers(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} teacher(s) deactivated.')
    deactivate_teachers.short_description = 'Deactivate selected teachers'
