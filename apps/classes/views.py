"""
Views for Class and Subject Management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import admin_required, teacher_required
from .models import ClassRoom, Subject, ClassSubject, TimeTable, AcademicYear
from .forms import ClassRoomForm, ClassSubjectForm

@login_required
@admin_required
def classsubject_create_view(request):
    """Create new ClassSubject assignments (assign multiple subjects to a class)"""
    if request.method == 'POST':
        form = ClassSubjectForm(request.POST)
        if form.is_valid():
            class_room = form.cleaned_data['class_room']
            subjects = form.cleaned_data['subjects']
            teacher = form.cleaned_data['teacher']
            is_active = form.cleaned_data['is_active']
            from .models import ClassSubject
            for subject in subjects:
                ClassSubject.objects.get_or_create(
                    class_room=class_room,
                    subject=subject,
                    defaults={'teacher': teacher, 'is_active': is_active}
                )
            messages.success(request, 'ClassSubject assignments created successfully!')
            return redirect('classes:subject_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ClassSubjectForm()
    return render(request, 'classes/classsubject_form.html', {'form': form, 'title': 'Assign Teacher to Subject/Class', 'button_text': 'Assign'})

@login_required
def class_subjects_view(request, class_id):
    """List all subjects registered for a specific class"""
    class_room = get_object_or_404(ClassRoom, pk=class_id)
    class_subjects = class_room.class_subjects.select_related('subject', 'teacher').filter(is_active=True)
    return render(request, 'classes/class_subjects.html', {
        'class_room': class_room,
        'class_subjects': class_subjects,
    })

@login_required
@admin_required
def class_update_view(request, pk):
    """Update an existing class (frontend form)"""
    class_room = get_object_or_404(ClassRoom, pk=pk)
    if request.method == 'POST':
        form = ClassRoomForm(request.POST, instance=class_room)
        if form.is_valid():
            form.save()
            messages.success(request, f'Class "{class_room}" updated successfully!')
            return redirect('classes:class_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ClassRoomForm(instance=class_room)
    return render(request, 'classes/class_form.html', {'form': form, 'title': f'Edit Class - {class_room}', 'button_text': 'Update Class'})

@login_required
@admin_required
def class_create_view(request):
    """Create a new class (frontend form)"""
    if request.method == 'POST':
        form = ClassRoomForm(request.POST)
        if form.is_valid():
            class_room = form.save()
            messages.success(request, f'Class "{class_room}" created successfully!')
            return redirect('classes:class_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ClassRoomForm()
    return render(request, 'classes/class_form.html', {'form': form, 'title': 'Add New Class', 'button_text': 'Create Class'})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import admin_required, teacher_required
from .models import ClassRoom, Subject, ClassSubject, TimeTable, AcademicYear


@login_required
def class_list_view(request):
    """List all classes (teachers see only their classes)"""
    if hasattr(request.user, 'teacher_profile'):
        # Only show classes where this teacher is assigned
        classes = ClassRoom.objects.filter(is_active=True, class_teacher=request.user.teacher_profile).select_related('class_teacher', 'academic_year')
    else:
        classes = ClassRoom.objects.filter(is_active=True).select_related('class_teacher', 'academic_year')
    return render(request, 'classes/class_list.html', {'classes': classes})


@login_required
def class_detail_view(request, pk):
    """View class details (teachers only see their own classes)"""
    class_room = get_object_or_404(ClassRoom, pk=pk)
    # If teacher, restrict access
    if hasattr(request.user, 'teacher_profile') and class_room.class_teacher != request.user.teacher_profile:
        messages.error(request, 'You do not have permission to view this class.')
        return redirect('classes:class_list')
    students = class_room.students.filter(is_active=True)
    subjects = class_room.class_subjects.filter(is_active=True)
    timetable = class_room.timetable_entries.all()
    context = {
        'class_room': class_room,
        'students': students,
        'subjects': subjects,
        'timetable': timetable,
    }
    return render(request, 'classes/class_detail.html', context)


@login_required
def subject_list_view(request):
    """List all subjects (teachers see only their assigned subjects)"""
    my_subjects = []
    is_teacher = hasattr(request.user, 'teacher_profile') and request.user.role == 'TEACHER'
    if is_teacher:
        class_subjects = ClassSubject.objects.filter(
            teacher=request.user.teacher_profile,
            is_active=True
        ).select_related('subject', 'class_room')
        # Unique subjects for this teacher
        seen = set()
        for cs in class_subjects:
            if cs.subject.id not in seen:
                my_subjects.append(cs.subject)
                seen.add(cs.subject.id)
    subjects = Subject.objects.filter(is_active=True)
    return render(request, 'classes/subject_list.html', {
        'subjects': subjects,
        'my_subjects': my_subjects,
        'is_teacher': is_teacher
    })


@login_required
@admin_required
def subject_create_view(request):
    """Create a new subject"""
    from apps.teachers.models import Teacher
    teachers = Teacher.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        category = request.POST.get('category')
        description = request.POST.get('description', '')
        pass_mark = request.POST.get('pass_mark', 40)
        total_marks = request.POST.get('total_marks', 100)
        teacher_id = request.POST.get('teacher')
        try:
            subject = Subject.objects.create(
                name=name,
                code=code,
                category=category,
                description=description,
                pass_mark=int(pass_mark),
                total_marks=int(total_marks)
            )
            # Assign teacher if selected
            if teacher_id:
                from apps.classes.models import ClassSubject
                # You may want to create a ClassSubject here if class is selected
                # For now, just assign teacher to subject (if you use M2M)
                teacher = Teacher.objects.filter(id=teacher_id).first()
                if teacher:
                    subject.teachers.add(teacher)
            messages.success(request, f'Subject "{subject.name}" created successfully!')
            return redirect('classes:subject_detail', pk=subject.pk)
        except Exception as e:
            messages.error(request, f'Error creating subject: {str(e)}')
    
    return render(request, 'classes/subject_form.html', {'action': 'Create', 'teachers': teachers})


@login_required
@admin_required
def subject_update_view(request, pk):
    """Update an existing subject"""
    subject = get_object_or_404(Subject, pk=pk)
    from apps.teachers.models import Teacher
    teachers = Teacher.objects.filter(is_active=True)
    from .models import ClassRoom, ClassSubject
    classes = ClassRoom.objects.filter(is_active=True)
    assigned_classes = [cs.class_room for cs in subject.class_subjects.all()]

    if request.method == 'POST':
        subject.name = request.POST.get('name')
        subject.code = request.POST.get('code')
        subject.category = request.POST.get('category')
        subject.description = request.POST.get('description', '')
        subject.pass_mark = int(request.POST.get('pass_mark', 40))
        subject.total_marks = int(request.POST.get('total_marks', 100))

        # Handle teacher assignment
        teacher_ids = request.POST.getlist('teachers')
        subject.save()
        subject.teachers.set(teacher_ids)

        # Handle class assignment
        class_ids = request.POST.getlist('classes')
        # Remove old assignments not in new selection
        ClassSubject.objects.filter(subject=subject).exclude(class_room_id__in=class_ids).delete()
        # Add new assignments
        for class_id in class_ids:
            ClassSubject.objects.get_or_create(class_room_id=class_id, subject=subject)

        try:
            messages.success(request, f'Subject "{subject.name}" updated successfully!')
            return redirect('classes:subject_detail', pk=subject.pk)
        except Exception as e:
            messages.error(request, f'Error updating subject: {str(e)}')

    return render(request, 'classes/subject_form.html', {
        'subject': subject,
        'action': 'Update',
        'teachers': teachers,
        'classes': classes,
        'assigned_classes': assigned_classes
    })


@login_required
def subject_detail_view(request, pk):
    """View subject details"""
    subject = get_object_or_404(Subject, pk=pk)
    classes = subject.class_subjects.filter(is_active=True)
    # Get teachers assigned to this subject via ClassSubject, avoid duplicates
    class_subjects = subject.class_subjects.filter(is_active=True, teacher__isnull=False).select_related('teacher')
    teacher_ids = set()
    teachers = []
    for cs in class_subjects:
        if cs.teacher and cs.teacher.id not in teacher_ids:
            teachers.append(cs.teacher)
            teacher_ids.add(cs.teacher.id)
    context = {
        'subject': subject,
        'classes': classes,
        'teachers': teachers,
        'class_subjects': subject.class_subjects.filter(is_active=True),
    }
    return render(request, 'classes/subject_detail.html', context)


@login_required
@teacher_required
def timetable_view(request, class_id):
    """View timetable for a class"""
    class_room = get_object_or_404(ClassRoom, pk=class_id)
    timetable = TimeTable.objects.filter(class_room=class_room).order_by('day', 'start_time')
    
    # Organize by day
    days = {}
    for entry in timetable:
        if entry.day not in days:
            days[entry.day] = []
        days[entry.day].append(entry)
    
    context = {
        'class_room': class_room,
        'timetable': days,
    }
    return render(request, 'classes/timetable.html', context)
