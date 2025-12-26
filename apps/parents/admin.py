"""
Admin configuration for Parents app
"""
from django.contrib import admin
from .models import Parent


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'relation',
        'occupation',
        'total_children',
        'is_active'
    ]
    list_filter = ['relation', 'is_active']
    search_fields = [
        'user__first_name',
        'user__last_name',
        'user__email',
        'occupation'
    ]
    autocomplete_fields = ['user']
    
    fieldsets = (
        ('User Account', {
            'fields': ('user', 'relation')
        }),
        ('Professional Information', {
            'fields': (
                'occupation',
                'employer',
                'office_address',
                'annual_income'
            )
        }),
        ('Alternative Contact', {
            'fields': (
                'alt_contact_name',
                'alt_contact_phone',
                'alt_contact_relation'
            )
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
