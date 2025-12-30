from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from apps.accounts.decorators import admin_required
from .models import Promotion
from .forms import PromotionForm
from apps.students.models import Student
from apps.classes.models import ClassRoom, AcademicYear


@login_required
@admin_required
def promotion_list_view(request):
    """List all promotions"""
    promotions = Promotion.objects.all().order_by('-promoted_on')
    return render(request, 'promotions/promotion_list.html', {'promotions': promotions})


@login_required
@admin_required
def promote_students_view(request):
    """View for bulk student promotion"""
    if request.method == 'POST':
        # Get form data
        student_ids = request.POST.getlist('student')
        from_class_id = request.POST.get('from_class')
        to_class_id = request.POST.get('to_class')
        from_academic_year_id = request.POST.get('from_academic_year')
        to_academic_year_id = request.POST.get('to_academic_year')
        status = request.POST.get('status')
        remarks = request.POST.get('remarks', '')
        
        # Validate required fields
        if not student_ids:
            messages.error(request, 'Please select at least one student')
            return redirect('promotions:promote_students')
        
        if not from_class_id or not from_academic_year_id or not to_academic_year_id or not status:
            messages.error(request, 'Please fill all required fields')
            return redirect('promotions:promote_students')
        
        # For promoted students, to_class is required
        if status == 'PROMOTED' and not to_class_id:
            messages.error(request, 'Destination class is required for promoted students')
            return redirect('promotions:promote_students')
        
        # Get objects
        from_class = ClassRoom.objects.get(id=from_class_id)
        to_class = ClassRoom.objects.get(id=to_class_id) if to_class_id else None
        from_academic_year = AcademicYear.objects.get(id=from_academic_year_id)
        to_academic_year = AcademicYear.objects.get(id=to_academic_year_id)
        
        # Track success count
        success_count = 0
        skipped_count = 0
        
        # Create promotions for each student
        for student_id in student_ids:
            student = Student.objects.get(id=student_id)
            
            # Check if promotion already exists
            existing = Promotion.objects.filter(
                student=student,
                from_academic_year=from_academic_year,
                to_academic_year=to_academic_year
            ).exists()
            
            if not existing:
                Promotion.objects.create(
                    student=student,
                    from_class=from_class,
                    to_class=to_class,
                    from_academic_year=from_academic_year,
                    to_academic_year=to_academic_year,
                    status=status,
                    remarks=remarks,
                    promoted_by=request.user
                )
                success_count += 1
            else:
                skipped_count += 1
        
        # Show success message
        if success_count > 0:
            messages.success(request, f'Successfully promoted {success_count} student(s)')
        if skipped_count > 0:
            messages.warning(request, f'{skipped_count} student(s) already promoted for this academic year')
        
        return redirect('promotions:promotion_list')
    
    # GET request - show form
    context = {
        'classes': ClassRoom.objects.filter(is_active=True),
        'academic_years': AcademicYear.objects.all()
    }
    return render(request, 'promotions/promote_students.html', context)


@login_required
@admin_required
def get_students_by_class(request):
    """AJAX endpoint to get students by class"""
    class_id = request.GET.get('class_id')
    if not class_id:
        return JsonResponse({'error': 'Class ID required'}, status=400)
    
    try:
        students = Student.objects.filter(
            class_assigned_id=class_id,
            is_active=True
        ).select_related('user').order_by('user__first_name', 'user__last_name')
        
        students_data = [
            {
                'id': student.id,
                'name': student.user.get_full_name(),
                'admission_number': student.admission_number,
                'gender': student.gender if hasattr(student, 'gender') else 'N/A'
            }
            for student in students
        ]
        
        return JsonResponse({'students': students_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@admin_required
def promotion_create_view(request):
    """Create a new promotion record"""
    if request.method == 'POST':
        # Get selected students (can be multiple)
        student_ids = request.POST.getlist('student')
        
        if not student_ids:
            messages.error(request, 'Please select at least one student.')
            form = PromotionForm(request.POST)
        else:
            # Get common form data
            from_class_id = request.POST.get('from_class')
            to_class_id = request.POST.get('to_class')
            from_academic_year_id = request.POST.get('from_academic_year')
            to_academic_year_id = request.POST.get('to_academic_year')
            status = request.POST.get('status')
            remarks = request.POST.get('remarks', '')
            
            try:
                from apps.students.models import Student
                from apps.classes.models import ClassRoom, AcademicYear
                
                from_class = ClassRoom.objects.get(pk=from_class_id)
                to_class = ClassRoom.objects.get(pk=to_class_id) if to_class_id else None
                from_academic_year = AcademicYear.objects.get(pk=from_academic_year_id)
                to_academic_year = AcademicYear.objects.get(pk=to_academic_year_id)
                
                # Create promotion records for each selected student
                created_count = 0
                for student_id in student_ids:
                    student = Student.objects.get(pk=student_id)
                    
                    # Check if promotion already exists
                    existing = Promotion.objects.filter(
                        student=student,
                        from_academic_year=from_academic_year,
                        to_academic_year=to_academic_year
                    ).first()
                    
                    if not existing:
                        Promotion.objects.create(
                            student=student,
                            from_class=from_class,
                            to_class=to_class,
                            from_academic_year=from_academic_year,
                            to_academic_year=to_academic_year,
                            status=status,
                            remarks=remarks,
                            promoted_by=request.user
                        )
                        created_count += 1
                
                if created_count > 0:
                    messages.success(request, f'Successfully created {created_count} promotion record(s)!')
                else:
                    messages.warning(request, 'No new promotions created. All selected students already have promotion records.')
                
                return redirect('promotions:promotion_list')
                
            except Exception as e:
                messages.error(request, f'Error creating promotions: {str(e)}')
                form = PromotionForm(request.POST)
    else:
        form = PromotionForm()
    
    context = {
        'form': form,
        'action': 'Create',
        'submit_text': 'Create Promotion(s)'
    }
    return render(request, 'promotions/promotion_form.html', context)


@login_required
@admin_required
def promotion_update_view(request, pk):
    """Update an existing promotion record"""
    promotion = get_object_or_404(Promotion, pk=pk)
    
    if request.method == 'POST':
        form = PromotionForm(request.POST, instance=promotion)
        if form.is_valid():
            form.save()
            messages.success(request, f'Promotion record updated successfully!')
            return redirect('promotions:promotion_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PromotionForm(instance=promotion)
    
    context = {
        'form': form,
        'promotion': promotion,
        'action': 'Update',
        'submit_text': 'Update Promotion'
    }
    return render(request, 'promotions/promotion_form.html', context)


@login_required
@admin_required
def promotion_delete_view(request, pk):
    """Delete a promotion record"""
    promotion = get_object_or_404(Promotion, pk=pk)
    
    if request.method == 'POST':
        student_name = promotion.student.user.get_full_name()
        promotion.delete()
        messages.success(request, f'Promotion record for {student_name} deleted successfully!')
        return redirect('promotions:promotion_list')
    
    context = {
        'promotion': promotion
    }
    return render(request, 'promotions/promotion_confirm_delete.html', context)
