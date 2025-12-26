"""
Fees Management Models
"""
from django.db import models
from django.core.validators import MinValueValidator
from apps.students.models import Student
from apps.classes.models import ClassRoom, AcademicYear


class FeeStructure(models.Model):
    """
    Fee structure for different classes
    """
    
    FEE_TYPE_CHOICES = (
        ('TUITION', 'Tuition Fee'),
        ('ADMISSION', 'Admission Fee'),
        ('EXAM', 'Examination Fee'),
        ('LIBRARY', 'Library Fee'),
        ('LAB', 'Laboratory Fee'),
        ('TRANSPORT', 'Transport Fee'),
        ('SPORTS', 'Sports Fee'),
        ('OTHER', 'Other Fee'),
    )
    
    FREQUENCY_CHOICES = (
        ('ONE_TIME', 'One Time'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('ANNUALLY', 'Annually'),
    )
    
    class_room = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name='fee_structures'
    )
    
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='fee_structures'
    )
    
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    due_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['class_room', 'fee_type']
        verbose_name = 'Fee Structure'
        verbose_name_plural = 'Fee Structures'
    
    def __str__(self):
        return f"{self.class_room} - {self.get_fee_type_display()} - {self.amount}"


class Payment(models.Model):
    """
    Student payment records
    """
    
    PAYMENT_METHOD_CHOICES = (
        ('CASH', 'Cash'),
        ('CHEQUE', 'Cheque'),
        ('CARD', 'Debit/Credit Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('MOBILE_MONEY', 'Mobile Money'),
        ('OTHER', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    )
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    
    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_reference = models.CharField(
        max_length=100,
        unique=True,
        help_text='Unique transaction ID'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='COMPLETED'
    )
    
    remarks = models.TextField(blank=True)
    
    received_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='payments_received'
    )
    
    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        indexes = [
            models.Index(fields=['student', 'payment_date']),
            models.Index(fields=['transaction_reference']),
        ]
    
    def __str__(self):
        return f"{self.student.admission_number} - {self.amount_paid} - {self.payment_date}"
    
    def save(self, *args, **kwargs):
        """Generate receipt number if not exists"""
        if not self.receipt_number:
            from django.utils import timezone
            year = timezone.now().year
            count = Payment.objects.filter(payment_date__year=year).count() + 1
            self.receipt_number = f"REC{year}{count:06d}"
        super().save(*args, **kwargs)


class FeeBalance(models.Model):
    """
    Track fee balance for each student
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='fee_balances'
    )
    
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE
    )
    
    total_fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    total_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'academic_year']
        verbose_name = 'Fee Balance'
        verbose_name_plural = 'Fee Balances'
    
    def __str__(self):
        return f"{self.student.admission_number} - Balance: {self.balance}"
    
    def update_balance(self):
        """Recalculate balance"""
        self.balance = self.total_fees - self.total_paid
        self.save()
