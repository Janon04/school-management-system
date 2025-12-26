from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    path('structure/', views.fee_structure_view, name='fee_structure'),
    path('payments/', views.payment_list_view, name='payment_list'),
    path('student/<int:student_id>/', views.student_fees_view, name='student_fees'),
    path('student/<int:student_id>/record/', views.record_payment_view, name='record_payment'),
]
