# School Report Processing System - User Guide

## Overview
This enhanced report processing system supports generating and printing academic reports for students across different educational levels:
- **Primary Level**: Colorful, easy-to-read reports for younger students
- **Secondary Level**: Professional format with detailed performance metrics
- **University Level**: Academic transcripts with GPA calculation and module-based grading

## Features Implemented

### 1. Multi-Level Support
The system now supports four educational levels:
- PRIMARY: Primary School
- SECONDARY: Secondary School  
- HIGH_SCHOOL: High School
- UNIVERSITY: University Level

### 2. Enhanced Report Cards

#### Primary Level Reports
- **Design**: Green-themed, child-friendly layout
- **Features**:
  - Clear subject-wise performance
  - Color-coded grades (A-F)
  - Pass/Fail indicators
  - Teacher and principal comments
  - Attendance tracking
  - Class position

#### Secondary Level Reports
- **Design**: Blue-themed, professional layout
- **Features**:
  - Detailed subject performance with remarks
  - Performance summary with overall percentage
  - Class position ranking
  - Attendance percentage
  - Space for teacher and principal remarks

#### University Level Reports (Transcripts)
- **Design**: Purple-themed, formal academic transcript
- **Features**:
  - Module-based grading (Module Code + Name)
  - GPA calculation on 4.0 scale
  - Credit hours tracking
  - Grade point system
  - Official certification section
  - Watermark for authenticity
  - Academic advisor and dean comments

### 3. Enhanced ReportCard Model

New fields added:
- `gpa`: GPA calculation for university level (4.0 scale)
- `class_position`: Position in class based on percentage
- `teacher_comment`: Class teacher's remarks
- `principal_comment`: Principal/Head's remarks  
- `attendance_days`: Days attended
- `total_school_days`: Total school days

### 4. Print Functionality

Each report template includes:
- **Print button**: Fixed position for easy access
- **Print-optimized CSS**: Proper page breaks and margins
- **A4 format**: Standard paper size
- **Color preservation**: Colors print correctly

### 5. GPA Calculation

For university level:
```
Grade Points (4.0 scale):
- A (80-100%): 4.0
- B (70-79%): 3.5
- C (60-69%): 3.0
- D (50-59%): 2.5
- E (40-49%): 2.0
- F (0-39%): 0.0
```

GPA = (Sum of Grade Points × Credits) / Total Credits

## Usage Guide

### Accessing Report Processing

1. **Navigate to Report Processing**:
   ```
   http://127.0.0.1:8000/results/processing/{exam_id}/
   ```

2. **Available Actions per Class**:
   - **Enter Results**: Input student marks for subjects
   - **Generate Reports**: Create report cards for all students
   - **Print All**: Bulk print all reports for a class

### Generating Reports

1. **Generate Single Report**:
   - Navigate to report generation page
   - Click "Generate" next to a student name
   - View and print individual report

2. **Generate All Reports**:
   - Click "Generate All Reports" button
   - System will:
     - Calculate totals for all students
     - Calculate class positions
     - Compute GPA (for university level)
     - Set overall grades

3. **Print Reports**:
   - Click "Print All" to open bulk print view
   - Use browser print (Ctrl+P / Cmd+P)
   - Select printer or save as PDF

### Viewing Report Cards

Individual report cards can be viewed at:
```
http://127.0.0.1:8000/results/report-card/{student_id}/{exam_id}/
```

The system automatically selects the correct template based on the student's class level.

### Adding Comments and Attendance

Use the update comments endpoint to add:
- Teacher comments
- Principal comments
- Attendance information

```javascript
// Example AJAX request
fetch('/results/update-comments/' + reportCardId + '/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
        teacher_comment: 'Excellent performance this term.',
        principal_comment: 'Keep up the good work.',
        attendance_days: 85,
        total_school_days: 90
    })
});
```

## URL Patterns

```python
# Report Processing Dashboard
/results/processing/<exam_id>/

# Result Entry
/results/enter/<exam_id>/<class_id>/
/results/save/<exam_id>/<class_id>/

# Report Generation
/results/generate/<exam_id>/<class_id>/
/results/generate-all/<exam_id>/<class_id>/
/results/generate-single/<exam_id>/<student_id>/

# Report Card View (auto-selects template)
/results/report-card/<student_id>/<exam_id>/

# Comments Update
/results/update-comments/<report_id>/

# Bulk Print
/results/bulk-print/<exam_id>/<class_id>/

# Calculate Rankings
/results/calculate-ranks/<exam_id>/<class_id>/

# Publish Results
/results/publish/<exam_id>/<class_id>/
```

## Database Changes

### Migration Files Created:
1. `apps/classes/migrations/0003_alter_classroom_level.py`
   - Added UNIVERSITY level to ClassRoom model

2. `apps/results/migrations/0002_reportcard_*.py`
   - Added attendance fields
   - Added class_position field
   - Added gpa field
   - Added comment fields

### Running Migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Customization

### Changing School Information

Edit the header section in each template:
- School name
- School address
- Contact information
- School motto
- School logo (emoji or image)

### Modifying Grading Scale

To change grading criteria:

1. **Primary/Secondary**: Edit the `calculate_grade()` method in [models.py](apps/results/models.py):
   ```python
   def calculate_grade(self):
       pct = self.percentage
       if pct >= 80: return 'A'
       elif pct >= 70: return 'B'
       # ... modify as needed
   ```

2. **University GPA**: Edit the `calculate_gpa()` method in ReportCard model

### Customizing Templates

Template files:
- `templates/results/report_card_primary.html`
- `templates/results/report_card_secondary.html`
- `templates/results/report_card_university.html`

CSS can be modified in the `<style>` section of each template.

## Best Practices

1. **Before Printing**:
   - Generate all reports first
   - Calculate class positions
   - Add teacher/principal comments
   - Verify attendance data

2. **Print Settings**:
   - Use "Print to PDF" for digital copies
   - Set margins to minimum
   - Enable background graphics
   - Use A4 paper size

3. **Data Entry**:
   - Enter results systematically by subject
   - Mark absent students appropriately
   - Double-check marks before generating reports

4. **End of Term Process**:
   ```
   1. Enter all results
   2. Generate all reports
   3. Add comments
   4. Calculate positions
   5. Print reports
   6. Publish results
   ```

## Troubleshooting

### Reports not displaying correctly?
- Clear browser cache
- Check that migrations are applied
- Verify student has class assigned

### GPA showing 0.00?
- Ensure class level is set to UNIVERSITY
- Check that results exist for the student
- Verify marks are entered correctly

### Print preview looks wrong?
- Use Chrome or Firefox for best results
- Enable print background colors/images
- Check page orientation is Portrait

## Technical Details

### Models Updated:
- `ClassRoom`: Added UNIVERSITY level
- `ReportCard`: Added 6 new fields
- `Result`: No changes, already comprehensive

### Views Added/Modified:
- `report_card_view()`: Template selection logic
- `generate_all_reports_view()`: Position calculation
- `update_report_comments_view()`: NEW - Update comments via AJAX
- `bulk_print_reports_view()`: NEW - Bulk printing support

### Templates Created:
- Primary level report card
- Secondary level report card  
- University level transcript
- All with print optimization

## Future Enhancements

Potential additions:
- Graphical performance charts
- Multi-semester cumulative GPA
- Export to PDF (server-side)
- Email reports to parents
- Digital signatures
- QR code verification
- Mobile-responsive view

## Support

For issues or questions:
1. Check this documentation
2. Review the code comments
3. Test with sample data
4. Verify database migrations are applied

---

**Version**: 2.0  
**Last Updated**: December 30, 2025  
**Compatibility**: Django 4.2+, Python 3.10+
