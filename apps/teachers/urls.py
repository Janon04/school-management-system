"""
URL configuration for teachers app
"""
from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('', views.teacher_list_view, name='teacher_list'),
    path('<int:pk>/', views.teacher_detail_view, name='teacher_detail'),
]
