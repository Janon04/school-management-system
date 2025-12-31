
from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('', views.exam_list_view, name='exam_list'),
    path('create/', views.exam_create_view, name='exam_create'),
    path('<int:exam_id>/', views.exam_detail_view, name='exam_detail'),
    path('<int:exam_id>/edit/', views.exam_update_view, name='exam_update'),
    path('schedule/list/', views.exam_schedule_list_view, name='exam_schedule_list'),
    path('<int:exam_id>/schedule/', views.exam_schedule_view, name='exam_schedule'),
    path('<int:exam_id>/schedule/add/', views.exam_schedule_create_view, name='exam_schedule_add'),
    path('schedule/<int:pk>/edit/', views.exam_schedule_edit_view, name='exam_schedule_edit'),
    path('schedule/<int:pk>/delete/', views.exam_schedule_delete_view, name='exam_schedule_delete'),
    path('schedule/<int:pk>/update_status/', views.exam_schedule_update_status_view, name='exam_schedule_update_status'),
    path('ajax/get_subjects/', views.get_subjects_for_class, name='ajax_get_subjects'),
]
