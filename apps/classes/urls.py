"""
URL configuration for classes app
"""
from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    path('', views.class_list_view, name='class_list'),
    path('create/', views.class_create_view, name='class_create'),
    path('<int:pk>/edit/', views.class_update_view, name='class_update'),
    path('<int:pk>/', views.class_detail_view, name='class_detail'),
    path('<int:class_id>/timetable/', views.timetable_view, name='timetable'),
    path('<int:class_id>/subjects/', views.class_subjects_view, name='class_subjects'),
    path('subjects/', views.subject_list_view, name='subject_list'),
    path('subjects/create/', views.subject_create_view, name='subject_create'),
    path('subjects/<int:pk>/', views.subject_detail_view, name='subject_detail'),
    path('subjects/<int:pk>/edit/', views.subject_update_view, name='subject_update'),
    path('assign/', views.classsubject_create_view, name='classsubject_create'),
]
