from django.contrib import admin
from .models import Result, ReportCard


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['get_student_name', 'exam', 'subject', 'marks_obtained', 'max_marks', 'grade', 'percentage']
    list_filter = ['exam', 'subject', 'grade', 'is_absent']
    search_fields = ['student__admission_number', 'student__user__first_name', 'student__user__last_name', 'subject__name']
    autocomplete_fields = ['student', 'exam', 'subject', 'entered_by']
    
    fieldsets = (
        ('👨‍🎓 Student & Exam', {
            'fields': ('student', 'exam', 'subject'),
        }),
        ('📊 Marks', {
            'fields': ('marks_obtained', 'max_marks', 'is_absent'),
        }),
        ('📝 Evaluation', {
            'fields': ('grade', 'remarks', 'entered_by'),
        }),
    )
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name() or obj.student.admission_number
    get_student_name.short_description = 'Student'
    get_student_name.admin_order_field = 'student__user__first_name'
    
    def percentage(self, obj):
        return f"{obj.percentage:.2f}%"


@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = ['get_student_name', 'exam', 'marks_obtained', 'total_marks', 'percentage', 'overall_grade', 'rank']
    list_filter = ['exam', 'overall_grade']
    search_fields = ['student__admission_number', 'student__user__first_name', 'student__user__last_name']
    autocomplete_fields = ['student', 'exam']
    readonly_fields = ['generated_at']
    
    fieldsets = (
        ('👨‍🎓 Student Information', {
            'fields': ('student', 'exam'),
        }),
        ('📊 Performance', {
            'fields': ('marks_obtained', 'total_marks', 'overall_grade', 'rank'),
        }),
        ('📝 Comments', {
            'fields': ('teacher_comments', 'principal_comments'),
        }),
        ('🕐 Generated', {
            'fields': ('generated_at',),
        }),
    )
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name() or obj.student.admission_number
    get_student_name.short_description = 'Student'
    get_student_name.admin_order_field = 'student__user__first_name'
