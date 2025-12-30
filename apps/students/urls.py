"""
URL configuration for students app
"""
from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_list_view, name='student_list'),
    path('<int:pk>/', views.student_detail_view, name='student_detail'),
    path('create/', views.student_create_view, name='student_create'),
    path('<int:pk>/edit/', views.student_update_view, name='student_update'),
    path('<int:pk>/delete/', views.student_delete_view, name='student_delete'),
]
