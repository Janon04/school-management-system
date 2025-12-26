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
    fee_structures = FeeStructure.objects.filter(is_active=True)
    return render(request, 'fees/fee_structure.html', {'fee_structures': fee_structures})


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
