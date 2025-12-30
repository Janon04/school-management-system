from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.staff_list_view, name='staff_list'),
    path('create/', views.staff_create_view, name='staff_create'),
    path('<int:pk>/', views.staff_detail_view, name='staff_detail'),
    path('<int:pk>/edit/', views.staff_update_view, name='staff_update'),
]
