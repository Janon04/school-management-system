"""
Generate Sample Students for Each Education Level
This script creates 20 students for each class level with realistic data
"""

import django
import os
import sys
import random
from datetime import datetime, timedelta

# Setup Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.students.models import Student
from apps.accounts.models import User
from apps.classes.models import ClassRoom, AcademicYear
from django.utils import timezone
from django.db import transaction


# Sample data for generating realistic students
FIRST_NAMES = [
    'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
    'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica',
    'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa',
    'Matthew', 'Betty', 'Anthony', 'Margaret', 'Mark', 'Sandra', 'Donald', 'Ashley',
    'Steven', 'Kimberly', 'Paul', 'Emily', 'Andrew', 'Donna', 'Joshua', 'Michelle',
    'Kenneth', 'Dorothy', 'Kevin', 'Carol', 'Brian', 'Amanda', 'George', 'Melissa',
    'Edward', 'Deborah', 'Ronald', 'Stephanie', 'Timothy', 'Rebecca', 'Jason', 'Sharon',
    'Jeffrey', 'Laura', 'Ryan', 'Cynthia', 'Jacob', 'Kathleen', 'Gary', 'Amy',
    'Nicholas', 'Shirley', 'Eric', 'Angela', 'Jonathan', 'Helen', 'Stephen', 'Anna',
    'Larry', 'Brenda', 'Justin', 'Pamela', 'Scott', 'Nicole', 'Brandon', 'Emma',
    'Benjamin', 'Samantha', 'Samuel', 'Katherine', 'Raymond', 'Christine', 'Patrick', 'Debra',
    'Alexander', 'Rachel', 'Jack', 'Catherine', 'Dennis', 'Carolyn', 'Jerry', 'Janet',
    'Tyler', 'Ruth', 'Aaron', 'Maria', 'Jose', 'Heather', 'Adam', 'Diane',
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas',
    'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White',
    'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young',
    'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
    'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell',
    'Carter', 'Roberts', 'Gomez', 'Phillips', 'Evans', 'Turner', 'Diaz', 'Parker',
    'Cruz', 'Edwards', 'Collins', 'Reyes', 'Stewart', 'Morris', 'Morales', 'Murphy',
    'Cook', 'Rogers', 'Gutierrez', 'Ortiz', 'Morgan', 'Cooper', 'Peterson', 'Bailey',
    'Reed', 'Kelly', 'Howard', 'Ramos', 'Kim', 'Cox', 'Ward', 'Richardson',
]

BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
GENDERS = ['M', 'F']
RELATIONS = ['Father', 'Mother', 'Guardian', 'Uncle', 'Aunt', 'Grandfather', 'Grandmother']


def generate_email(first_name, last_name, student_num):
    """Generate a unique email address"""
    return f"{first_name.lower()}.{last_name.lower()}{student_num}@student.school.edu"


def generate_phone():
    """Generate a random phone number"""
    return f"+1{random.randint(2000000000, 9999999999)}"


def generate_date_of_birth(level):
    """Generate age-appropriate date of birth based on education level"""
    today = timezone.now().date()
    
    if level == 'PRIMARY':
        # Ages 5-12
        years_ago = random.randint(5, 12)
    elif level in ['SECONDARY', 'HIGH_SCHOOL']:
        # Ages 13-18
        years_ago = random.randint(13, 18)
    elif level == 'UNIVERSITY':
        # Ages 18-25
        years_ago = random.randint(18, 25)
    else:
        years_ago = random.randint(10, 18)
    
    # Random date within that year
    birth_date = today - timedelta(days=years_ago * 365 + random.randint(0, 365))
    return birth_date


def create_students_for_class(class_room, num_students=20):
    """Create specified number of students for a class"""
    
    print(f"\n{'='*60}")
    print(f"Creating {num_students} students for {class_room.name} ({class_room.level})")
    print(f"{'='*60}")
    
    created_count = 0
    skipped_count = 0
    
    with transaction.atomic():
        for i in range(num_students):
            try:
                # Generate student data
                first_name = random.choice(FIRST_NAMES)
                last_name = random.choice(LAST_NAMES)
                gender = random.choice(GENDERS)
                email = generate_email(first_name, last_name, random.randint(1000, 9999))
                
                # Check if user already exists
                if User.objects.filter(email=email).exists():
                    email = generate_email(first_name, last_name, random.randint(10000, 99999))
                
                # Create user account
                user = User.objects.create_user(
                    username=email.split('@')[0],
                    email=email,
                    password='student123',  # Default password
                    first_name=first_name,
                    last_name=last_name,
                    role='STUDENT'
                )
                
                # Create student profile
                student = Student.objects.create(
                    user=user,
                    date_of_birth=generate_date_of_birth(class_room.level),
                    gender=gender,
                    blood_group=random.choice(BLOOD_GROUPS),
                    emergency_contact_name=f"{random.choice(FIRST_NAMES)} {last_name}",
                    emergency_contact_phone=generate_phone(),
                    emergency_contact_relation=random.choice(RELATIONS),
                    class_assigned=class_room,
                    academic_year=class_room.academic_year,
                    admission_date=timezone.now().date() - timedelta(days=random.randint(30, 365)),
                    roll_number=str(i + 1).zfill(3),
                    is_active=True
                )
                
                created_count += 1
                print(f"✓ Created: {student.user.get_full_name()} ({student.admission_number}) - Roll: {student.roll_number}")
                
            except Exception as e:
                skipped_count += 1
                print(f"✗ Skipped: {first_name} {last_name} - Error: {str(e)}")
    
    print(f"\n{'='*60}")
    print(f"Summary for {class_room.name}:")
    print(f"  ✓ Created: {created_count} students")
    if skipped_count > 0:
        print(f"  ✗ Skipped: {skipped_count} students")
    print(f"{'='*60}")
    
    return created_count, skipped_count


def main():
    """Main function to create students for all class levels"""
    
    print("\n" + "="*60)
    print("SAMPLE STUDENT GENERATOR")
    print("="*60)
    
    # Get or create current academic year
    academic_year = AcademicYear.objects.filter(is_current=True).first()
    if not academic_year:
        print("\n⚠ No current academic year found. Creating one...")
        academic_year = AcademicYear.objects.create(
            name='2024-2025',
            start_date=timezone.now().date(),
            end_date=timezone.now().date().replace(year=timezone.now().year + 1),
            is_current=True
        )
        print(f"✓ Created academic year: {academic_year.name}")
    
    # Get or create classes for each level
    levels_config = [
        ('PRIMARY', 'Grade 3'),
        ('SECONDARY', 'Form 2'),
        ('HIGH_SCHOOL', 'Form 5'),
        ('UNIVERSITY', 'Year 2 Computer Science')
    ]
    
    total_created = 0
    total_skipped = 0
    
    for level, class_name in levels_config:
        # Get or create class
        class_room = ClassRoom.objects.filter(
            level=level,
            academic_year=academic_year
        ).first()
        
        if not class_room:
            print(f"\n⚠ No {level} class found. Creating {class_name}...")
            class_room = ClassRoom.objects.create(
                name=class_name,
                level=level,
                academic_year=academic_year,
                capacity=30,
                is_active=True
            )
            print(f"✓ Created class: {class_room.name}")
        
        # Create students
        created, skipped = create_students_for_class(class_room, num_students=20)
        total_created += created
        total_skipped += skipped
    
    # Final summary
    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    print(f"Total Students Created: {total_created}")
    if total_skipped > 0:
        print(f"Total Skipped: {total_skipped}")
    print("\nDefault Password for all students: student123")
    print("\nYou can now:")
    print("1. Create exam schedules for these classes")
    print("2. Enter results for students")
    print("3. Generate report cards")
    print("="*60 + "\n")


def show_student_summary():
    """Show summary of students by class"""
    print("\n" + "="*60)
    print("CURRENT STUDENT DISTRIBUTION")
    print("="*60)
    
    classes = ClassRoom.objects.filter(is_active=True).order_by('level', 'name')
    
    for class_room in classes:
        student_count = class_room.students.filter(is_active=True).count()
        print(f"{class_room.name} ({class_room.level}): {student_count} students")
    
    total_students = Student.objects.filter(is_active=True).count()
    print(f"\nTotal Active Students: {total_students}")
    print("="*60 + "\n")


if __name__ == '__main__':
    # Show current distribution
    show_student_summary()
    
    # Ask for confirmation
    response = input("Generate 20 students for each class level? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        main()
        
        # Show updated distribution
        show_student_summary()
    else:
        print("\nOperation cancelled.")
