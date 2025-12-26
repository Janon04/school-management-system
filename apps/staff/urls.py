from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.staff_list_view, name='staff_list'),
    path('<int:pk>/', views.staff_detail_view, name='staff_detail'),
]
