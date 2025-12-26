from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('notices/', views.notice_board_view, name='notice_board'),
    path('', views.notifications_view, name='notifications'),
    path('<int:notification_id>/read/', views.mark_notification_read, name='mark_read'),
    path('messages/', views.messages_view, name='messages'),
]
