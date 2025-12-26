from django.contrib import admin
from .models import FeeStructure, Payment, FeeBalance


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['class_room', 'fee_type', 'amount', 'frequency', 'is_mandatory', 'is_active']
    list_filter = ['fee_type', 'frequency', 'is_mandatory', 'is_active', 'academic_year']
    search_fields = ['class_room__name', 'fee_type', 'description']
    autocomplete_fields = ['class_room', 'academic_year']
    
    fieldsets = (
        ('🏫 Class Information', {
            'fields': ('class_room', 'academic_year'),
        }),
        ('💵 Fee Details', {
            'fields': ('fee_type', 'amount', 'frequency', 'due_date'),
        }),
        ('📝 Description & Settings', {
            'fields': ('description', 'is_mandatory', 'is_active'),
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'get_student_name', 'amount_paid', 'payment_date', 'payment_method', 'status']
    list_filter = ['payment_date', 'payment_method', 'status']
    search_fields = ['student__admission_number', 'student__user__first_name', 'student__user__last_name', 
                     'transaction_reference', 'receipt_number']
    readonly_fields = ['receipt_number', 'created_at', 'updated_at']
    
    # Use autocomplete instead of raw_id for better user experience
    autocomplete_fields = ['student', 'fee_structure', 'received_by']
    
    fieldsets = (
        ('💰 Payment Information', {
            'fields': ('student', 'fee_structure', 'amount_paid'),
        }),
        ('📅 Payment Details', {
            'fields': ('payment_date', 'payment_method', 'transaction_reference', 'status'),
        }),
        ('📝 Additional Information', {
            'fields': ('remarks', 'received_by'),
        }),
        ('🧾 Receipt & Audit', {
            'fields': ('receipt_number', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name() or obj.student.admission_number
    get_student_name.short_description = 'Student Name'
    get_student_name.admin_order_field = 'student__user__first_name'
    
    # Auto-generate receipt number on save
    def save_model(self, request, obj, form, change):
        if not obj.receipt_number:
            # Generate receipt number
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            last_payment = Payment.objects.filter(receipt_number__startswith=f'REC-{date_str}').order_by('-receipt_number').first()
            if last_payment:
                last_num = int(last_payment.receipt_number.split('-')[-1])
                obj.receipt_number = f'REC-{date_str}-{last_num + 1:04d}'
            else:
                obj.receipt_number = f'REC-{date_str}-0001'
        super().save_model(request, obj, form, change)


@admin.register(FeeBalance)
class FeeBalanceAdmin(admin.ModelAdmin):
    list_display = ['get_student_name', 'academic_year', 'total_fees', 'total_paid', 'get_balance', 'last_updated']
    list_filter = ['academic_year']
    search_fields = ['student__admission_number', 'student__user__first_name', 'student__user__last_name']
    readonly_fields = ['last_updated']
    
    # Use autocomplete instead of raw_id
    autocomplete_fields = ['student', 'academic_year']
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name() or obj.student.admission_number
    get_student_name.short_description = 'Student'
    get_student_name.admin_order_field = 'student__user__first_name'
    
    def get_balance(self, obj):
        return obj.balance
    get_balance.short_description = 'Balance'
