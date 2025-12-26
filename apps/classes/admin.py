"""
Admin configuration for Classes app
"""
from django.contrib import admin
from .models import AcademicYear, ClassRoom, Subject, ClassSubject, TimeTable


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current']
    search_fields = ['name']


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'stream', 'level', 'class_teacher', 'current_students_count', 'capacity', 'is_active']
    list_filter = ['level', 'is_active', 'academic_year']
    search_fields = ['name', 'stream', 'room_number']
    autocomplete_fields = ['class_teacher']
    
    def current_students_count(self, obj):
        return obj.current_students_count
    current_students_count.short_description = 'Students'


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'pass_mark', 'total_marks', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'code']


@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ['class_room', 'subject', 'teacher', 'is_active']
    list_filter = ['class_room', 'subject', 'is_active']
    search_fields = ['class_room__name', 'subject__name']
    autocomplete_fields = ['class_room', 'subject', 'teacher']


@admin.register(TimeTable)
class TimeTableAdmin(admin.ModelAdmin):
    list_display = ['class_room', 'subject', 'teacher', 'day', 'start_time', 'end_time']
    list_filter = ['day', 'class_room']
    search_fields = ['class_room__name', 'subject__name']
    autocomplete_fields = ['class_room', 'subject', 'teacher']
