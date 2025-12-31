"""
Views for Fees Management
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import admin_required
from .models import FeeStructure, Payment, FeeBalance
from apps.students.models import Student
from .forms import FeeStructureForm

@login_required
@admin_required
def fee_structure_create_view(request):
    """Create a new fee structure (frontend)"""
    if request.method == 'POST':
        form = FeeStructureForm(request.POST)
        if form.is_valid():
            fee_structure = form.save()
            from django.contrib import messages
            messages.success(request, 'Fee structure added successfully!')
            return redirect('fees:fee_structure')
    else:
        form = FeeStructureForm()
    return render(request, 'fees/fee_structure_form.html', {'form': form, 'title': 'Add Fee Structure', 'button_text': 'Add Fee'})
"""
Views for Fees Management
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import admin_required
from .models import FeeStructure, Payment, FeeBalance
from apps.students.models import Student


@login_required
def fee_structure_view(request):
    """View fee structures"""
    fee_structures = FeeStructure.objects.filter(is_active=True).select_related('class_room', 'academic_year')
    
    # Calculate statistics
    unique_classes = fee_structures.values('class_room').distinct().count()
    unique_years = fee_structures.values('academic_year').distinct().count()
    unique_types = fee_structures.values('fee_type').distinct().count()
    total_amount = sum([fs.amount for fs in fee_structures])
    
    context = {
        'fee_structures': fee_structures,
        'unique_classes': unique_classes,
        'unique_years': unique_years,
        'unique_types': unique_types,
        'total_amount': total_amount,
    }
    return render(request, 'fees/fee_structure.html', context)


@login_required
def payment_list_view(request):
    """List all payments"""
    payments = Payment.objects.all().order_by('-payment_date')[:100]
    return render(request, 'fees/payment_list.html', {'payments': payments})


@login_required
def student_fees_view(request, student_id):
    """View student fees and payment history"""
    student = get_object_or_404(Student, pk=student_id)
    payments = Payment.objects.filter(student=student).order_by('-payment_date')
    
    try:
        balance = FeeBalance.objects.get(student=student)
    except FeeBalance.DoesNotExist:
        balance = None
    
    context = {
        'student': student,
        'payments': payments,
        'balance': balance,
    }
    return render(request, 'fees/student_fees.html', context)


@login_required
@admin_required
def record_payment_view(request, student_id):
    """Record a new payment"""
    student = get_object_or_404(Student, pk=student_id)
    # Payment form handling would go here
    return render(request, 'fees/record_payment.html', {'student': student})
