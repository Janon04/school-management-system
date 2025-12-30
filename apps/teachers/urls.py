"""
URL configuration for teachers app
"""
from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('', views.teacher_list_view, name='teacher_list'),
    path('create/', views.teacher_create_view, name='teacher_create'),
    path('<int:pk>/', views.teacher_detail_view, name='teacher_detail'),
    path('<int:pk>/edit/', views.teacher_update_view, name='teacher_edit'),
]
