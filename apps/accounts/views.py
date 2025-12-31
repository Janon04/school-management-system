
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import User
from django.contrib.auth import login, logout, authenticate
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .forms import UserLoginForm, UserRegistrationForm
from apps.exams.models import ExamSchedule

@login_required
def user_create_view(request):
    """Create a new user (frontend form, admin only)"""
    if not request.user.is_admin:
        messages.error(request, 'You do not have permission to add users.')
        return redirect('accounts:user_list')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, f'User "{user.username}" created successfully!')
            return redirect('accounts:user_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Add New User', 'button_text': 'Create User'})

@login_required
def user_detail_view(request, user_id):
    """Display a user's profile (frontend view)"""
    user_obj = User.objects.filter(pk=user_id).first()
    if not user_obj:
        messages.error(request, 'User not found.')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_detail.html', {'user_obj': user_obj})

@login_required
def user_delete_view(request, user_id):
    """Delete a user (frontend action, admin/staff only)"""
    if not (request.user.is_admin or request.user.is_staff_member or request.user.is_superuser):
        return HttpResponseForbidden("You do not have permission to delete users.")
    user = User.objects.filter(pk=user_id).first()
    if not user:
        return JsonResponse({'success': False, 'error': 'User not found.'}, status=404)
    if request.method == 'POST':
        if user == request.user:
            return JsonResponse({'success': False, 'error': 'You cannot delete your own account.'}, status=400)
        user.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=405)

@login_required
def user_list_view(request):
    """Frontend user list table view (only ADMIN, TEACHER, PARENT)"""
    query = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '').strip()
    allowed_roles = ['ADMIN', 'TEACHER', 'PARENT']
    users = User.objects.filter(role__in=allowed_roles)
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    if role_filter and role_filter in allowed_roles:
        users = users.filter(role=role_filter)
    users = users.order_by('-date_joined')
    context = {
        'users': users,
        'query': query,
        'role_filter': role_filter,
    }
    return render(request, 'accounts/user_list.html', context)
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
from apps.exams.models import ExamSchedule


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
    
    # Debug output
    print(f"DEBUG: User {user.username}, Role: {user.role if hasattr(user, 'role') else 'NO ROLE'}, Superuser: {user.is_superuser}")
    print(f"DEBUG: is_admin={user.is_admin}, is_staff_member={user.is_staff_member}, is_superuser={user.is_superuser}")
    
    # Admin Dashboard
    if user.is_admin or user.is_staff_member or user.is_superuser:
        from apps.students.models import Student
        from apps.teachers.models import Teacher
        from apps.parents.models import Parent
        from apps.attendance.models import Attendance
        from apps.fees.models import Payment
        from apps.classes.models import ClassRoom
        from apps.exams.models import Exam
        from apps.results.models import Result
        from apps.promotions.models import Promotion
        from apps.notifications.models import Notification
        from django.db.models import Count, Sum, Avg
        
        today = timezone.now().date()
        from datetime import timedelta
        last_30_days = today - timedelta(days=30)
        
        # Student statistics
        total_students = Student.objects.count()
        active_students = Student.objects.filter(is_active=True).count()
        male_students = Student.objects.filter(gender='M').count()
        female_students = Student.objects.filter(gender='F').count()
        
        # Teacher statistics
        total_teachers = Teacher.objects.count()
        active_teachers = Teacher.objects.filter(user__is_active=True).count()
        
        # Class statistics
        total_classes = ClassRoom.objects.count()
        active_classes = ClassRoom.objects.filter(is_active=True).count()
        
        # Exam statistics
        total_exams = Exam.objects.count()
        upcoming_exams = Exam.objects.filter(start_date__gte=today).count()
        completed_exams = Exam.objects.filter(end_date__lt=today).count()
        
        # Attendance statistics (today)
        today_attendance = Attendance.objects.filter(date=today, status='Present').count()
        today_absent = Attendance.objects.filter(date=today, status='Absent').count()
        today_late = Attendance.objects.filter(date=today, status='Late').count()
        today_excused = Attendance.objects.filter(date=today, status='Excused').count()
        total_marked_today = Attendance.objects.filter(date=today).count()
        
        # Results statistics
        total_results = Result.objects.count()
        avg_score = Result.objects.aggregate(avg=Avg('marks_obtained'))['avg'] or 0
        
        # Payment statistics
        total_revenue = Payment.objects.filter(payment_date__gte=last_30_days).aggregate(
            total=Sum('amount_paid')
        )['total'] or 0
        total_payments = Payment.objects.count()
        pending_payments = Student.objects.filter(is_active=True).count() - Payment.objects.values('student').distinct().count()
        
        # Recent activity
        recent_payments = Payment.objects.select_related('student__user').order_by('-payment_date')[:5]
        recent_results = Result.objects.select_related('student__user', 'exam', 'subject').order_by('-created_at')[:5]
        recent_students = Student.objects.select_related('user', 'class_assigned').order_by('-created_at')[:5]
        
        # Promotions
        total_promotions = Promotion.objects.count()
        recent_promotions = Promotion.objects.select_related('student__user', 'from_class', 'to_class').order_by('-promoted_on')[:5]
        
        # Notifications
        unread_notifications = Notification.objects.filter(is_read=False).count()
        
        # System users
        total_parents = Parent.objects.count()
        total_staff = User.objects.filter(role='STAFF').count()
        total_users = User.objects.count()
        
        print(f"DEBUG: Fetched stats - Students: {total_students}, Teachers: {total_teachers}, Classes: {active_classes}")
        
        context.update({
            # Student stats
            'total_students': total_students,
            'active_students': active_students,
            'male_students': male_students,
            'female_students': female_students,
            
            # Teacher stats
            'total_teachers': total_teachers,
            'active_teachers': active_teachers,
            
            # Class stats
            'total_classes': total_classes,
            'active_classes': active_classes,
            
            # Exam stats
            'total_exams': total_exams,
            'upcoming_exams': upcoming_exams,
            'completed_exams': completed_exams,
            
            # Attendance stats
            'today_attendance': today_attendance,
            'today_absent': today_absent,
            'today_late': today_late,
            'today_excused': today_excused,
            'total_marked_today': total_marked_today,
            
            # Result stats
            'total_results': total_results,
            'avg_score': round(avg_score, 2),
            
            # Payment stats
            'total_revenue_30days': total_revenue,
            'total_payments': total_payments,
            'pending_payments': pending_payments,
            
            # Recent activity
            'recent_payments': recent_payments,
            'recent_results': recent_results,
            'recent_students': recent_students,
            'recent_promotions': recent_promotions,
            
            # Other stats
            'total_promotions': total_promotions,
            'unread_notifications': unread_notifications,
            'total_parents': total_parents,
            'total_staff': total_staff,
            'total_users': total_users,
        })
    
    # Teacher Dashboard
    elif user.is_teacher:
        from apps.teachers.models import Teacher
        from apps.classes.models import ClassRoom
        from apps.students.models import Student
        from apps.exams.models import Exam
        
        try:
            teacher = Teacher.objects.get(user=user)
            classes_assigned = ClassRoom.objects.filter(class_teacher=teacher)
            subjects = teacher.subjects.all()
            # Count students in teacher's classes
            total_students_teaching = Student.objects.filter(
                class_assigned__in=classes_assigned
            ).count()
            # Attendance marked today (for teacher's classes)
            from apps.attendance.models import Attendance
            today = timezone.now().date()
            attendance_marked_today = Attendance.objects.filter(
                class_room__in=classes_assigned, date=today
            ).values('class_room').distinct().count()
            # Upcoming exams - use schedules instead of direct exam filter
            from apps.exams.models import ExamSchedule
            upcoming_exams = ExamSchedule.objects.filter(
                subject__in=subjects,
                exam_date__gte=today
            ).count()
            context.update({
                'teacher': teacher,
                'subjects': subjects,
                'classes_assigned': classes_assigned,
                'total_students': total_students_teaching,
                'attendance_marked_today': attendance_marked_today,
                'upcoming_exams': upcoming_exams,
            })
        except Teacher.DoesNotExist:
            messages.warning(request, 'Your teacher profile is not complete. Please contact admin.')
    
    # Student Dashboard
    elif user.is_student:
        from apps.students.models import Student
        from apps.results.models import Result
        from apps.attendance.models import Attendance
        from django.db.models import Avg
        
        try:
            student = Student.objects.get(user=user)
            recent_results = Result.objects.filter(student=student).select_related(
                'exam', 'subject'
            ).order_by('-exam__date')[:5]
            
            # Calculate average score
            avg_score = Result.objects.filter(student=student).aggregate(
                avg=Avg('marks_obtained')
            )['avg'] or 0
            
            # Attendance statistics (last 30 days)
            from datetime import timedelta
            today = timezone.now().date()
            last_30_days = today - timedelta(days=30)
            
            attendance_stats = {
                'present': Attendance.objects.filter(
                    student=student, date__gte=last_30_days, status='Present'
                ).count(),
                'absent': Attendance.objects.filter(
                    student=student, date__gte=last_30_days, status='Absent'
                ).count(),
                'late': Attendance.objects.filter(
                    student=student, date__gte=last_30_days, status='Late'
                ).count(),
            }
            total_days = sum(attendance_stats.values())
            attendance_percentage = (attendance_stats['present'] / total_days * 100) if total_days > 0 else 0
            
            context.update({
                'student': student,
                'class_room': student.class_assigned,
                'recent_results': recent_results,
                'avg_score': round(avg_score, 2),
                'attendance_stats': attendance_stats,
                'attendance_percentage': round(attendance_percentage, 1),
            })
        except Student.DoesNotExist:
            messages.warning(request, 'Your student profile is not complete. Please contact admin.')
    
    # Parent Dashboard
    elif user.is_parent:
        from apps.parents.models import Parent
        from apps.students.models import Student
        from apps.results.models import Result
        from apps.attendance.models import Attendance
        from datetime import timedelta
        
        try:
            parent = Parent.objects.get(user=user)
            children = Student.objects.filter(parent=parent).select_related('class_assigned')
            # Get recent results for all children
            recent_results = Result.objects.filter(
                student__in=children
            ).select_related('student__user', 'exam', 'subject').order_by('-exam__date')[:10]
            # Get attendance summary for all children (this term)
            from apps.attendance.models import Attendance
            from django.db.models import Avg
            # Calculate average performance for all children
            from apps.results.models import Result
            if children:
                average_performance = Result.objects.filter(student__in=children).aggregate(avg=Avg('marks_obtained'))['avg']
                if average_performance is not None:
                    average_performance = round(average_performance, 1)
                else:
                    average_performance = '-'
                # Attendance this term (present days / total days for all children)
                present = Attendance.objects.filter(student__in=children, status='Present').count()
                total = Attendance.objects.filter(student__in=children).count()
                if total > 0:
                    attendance_this_term = f"{present} / {total}"
                else:
                    attendance_this_term = '-'
            else:
                average_performance = '-'
                attendance_this_term = '-'
            # Unread notifications (reuse from admin context if available)
            unread_notifications = context.get('unread_notifications', 0)
            context.update({
                'parent': parent,
                'children': children,
                'recent_results': recent_results,
                'average_performance': average_performance,
                'attendance_this_term': attendance_this_term,
                'unread_notifications': unread_notifications,
            })
        except Parent.DoesNotExist:
            messages.warning(request, 'Your parent profile is not complete. Please contact admin.')
    
    return render(request, 'dashboard.html', context)


@login_required
def profile_view(request):
    """User profile view"""
    teacher_profile = getattr(request.user, 'teacher_profile', None)
    staff_profile = getattr(request.user, 'staff_profile', None)
    return render(request, 'auth/profile.html', {
        'user': request.user,
        'teacher_profile': teacher_profile,
        'staff_profile': staff_profile,
    })



@login_required
def profile_update_view(request):
    """Update user profile. Superusers can update any user's role/status via ?user_id= param."""
    from .forms import UserProfileUpdateForm
    user_obj = request.user
    # Allow superuser to update other users
    user_id = request.GET.get('user_id')
    if request.user.is_superuser and user_id:
        from django.shortcuts import get_object_or_404
        user_obj = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=user_obj)
        updated = False
        if form.is_valid():
            form.save()
            updated = True
            # Allow superuser to update role and is_superuser
            if request.user.is_superuser and user_obj != request.user:
                new_role = request.POST.get('role')
                is_super = request.POST.get('is_superuser') == 'on'
                if new_role and new_role in dict(User.ROLE_CHOICES):
                    user_obj.role = new_role
                user_obj.is_superuser = is_super
                user_obj.save()
            # Save teacher professional info
            if user_obj.role == 'TEACHER' and hasattr(user_obj, 'teacher_profile'):
                teacher = user_obj.teacher_profile
                teacher.qualification = request.POST.get('qualification', teacher.qualification)
                teacher.specialization = request.POST.get('specialization', teacher.specialization)
                teacher.experience_years = request.POST.get('experience_years', teacher.experience_years)
                teacher.certifications = request.POST.get('certifications', teacher.certifications)
                teacher.bio = request.POST.get('bio', teacher.bio)
                teacher.save()
            # Save staff professional info
            if user_obj.role == 'STAFF' and hasattr(user_obj, 'staff_profile'):
                staff = user_obj.staff_profile
                staff.designation = request.POST.get('designation', staff.designation)
                joining_date = request.POST.get('joining_date', None)
                if joining_date:
                    staff.joining_date = joining_date
                salary = request.POST.get('salary', None)
                if salary:
                    staff.salary = salary
                staff.save()
            if updated:
                messages.success(request, 'Profile updated successfully!')
            else:
                messages.info(request, 'No changes detected.')
            # Redirect to same page for the edited user
            if request.user.is_superuser and user_id:
                return redirect(f"{request.path}?user_id={user_id}")
            return redirect('accounts:profile_update')
    else:
        form = UserProfileUpdateForm(instance=user_obj)
    return render(request, 'auth/profile_update.html', {'user': user_obj, 'form': form})


@login_required
def admin_access_view(request):
    """Verify credentials before allowing admin panel access"""
    # Check if user is eligible for admin access
    if not (request.user.role == 'ADMIN' and request.user.is_superuser):
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Verify credentials
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_superuser:
            # Store admin verification in session (expires after 15 minutes)
            request.session['admin_verified'] = True
            request.session['admin_verified_time'] = timezone.now().timestamp()
            messages.success(request, 'Admin access granted!')
            return redirect('/admin/')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions!')
    
    return render(request, 'auth/admin_access.html')
