from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_home_view, name='attendance_home'),
    path('mark/<int:class_id>/', views.mark_attendance_view, name='mark_attendance'),
    path('report/', views.attendance_report_view, name='attendance_report'),
    path('report/<int:student_id>/', views.attendance_report_view, name='student_attendance_report'),
    path('api/mark/', views.mark_attendance_ajax, name='mark_attendance_ajax'),
]
