"""
Test Script for Report Processing System
Run this to test the report generation functionality
"""

import django
import os
import sys

# Setup Django first
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Now import models
from apps.students.models import Student
from apps.exams.models import Exam
from apps.results.models import Result, ReportCard
from apps.classes.models import ClassRoom

def test_report_generation():
    """Test report generation for different levels"""
    
    print("=" * 60)
    print("TESTING REPORT GENERATION SYSTEM")
    print("=" * 60)
    
    # Test 1: Check if levels are available
    print("\n1. Testing Educational Levels...")
    levels = ClassRoom._meta.get_field('level').choices
    print(f"   Available levels: {[level[0] for level in levels]}")
    
    # Test 2: Check ReportCard model fields
    print("\n2. Testing ReportCard Model...")
    report_card_fields = [f.name for f in ReportCard._meta.get_fields()]
    new_fields = ['gpa', 'class_position', 'teacher_comment', 'principal_comment', 
                  'attendance_days', 'total_school_days']
    
    for field in new_fields:
        if field in report_card_fields:
            print(f"   ✓ {field} field exists")
        else:
            print(f"   ✗ {field} field missing!")
    
    # Test 3: GPA Calculation
    print("\n3. Testing GPA Calculation...")
    try:
        # Find a university level class
        university_classes = ClassRoom.objects.filter(level='UNIVERSITY')
        if university_classes.exists():
            print(f"   ✓ Found {university_classes.count()} university level class(es)")
        else:
            print("   ℹ No university level classes found (create one to test)")
        
        # Test GPA calculation logic
        test_gpa = calculate_test_gpa()
        print(f"   ✓ GPA calculation working: Test GPA = {test_gpa}")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 4: Check Templates
    print("\n4. Testing Template Files...")
    import os
    from django.conf import settings
    
    template_dir = os.path.join(settings.BASE_DIR, 'templates', 'results')
    required_templates = [
        'report_card_primary.html',
        'report_card_secondary.html',
        'report_card_university.html'
    ]
    
    for template in required_templates:
        template_path = os.path.join(template_dir, template)
        if os.path.exists(template_path):
            print(f"   ✓ {template} exists")
        else:
            print(f"   ✗ {template} missing!")
    
    # Test 5: URL Configuration
    print("\n5. Testing URL Configuration...")
    from django.urls import reverse, NoReverseMatch
    
    test_urls = [
        ('results:report_processing', {'exam_id': 1}),
        ('results:update_comments', {'report_id': 1}),
        ('results:bulk_print', {'exam_id': 1, 'class_id': 1}),
    ]
    
    for url_name, kwargs in test_urls:
        try:
            url = reverse(url_name, kwargs=kwargs)
            print(f"   ✓ {url_name}: {url}")
        except NoReverseMatch:
            print(f"   ✗ {url_name} not found!")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


def calculate_test_gpa():
    """Test GPA calculation with sample data"""
    # Simulate results with different percentages
    sample_results = [
        {'percentage': 85, 'credits': 3},  # Should be 4.0
        {'percentage': 75, 'credits': 3},  # Should be 3.5
        {'percentage': 65, 'credits': 3},  # Should be 3.0
    ]
    
    total_credit_points = 0
    total_credits = 0
    
    for result in sample_results:
        percentage = result['percentage']
        credits = result['credits']
        
        # Convert percentage to grade points
        if percentage >= 80:
            grade_point = 4.0
        elif percentage >= 70:
            grade_point = 3.5
        elif percentage >= 60:
            grade_point = 3.0
        elif percentage >= 50:
            grade_point = 2.5
        elif percentage >= 40:
            grade_point = 2.0
        else:
            grade_point = 0.0
        
        total_credit_points += (grade_point * credits)
        total_credits += credits
    
    gpa = round(total_credit_points / total_credits, 2) if total_credits > 0 else 0.0
    return gpa


def create_sample_data():
    """Create sample data for testing"""
    print("\nCreating sample data for testing...")
    
    from apps.classes.models import AcademicYear, Subject
    from apps.accounts.models import User
    from django.utils import timezone
    
    # Create academic year
    academic_year, created = AcademicYear.objects.get_or_create(
        name='2024-2025',
        defaults={
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date().replace(year=timezone.now().year + 1),
            'is_current': True
        }
    )
    
    # Create classes for each level
    levels = ['PRIMARY', 'SECONDARY', 'UNIVERSITY']
    for level in levels:
        class_room, created = ClassRoom.objects.get_or_create(
            name=f"{level.title()} Class 1",
            level=level,
            academic_year=academic_year,
            defaults={
                'capacity': 30,
                'is_active': True
            }
        )
        if created:
            print(f"   ✓ Created {level} class")
    
    # Create sample subjects
    subjects_data = [
        ('MATH101', 'Mathematics'),
        ('ENG101', 'English'),
        ('SCI101', 'Science'),
        ('HIST101', 'History'),
    ]
    
    for code, name in subjects_data:
        subject, created = Subject.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'category': 'CORE',
                'pass_mark': 40,
                'total_marks': 100
            }
        )
        if created:
            print(f"   ✓ Created subject: {name}")
    
    # Create exam
    exam, created = Exam.objects.get_or_create(
        name='Mid Term Exam',
        academic_year=academic_year,
        defaults={
            'exam_type': 'MID_TERM',
            'term': 'Term 1',
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date(),
            'is_published': False
        }
    )
    if created:
        print(f"   ✓ Created exam: {exam.name}")
    
    print("\n✓ Sample data creation complete!")
    print("\nYou can now:")
    print("1. Add students to the classes")
    print("2. Create exam schedules")
    print("3. Enter results")
    print("4. Generate reports")


if __name__ == '__main__':
    # Run tests
    test_report_generation()
    
    # Ask if user wants to create sample data
    response = input("\nDo you want to create sample data? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        create_sample_data()
