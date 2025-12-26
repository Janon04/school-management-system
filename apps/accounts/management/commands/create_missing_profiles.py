"""
Management command to create missing profiles for existing users
Usage: python manage.py create_missing_profiles
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import User
from apps.teachers.models import Teacher
from apps.students.models import Student
from apps.parents.models import Parent


class Command(BaseCommand):
    help = 'Creates missing Teacher, Student, and Parent profiles for existing users'

    def handle(self, *args, **options):
        created_count = 0
        
        # Process Teachers
        teachers_without_profile = User.objects.filter(role='TEACHER').exclude(teacher_profile__isnull=False)
        for user in teachers_without_profile:
            # Generate unique employee ID
            last_teacher = Teacher.objects.order_by('-id').first()
            emp_number = 1 if not last_teacher else last_teacher.id + 1
            employee_id = f"TCH{emp_number:04d}"
            
            Teacher.objects.create(
                user=user,
                employee_id=employee_id,
                qualification='To be updated',
                joining_date=timezone.now().date()
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Created Teacher profile for {user.username}'))
            created_count += 1
        
        # Process Students
        students_without_profile = User.objects.filter(role='STUDENT').exclude(student_profile__isnull=False)
        for user in students_without_profile:
            Student.objects.create(
                user=user,
                date_of_birth=timezone.now().date(),
                gender='O',
                emergency_contact_name='To be updated',
                emergency_contact_phone='000000000',
                emergency_contact_relation='Guardian'
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Created Student profile for {user.username}'))
            created_count += 1
        
        # Process Parents
        parents_without_profile = User.objects.filter(role='PARENT').exclude(parent_profile__isnull=False)
        for user in parents_without_profile:
            Parent.objects.create(
                user=user,
                relation='GUARDIAN'
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Created Parent profile for {user.username}'))
            created_count += 1
        
        if created_count == 0:
            self.stdout.write(self.style.WARNING('No missing profiles found. All users have their profiles.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created {created_count} profile(s)'))
            self.stdout.write(self.style.WARNING('⚠ Please update placeholder values through the admin panel.'))
