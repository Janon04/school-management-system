from django.contrib import admin
from .models import Staff


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'get_full_name', 'department', 'designation', 'joining_date', 'is_active']
    list_filter = ['department', 'is_active', 'joining_date']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name', 'user__email', 'designation']
    
    # Better user selection with autocomplete instead of raw_id
    autocomplete_fields = ['user']
    
    # Organize form fields in sections
    fieldsets = (
        ('👤 User Account', {
            'fields': ('user',),
            'description': 'Select an existing user account or create a new user first from the Users section.'
        }),
        ('💼 Employment Details', {
            'fields': ('employee_id', 'department', 'designation', 'joining_date'),
        }),
        ('💰 Compensation', {
            'fields': ('salary',),
        }),
        ('✅ Status', {
            'fields': ('is_active',),
        }),
    )
    
    # Make it easier to add new staff
    list_per_page = 25
    date_hierarchy = 'joining_date'
    
    # Custom method to display full name
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'user__first_name'
    
    # Add helpful actions
    actions = ['activate_staff', 'deactivate_staff']
    
    def activate_staff(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} staff member(s) activated successfully.')
    activate_staff.short_description = 'Activate selected staff members'
    
    def deactivate_staff(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} staff member(s) deactivated successfully.')
    deactivate_staff.short_description = 'Deactivate selected staff members'
