from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notice Board
    path('notices/', views.notice_board_view, name='notice_board'),
    path('notices/create/', views.notice_create_view, name='notice_create'),
    path('notices/<int:pk>/', views.notice_detail_view, name='notice_detail'),
    path('notices/<int:pk>/edit/', views.notice_update_view, name='notice_update'),
    path('notices/<int:pk>/delete/', views.notice_delete_view, name='notice_delete'),
    
    # Notifications
    path('', views.notifications_view, name='notifications'),
    path('create/', views.notification_create_view, name='notification_create'),
    path('<int:notification_id>/read/', views.mark_notification_read, name='mark_read'),
    
    # Messages
    path('messages/', views.messages_view, name='messages'),
]
