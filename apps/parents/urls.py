"""
URL configuration for parents app
"""
from django.urls import path
from . import views

app_name = 'parents'

urlpatterns = [
    path('', views.parent_list_view, name='parent_list'),
    path('create/', views.parent_create_view, name='parent_create'),
    path('<int:pk>/', views.parent_detail_view, name='parent_detail'),
    path('<int:pk>/edit/', views.parent_update_view, name='parent_update'),
]
