from django.db import models
from apps.teachers.models import Teacher

class SchoolInfo(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    motto = models.CharField(max_length=255, blank=True)
    headmaster = models.ForeignKey(Teacher, null=True, blank=True, on_delete=models.SET_NULL, related_name='school_headmaster')
    logo = models.ImageField(upload_to='school/logo/', blank=True, null=True)
    principal_signature = models.ImageField(upload_to='school/signatures/', blank=True, null=True, verbose_name='Principal Signature')
    class_teacher_signature = models.ImageField(upload_to='school/signatures/', blank=True, null=True, verbose_name='Class Teacher Signature')
    school_stamp = models.ImageField(upload_to='school/stamps/', blank=True, null=True, verbose_name='School Stamp')
    principal_name = models.CharField(max_length=255, blank=True, verbose_name='Principal Name (Override)')
    class_teacher_name = models.CharField(max_length=255, blank=True, verbose_name='Class Teacher Name (Override)')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'School Information'
        verbose_name_plural = 'School Information'
