from django.contrib import admin
from .models import Exam, ExamSchedule


class ExamScheduleInline(admin.TabularInline):
    model = ExamSchedule
    extra = 0
    autocomplete_fields = ['class_room', 'subject']
    classes = ['collapse']  # Make it collapsible
    verbose_name = 'Exam Schedule'
    verbose_name_plural = 'Exam Schedules (Optional - Can be added later)'


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_type', 'term', 'start_date', 'end_date', 'is_published']
    list_filter = ['exam_type', 'is_published', 'academic_year']
    search_fields = ['name', 'term', 'description']
    autocomplete_fields = ['academic_year']
    inlines = [ExamScheduleInline]
    
    fieldsets = (
        ('📝 Basic Information', {
            'fields': ('name', 'exam_type', 'term', 'academic_year'),
        }),
        ('📅 Schedule', {
            'fields': ('start_date', 'end_date'),
        }),
        ('📄 Details', {
            'fields': ('description', 'is_published'),
        }),
    )


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ['exam', 'class_room', 'subject', 'exam_date', 'start_time']
    list_filter = ['exam_date', 'exam']
    search_fields = ['exam__name', 'subject__name', 'class_room__name']
    autocomplete_fields = ['exam', 'class_room', 'subject']
    
    fieldsets = (
        ('📝 Exam & Class', {
            'fields': ('exam', 'class_room', 'subject'),
        }),
        ('🕐 Timing', {
            'fields': ('exam_date', 'start_time', 'end_time'),
        }),
        ('📍 Location', {
            'fields': ('room_number',),
        }),
    )
