"""
Admin configuration for Accounts app
Customizes the Django admin interface for User management
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, AuditLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Enhanced User admin with role-based filtering and custom display"""
    
    list_display = ['username', 'email', 'get_full_name', 'role', 'is_active', 'date_joined', 'profile_image']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']
    ordering = ['-date_joined']
    
    # Enable autocomplete support for foreign key relations
    search_fields = ['username', 'first_name', 'last_name', 'email']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Profile', {
            'fields': ('role', 'phone_number', 'address', 'date_of_birth', 'profile_picture')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Information', {
            'fields': ('role', 'email', 'first_name', 'last_name', 'phone_number')
        }),
    )
    
    def profile_image(self, obj):
        """Display profile picture thumbnail"""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.profile_picture.url
            )
        return format_html('<span style="color: #ccc;">No Image</span>')
    
    profile_image.short_description = 'Profile'
    
    actions = ['activate_users', 'deactivate_users']
    
    def activate_users(self, request, queryset):
        """Bulk activate users"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated successfully.')
    activate_users.short_description = 'Activate selected users'
    
    def deactivate_users(self, request, queryset):
        """Bulk deactivate users"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated successfully.')
    deactivate_users.short_description = 'Deactivate selected users'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin for audit logs - read only"""
    
    list_display = ['user', 'action', 'timestamp', 'ip_address']
    list_filter = ['timestamp', 'user']
    search_fields = ['user__username', 'action', 'details']
    readonly_fields = ['user', 'action', 'details', 'ip_address', 'timestamp']
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        """Audit logs cannot be manually added"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Audit logs cannot be deleted"""
        return False
