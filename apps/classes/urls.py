"""
URL configuration for classes app
"""
from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    path('', views.class_list_view, name='class_list'),
    path('<int:pk>/', views.class_detail_view, name='class_detail'),
    path('<int:class_id>/timetable/', views.timetable_view, name='timetable'),
    path('subjects/', views.subject_list_view, name='subject_list'),
    path('subjects/<int:pk>/', views.subject_detail_view, name='subject_detail'),
]
