from django.contrib import admin
from .models import Promotion


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['get_student_name', 'from_class', 'to_class', 'status', 'promoted_on']
    list_filter = ['status', 'from_academic_year', 'to_academic_year']
    search_fields = ['student__admission_number', 'student__user__first_name', 'student__user__last_name']
    autocomplete_fields = ['student', 'from_class', 'to_class', 'promoted_by']
    date_hierarchy = 'promoted_on'
    
    fieldsets = (
        ('👨‍🎓 Student Information', {
            'fields': ('student',),
        }),
        ('📚 Class Transition', {
            'fields': ('from_class', 'from_academic_year', 'to_class', 'to_academic_year'),
        }),
        ('✅ Promotion Details', {
            'fields': ('status', 'promoted_by', 'remarks'),
        }),
    )
    
    readonly_fields = ['promoted_on']
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name() or obj.student.admission_number
    get_student_name.short_description = 'Student'
    get_student_name.admin_order_field = 'student__user__first_name'
