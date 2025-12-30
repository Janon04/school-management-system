"""
Generate Sample Exam Data and Results
This script creates exam schedules, results, and generates reports
"""

import django
import os
import sys
import random

# Setup Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.students.models import Student
from apps.exams.models import Exam, ExamSchedule
from apps.results.models import Result, ReportCard
from apps.classes.models import ClassRoom, Subject, AcademicYear
from django.utils import timezone
from django.db import transaction


def create_subjects():
    """Create sample subjects if they don't exist"""
    subjects_data = [
        # Primary subjects
        ('MATH-P', 'Mathematics - Primary', 'CORE'),
        ('ENG-P', 'English Language', 'CORE'),
        ('SCI-P', 'General Science', 'CORE'),
        ('SOC-P', 'Social Studies', 'CORE'),
        ('ART-P', 'Creative Arts', 'EXTRA'),
        
        # Secondary subjects
        ('MATH-S', 'Mathematics - Secondary', 'CORE'),
        ('ENG-S', 'English Literature', 'CORE'),
        ('PHYS-S', 'Physics', 'CORE'),
        ('CHEM-S', 'Chemistry', 'CORE'),
        ('BIO-S', 'Biology', 'CORE'),
        ('HIST-S', 'History', 'ELECTIVE'),
        ('GEO-S', 'Geography', 'ELECTIVE'),
        
        # University subjects/modules
        ('CS101', 'Introduction to Programming', 'CORE'),
        ('CS102', 'Data Structures and Algorithms', 'CORE'),
        ('CS201', 'Database Systems', 'CORE'),
        ('CS202', 'Software Engineering', 'CORE'),
        ('MATH201', 'Discrete Mathematics', 'CORE'),
    ]
    
    created_subjects = []
    
    print("\n" + "="*60)
    print("Creating Subjects...")
    print("="*60)
    
    for code, name, category in subjects_data:
        subject, created = Subject.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'category': category,
                'pass_mark': 40,
                'total_marks': 100
            }
        )
        if created:
            print(f"✓ Created: {subject.name} ({subject.code})")
        else:
            print(f"  Exists: {subject.name} ({subject.code})")
        created_subjects.append(subject)
    
    return created_subjects


def create_exam():
    """Create a sample exam"""
    academic_year = AcademicYear.objects.filter(is_current=True).first()
    
    exam, created = Exam.objects.get_or_create(
        name='End of Term Examination',
        academic_year=academic_year,
        defaults={
            'exam_type': 'FINAL',
            'term': 'Term 1',
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date(),
            'is_published': False,
            'description': 'End of term final examination'
        }
    )
    
    if created:
        print(f"\n✓ Created exam: {exam.name}")
    else:
        print(f"\n  Using existing exam: {exam.name}")
    
    return exam


def create_exam_schedules(exam):
    """Create exam schedules for all classes"""
    print("\n" + "="*60)
    print("Creating Exam Schedules...")
    print("="*60)
    
    classes = ClassRoom.objects.filter(is_active=True)
    
    # Subject mapping by level
    subject_mapping = {
        'PRIMARY': ['MATH-P', 'ENG-P', 'SCI-P', 'SOC-P', 'ART-P'],
        'SECONDARY': ['MATH-S', 'ENG-S', 'PHYS-S', 'CHEM-S', 'BIO-S', 'HIST-S'],
        'HIGH_SCHOOL': ['MATH-S', 'ENG-S', 'PHYS-S', 'CHEM-S', 'BIO-S', 'GEO-S'],
        'UNIVERSITY': ['CS101', 'CS102', 'CS201', 'CS202', 'MATH201']
    }
    
    schedule_count = 0
    
    for class_room in classes:
        subject_codes = subject_mapping.get(class_room.level, [])
        subjects = Subject.objects.filter(code__in=subject_codes)
        
        print(f"\n{class_room.name} ({class_room.level}):")
        
        for subject in subjects:
            schedule, created = ExamSchedule.objects.get_or_create(
                exam=exam,
                class_room=class_room,
                subject=subject,
                defaults={
                    'exam_date': exam.start_date,
                    'start_time': '09:00',
                    'end_time': '11:00',
                    'max_marks': 100,
                    'pass_marks': 40
                }
            )
            if created:
                print(f"  ✓ {subject.name}")
                schedule_count += 1
            else:
                print(f"    {subject.name} (exists)")
    
    print(f"\n✓ Created {schedule_count} exam schedules")
    return schedule_count


def generate_results(exam):
    """Generate random results for all students"""
    print("\n" + "="*60)
    print("Generating Results...")
    print("="*60)
    
    schedules = ExamSchedule.objects.filter(exam=exam)
    results_created = 0
    
    with transaction.atomic():
        for schedule in schedules:
            students = schedule.class_room.students.filter(is_active=True)
            
            print(f"\n{schedule.class_room.name} - {schedule.subject.name}:")
            print(f"  Generating results for {students.count()} students...")
            
            for student in students:
                # Check if result exists
                if Result.objects.filter(
                    student=student,
                    exam=exam,
                    subject=schedule.subject
                ).exists():
                    continue
                
                # Generate realistic marks based on level
                if schedule.class_room.level == 'PRIMARY':
                    # Primary: Higher pass rate, 60-95%
                    marks = random.randint(60, 95)
                elif schedule.class_room.level in ['SECONDARY', 'HIGH_SCHOOL']:
                    # Secondary: Normal distribution, 45-90%
                    marks = random.randint(45, 90)
                else:  # UNIVERSITY
                    # University: Wider range, 50-95%
                    marks = random.randint(50, 95)
                
                # 5% chance of being absent
                is_absent = random.random() < 0.05
                
                if is_absent:
                    marks_obtained = 0
                else:
                    marks_obtained = marks
                
                result = Result.objects.create(
                    student=student,
                    exam=exam,
                    subject=schedule.subject,
                    marks_obtained=marks_obtained,
                    max_marks=schedule.max_marks,
                    is_absent=is_absent,
                    remarks='' if not is_absent else 'Student was absent'
                )
                
                results_created += 1
    
    print(f"\n✓ Generated {results_created} results")
    return results_created


def generate_report_cards(exam):
    """Generate report cards for all students"""
    print("\n" + "="*60)
    print("Generating Report Cards...")
    print("="*60)
    
    students = Student.objects.filter(is_active=True)
    reports_generated = 0
    
    # Sample comments
    teacher_comments = [
        "Excellent performance this term. Keep up the good work!",
        "Good progress shown. Continue to work hard.",
        "Satisfactory performance. More effort needed in some subjects.",
        "Outstanding achievement. Well done!",
        "Shows great potential. Keep improving.",
        "Good effort. Focus on weak areas for better results.",
        "Impressive performance across all subjects.",
        "Steady progress observed. Maintain consistency.",
        "Commendable work ethic and dedication.",
        "Good performance. Can achieve more with extra effort."
    ]
    
    principal_comments = [
        "Promoted to next class. Congratulations!",
        "Keep working hard and stay focused.",
        "Well done. Continue with the same dedication.",
        "Good performance. Best wishes for next term.",
        "Excellent results. Keep it up!",
        "Satisfactory progress. Aim higher next term.",
        "Outstanding performance. Proud of your achievement!",
        "Good work. Continue to excel.",
        "Commendable effort. Keep pushing forward.",
        "Great job this term!"
    ]
    
    with transaction.atomic():
        for student in students:
            # Check if report card exists
            report_card, created = ReportCard.objects.get_or_create(
                student=student,
                exam=exam
            )
            
            if created or not report_card.marks_obtained:
                # Calculate totals
                report_card.calculate_totals()
                
                # Add comments
                report_card.teacher_comment = random.choice(teacher_comments)
                report_card.principal_comment = random.choice(principal_comments)
                
                # Add attendance (random 75-100% attendance)
                total_days = 90
                attendance_days = random.randint(75, 90)
                report_card.total_school_days = total_days
                report_card.attendance_days = attendance_days
                
                report_card.save()
                reports_generated += 1
                
                print(f"✓ {student.user.get_full_name()} - {report_card.percentage:.1f}%")
        
        # Calculate class positions
        classes = ClassRoom.objects.filter(is_active=True)
        for class_room in classes:
            report_cards = ReportCard.objects.filter(
                exam=exam,
                student__class_assigned=class_room
            ).order_by('-percentage')
            
            for index, report_card in enumerate(report_cards, start=1):
                report_card.class_position = index
                report_card.save(update_fields=['class_position'])
    
    print(f"\n✓ Generated {reports_generated} report cards")
    print("✓ Calculated class positions")
    return reports_generated


def main():
    """Main function"""
    print("\n" + "="*60)
    print("EXAM DATA & RESULTS GENERATOR")
    print("="*60)
    
    # Check if students exist
    student_count = Student.objects.filter(is_active=True).count()
    if student_count == 0:
        print("\n⚠ No students found!")
        print("Please run 'generate_sample_students.py' first.")
        return
    
    print(f"\nFound {student_count} active students")
    
    # Step 1: Create subjects
    subjects = create_subjects()
    
    # Step 2: Create exam
    exam = create_exam()
    
    # Step 3: Create exam schedules
    schedule_count = create_exam_schedules(exam)
    
    if schedule_count == 0:
        print("\n⚠ No new schedules created (may already exist)")
    
    # Step 4: Generate results
    results_count = generate_results(exam)
    
    # Step 5: Generate report cards
    reports_count = generate_report_cards(exam)
    
    # Final summary
    print("\n" + "="*60)
    print("GENERATION COMPLETE!")
    print("="*60)
    print(f"Exam: {exam.name}")
    print(f"Students: {student_count}")
    print(f"Results Generated: {results_count}")
    print(f"Report Cards: {reports_count}")
    print("\n✓ You can now view reports at:")
    print(f"   http://127.0.0.1:8000/results/processing/{exam.id}/")
    print("="*60 + "\n")


if __name__ == '__main__':
    response = input("Generate exam data and results for all students? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        main()
    else:
        print("\nOperation cancelled.")
