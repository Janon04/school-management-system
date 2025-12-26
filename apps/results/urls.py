from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    # Report Processing Dashboard
    path('processing/<int:exam_id>/', views.report_processing_view, name='report_processing'),
    
    # Result Entry
    path('enter/<int:exam_id>/<int:class_id>/', views.enter_results_view, name='enter_results'),
    path('save/<int:exam_id>/<int:class_id>/', views.save_results_view, name='save_results'),
    
    # Report Generation
    path('generate/<int:exam_id>/<int:class_id>/', views.generate_reports_view, name='generate_reports'),
    path('generate-all/<int:exam_id>/<int:class_id>/', views.generate_all_reports_view, name='generate_all_reports'),
    path('generate-single/<int:exam_id>/<int:student_id>/', views.generate_single_report_view, name='generate_single_report'),
    
    # Ranks
    path('calculate-ranks/<int:exam_id>/<int:class_id>/', views.calculate_ranks_view, name='calculate_ranks'),
    
    # Publishing
    path('publish/<int:exam_id>/<int:class_id>/', views.publish_results_view, name='publish_results'),
    
    # Report Card View
    path('report-card/<int:student_id>/<int:exam_id>/', views.report_card_view, name='report_card'),
    
    # Student Results
    path('student/<int:student_id>/', views.student_results_view, name='student_results'),
]
