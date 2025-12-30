"""
Models for Class and Subject Management
Handles classroom organization, streams, and subject allocation
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class AcademicYear(models.Model):
    """Academic year configuration"""
    name = models.CharField(max_length=50, unique=True, help_text='e.g., 2024-2025')
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False, help_text='Is this the current academic year?')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Academic Year'
        verbose_name_plural = 'Academic Years'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Ensure only one academic year is marked as current"""
        if self.is_current:
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class ClassRoom(models.Model):
    """
    Represents a class/grade in the school
    e.g., Grade 1, Grade 2, Form 1, etc.
    """
    
    LEVEL_CHOICES = (
        ('PRIMARY', 'Primary School'),
        ('SECONDARY', 'Secondary School'),
        ('HIGH_SCHOOL', 'High School'),
        ('UNIVERSITY', 'University Level'),
    )
    
    name = models.CharField(max_length=50, help_text='e.g., Grade 10, Form 4')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    stream = models.CharField(
        max_length=20, 
        blank=True,
        help_text='e.g., A, B, Science, Arts'
    )
    capacity = models.IntegerField(
        default=40,
        validators=[MinValueValidator(1)],
        help_text='Maximum number of students'
    )
    room_number = models.CharField(
        max_length=20, 
        blank=True,
        help_text='Physical classroom number'
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='classes'
    )
    class_teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes_as_teacher'
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['level', 'name', 'stream']
        verbose_name = 'Class Room'
        verbose_name_plural = 'Class Rooms'
        unique_together = ['name', 'stream', 'academic_year']
    
    def __str__(self):
        if self.stream:
            return f"{self.name} - {self.stream}"
        return self.name
    
    @property
    def full_name(self):
        """Return full class name with stream"""
        return str(self)
    
    @property
    def current_students_count(self):
        """Count enrolled students"""
        return self.students.filter(is_active=True).count()
    
    @property
    def available_seats(self):
        """Calculate available seats"""
        return self.capacity - self.current_students_count


class Subject(models.Model):
    """
    Academic subjects taught in the school
    """
    
    CATEGORY_CHOICES = (
        ('CORE', 'Core Subject'),
        ('ELECTIVE', 'Elective'),
        ('EXTRA', 'Extra Curricular'),
    )
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, help_text='Subject code, e.g., MATH101')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='CORE')
    description = models.TextField(blank=True)
    pass_mark = models.IntegerField(
        default=40,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Minimum marks to pass'
    )
    total_marks = models.IntegerField(
        default=100,
        validators=[MinValueValidator(1)],
        help_text='Total marks for the subject'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ClassSubject(models.Model):
    """
    Link subjects to specific classes
    A subject can be taught in multiple classes
    """
    class_room = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name='class_subjects'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='class_subjects'
    )
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teaching_subjects'
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['class_room', 'subject']
        verbose_name = 'Class Subject'
        verbose_name_plural = 'Class Subjects'
    
    def __str__(self):
        return f"{self.subject.name} in {self.class_room}"


class TimeTable(models.Model):
    """
    Class timetable/schedule
    """
    
    DAY_CHOICES = (
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
        ('SUNDAY', 'Sunday'),
    )
    
    class_room = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name='timetable_entries'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True
    )
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=20, blank=True)
    
    class Meta:
        ordering = ['day', 'start_time']
        verbose_name = 'Time Table Entry'
        verbose_name_plural = 'Time Table Entries'
    
    def __str__(self):
        return f"{self.class_room} - {self.subject.name} ({self.day})"
