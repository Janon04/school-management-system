"""
Views for authentication and user management
Handles login, logout, registration, password management, and dashboard
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import User
from .forms import UserLoginForm, UserRegistrationForm


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name()}!')
                    
                    # Redirect based on role
                    next_url = request.GET.get('next', 'dashboard')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Your account is inactive. Please contact admin.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


def register_view(request):
    """User registration view (for initial setup or self-registration if enabled)"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Automatically create corresponding profile based on role
            try:
                if user.role == 'TEACHER':
                    from apps.teachers.models import Teacher
                    from django.utils import timezone
                    
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
                    messages.success(request, 'Teacher account created! Please complete your profile through admin.')
                    
                elif user.role == 'STUDENT':
                    from apps.students.models import Student
                    from django.utils import timezone
                    
                    Student.objects.create(
                        user=user,
                        date_of_birth=timezone.now().date(),  # Placeholder
                        gender='O',  # Other/unspecified
                        emergency_contact_name='To be updated',
                        emergency_contact_phone='000000000',
                        emergency_contact_relation='Guardian'
                    )
                    messages.success(request, 'Student account created! Please complete your profile through admin.')
                    
                elif user.role == 'PARENT':
                    from apps.parents.models import Parent
                    
                    Parent.objects.create(
                        user=user,
                        relation='GUARDIAN'  # Default relation
                    )
                    messages.success(request, 'Parent account created! Please complete your profile through admin.')
                    
                else:
                    messages.success(request, 'Account created successfully! Please login.')
                    
            except Exception as e:
                messages.warning(request, f'Account created but profile setup incomplete: {str(e)}')
            
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'auth/register.html', {'form': form})


@login_required
def dashboard_view(request):
    """
    Main dashboard - displays different content based on user role
    """
    user = request.user
    context = {
        'user': user,
        'current_date': timezone.now()
    }
    
    # Admin Dashboard
    if user.is_admin or user.is_staff_member or user.is_superuser:
        from apps.students.models import Student
        from apps.teachers.models import Teacher
        from apps.parents.models import Parent
        from apps.attendance.models import Attendance
        from apps.fees.models import Payment
        from apps.classes.models import ClassRoom
        from apps.exams.models import Exam
        
        today = timezone.now().date()
        
        context.update({
            'total_students': Student.objects.count(),
            'total_teachers': Teacher.objects.count(),
            'total_parents': Parent.objects.count(),
            'total_staff': User.objects.filter(role='STAFF').count(),
            'active_classes': ClassRoom.objects.filter(is_active=True).count(),
            'upcoming_exams': Exam.objects.filter(start_date__gte=today).count(),
            'today_attendance': Attendance.objects.filter(date=today, status='Present').count(),
            'recent_payments': Payment.objects.order_by('-payment_date')[:5],
        })
    
    # Teacher Dashboard
    elif user.is_teacher:
        from apps.teachers.models import Teacher
        from apps.classes.models import ClassRoom
        
        try:
            teacher = Teacher.objects.get(user=user)
            context.update({
                'teacher': teacher,
                'subjects': teacher.subjects.all(),
                'classes_assigned': ClassRoom.objects.filter(class_teacher=teacher),
            })
        except Teacher.DoesNotExist:
            messages.warning(request, 'Your teacher profile is not complete. Please contact admin.')
    
    # Student Dashboard
    elif user.is_student:
        from apps.students.models import Student
        from apps.results.models import Result
        
        try:
            student = Student.objects.get(user=user)
            context.update({
                'student': student,
                'class_room': student.class_assigned,
                'recent_results': Result.objects.filter(student=student).order_by('-exam__date')[:5],
            })
        except Student.DoesNotExist:
            messages.warning(request, 'Your student profile is not complete. Please contact admin.')
    
    # Parent Dashboard
    elif user.is_parent:
        from apps.parents.models import Parent
        from apps.students.models import Student
        
        try:
            parent = Parent.objects.get(user=user)
            children = Student.objects.filter(parent=parent)
            context.update({
                'parent': parent,
                'children': children,
            })
        except Parent.DoesNotExist:
            messages.warning(request, 'Your parent profile is not complete. Please contact admin.')
    
    return render(request, 'dashboard.html', context)


@login_required
def profile_view(request):
    """User profile view"""
    return render(request, 'auth/profile.html', {'user': request.user})


@login_required
def profile_update_view(request):
    """Update user profile"""
    from .forms import UserProfileUpdateForm
    
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile_update')
    else:
        form = UserProfileUpdateForm(instance=request.user)
    
    return render(request, 'auth/profile_update.html', {'user': request.user, 'form': form})
