import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.results.models import Result, ReportCard
from apps.students.models import Student
from apps.classes.models import ClassRoom

print("=" * 80)
print("📊 REPORT GENERATION SYSTEM - READY TO VIEW!")
print("=" * 80)

# Summary
total_students = Student.objects.filter(is_active=True).count()
total_results = Result.objects.count()
total_reports = ReportCard.objects.count()

print(f"\n✅ Total Students: {total_students}")
print(f"✅ Total Results Entered: {total_results}")
print(f"✅ Total Report Cards: {total_reports}")

print("\n" + "=" * 80)
print("🎯 MAIN DASHBOARD - View All Reports")
print("=" * 80)
print("\n📌 http://127.0.0.1:8000/results/processing/2/")
print("   → From here you can:")
print("   • View all classes")
print("   • Click 'Print All' for any class")
print("   • Click individual students to view their reports")

print("\n" + "=" * 80)
print("👥 SAMPLE STUDENT REPORT LINKS")
print("=" * 80)

# Get sample students from each level
for cls in ClassRoom.objects.all().order_by('id'):
    students = Student.objects.filter(class_assigned=cls, is_active=True).order_by('id')[:5]
    
    if students.exists():
        print(f"\n📚 {cls.name} ({cls.get_level_display()}):")
        print(f"   Bulk Print All: http://127.0.0.1:8000/results/bulk-print/2/{cls.id}/")
        print(f"   Individual Reports:")
        
        for student in students:
            print(f"   • {student.user.get_full_name():25} → http://127.0.0.1:8000/results/report-card/{student.id}/2/")

print("\n" + "=" * 80)
print("🖨️ HOW TO PRINT REPORTS")
print("=" * 80)
print("\n1. Click any report link above")
print("2. Click 'Print Report' button OR press Ctrl+P")
print("3. Select your printer or 'Save as PDF'")
print("4. Enable 'Background Graphics' option")
print("5. Click Print!")

print("\n" + "=" * 80)
print("🎨 REPORT TEMPLATES")
print("=" * 80)
print("\n• PRIMARY Level    → Green themed report")
print("• SECONDARY Level  → Blue themed report")
print("• HIGH_SCHOOL Level → Blue themed report")
print("• UNIVERSITY Level → Purple themed transcript with GPA")

print("\n" + "=" * 80)
print("✨ READY TO GO!")
print("=" * 80)
print("\nYour development server is running at: http://127.0.0.1:8000")
print("Start viewing reports at: http://127.0.0.1:8000/results/processing/2/")
print("=" * 80)
