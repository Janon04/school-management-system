# Report Processing - Quick Reference Card

## 🚀 Quick Start

### 1. Generate Reports
```
URL: http://127.0.0.1:8000/results/processing/{exam_id}/
1. Click "Generate Reports" for a class
2. Click "Generate All Reports" button
3. Reports are created automatically
```

### 2. View Individual Report
```
URL: http://127.0.0.1:8000/results/report-card/{student_id}/{exam_id}/
- System auto-selects template based on student level
- Click "Print Report" button to print
```

### 3. Bulk Print
```
Click "Print All" button from processing dashboard
- Opens all reports in one page
- Use browser print (Ctrl+P)
```

## 📊 Report Types

| Education Level | Template Used | Special Features |
|-----------------|---------------|------------------|
| PRIMARY | Primary Report | Simple, colorful, child-friendly |
| SECONDARY | Secondary Report | Professional, detailed metrics |
| HIGH_SCHOOL | Secondary Report | Same as secondary |
| UNIVERSITY | University Transcript | GPA, modules, credits |

## 🎯 Key URLs

```
Dashboard:           /results/processing/{exam_id}/
Individual Report:   /results/report-card/{student_id}/{exam_id}/
Bulk Print:          /results/bulk-print/{exam_id}/{class_id}/
Update Comments:     /results/update-comments/{report_id}/
```

## 📝 ReportCard Fields

- `marks_obtained` - Total marks scored
- `total_marks` - Maximum marks
- `percentage` - Overall percentage
- `overall_grade` - Letter grade
- `gpa` - GPA (for university)
- `class_position` - Rank in class
- `teacher_comment` - Teacher remarks
- `principal_comment` - Principal remarks
- `attendance_days` - Days present
- `total_school_days` - Total days

## 🎓 GPA Scale (University)

```
A: 80-100% = 4.0
B: 70-79%  = 3.5
C: 60-69%  = 3.0
D: 50-59%  = 2.5
E: 40-49%  = 2.0
F: 0-39%   = 0.0
```

## 🖨️ Print Tips

1. Click "Print Report" button
2. Select printer or "Save as PDF"
3. Set margins to minimum
4. Enable background graphics
5. Use Portrait orientation
6. Paper size: A4

## ⚡ Workflow

```
Enter Results → Generate All Reports → Calculate Positions → Add Comments → Print → Publish
```

## 🔧 Common Tasks

### Add Teacher Comments
```python
# Use update comments endpoint
POST /results/update-comments/{report_id}/
{
    "teacher_comment": "Excellent work",
    "principal_comment": "Keep it up",
    "attendance_days": 85,
    "total_school_days": 90
}
```

### Regenerate Single Report
```
GET /results/report-card/{student_id}/{exam_id}/?regenerate=true
```

### Calculate Class Rankings
```
POST /results/calculate-ranks/{exam_id}/{class_id}/
```

## 📱 Browser Compatibility

✅ Chrome (Recommended)  
✅ Firefox  
✅ Edge  
⚠️ Safari (Test print preview)

## 🎨 Template Files

```
templates/results/report_card_primary.html     - Primary school
templates/results/report_card_secondary.html   - Secondary school
templates/results/report_card_university.html  - University
```

## 🛠️ Customization

### Change School Name
Edit template files, find:
```html
<div class="school-name">YOUR SCHOOL NAME</div>
```

### Modify Grading Scale
Edit: `apps/results/models.py`
Method: `Result.calculate_grade()`

### Adjust GPA Calculation
Edit: `apps/results/models.py`
Method: `ReportCard.calculate_gpa()`

## 📋 Checklist for Term End

- [ ] All results entered
- [ ] All reports generated
- [ ] Class positions calculated
- [ ] Teacher comments added
- [ ] Principal comments added
- [ ] Attendance data entered
- [ ] Reports printed
- [ ] Results published

## 🐛 Troubleshooting

**Reports not showing?**
- Check migrations applied
- Verify student has class assigned
- Ensure results exist

**GPA showing 0.00?**
- Class level must be UNIVERSITY
- Results must exist
- Marks must be entered

**Print looks wrong?**
- Use Chrome or Firefox
- Enable background colors
- Check page orientation

## 💡 Tips

1. Generate reports before printing
2. Add comments before printing
3. Use "Print to PDF" for digital copies
4. Test print one report first
5. Calculate positions after all results entered

---

For detailed information, see: `REPORT_PROCESSING_GUIDE.md`
