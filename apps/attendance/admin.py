from django.contrib import admin
from .models import Attendance, AttendanceSummary


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['get_student_name', 'date', 'status', 'class_room', 'marked_by']
    list_filter = ['date', 'status', 'class_room']
    search_fields = ['student__admission_number', 'student__user__first_name', 'student__user__last_name']
    autocomplete_fields = ['student', 'class_room', 'marked_by']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('👨‍🎓 Student Information', {
            'fields': ('student', 'class_room', 'date'),
        }),
        ('📊 Attendance Details', {
            'fields': ('status', 'remarks'),
        }),
        ('✅ Verification', {
            'fields': ('marked_by',),
        }),
    )
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name() or obj.student.admission_number
    get_student_name.short_description = 'Student'
    get_student_name.admin_order_field = 'student__user__first_name'


@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ['get_student_name', 'month', 'present_days', 'absent_days', 'attendance_percentage']
    list_filter = ['month']
    search_fields = ['student__admission_number', 'student__user__first_name', 'student__user__last_name']
    autocomplete_fields = ['student']
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name() or obj.student.admission_number
    get_student_name.short_description = 'Student'
    get_student_name.admin_order_field = 'student__user__first_name'
