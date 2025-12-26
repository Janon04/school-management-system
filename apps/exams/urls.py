from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('', views.exam_list_view, name='exam_list'),
    path('<int:exam_id>/', views.exam_detail_view, name='exam_detail'),
    path('<int:exam_id>/schedule/', views.exam_schedule_view, name='exam_schedule'),
]
