"""
Views for Notifications and Notices
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notice, Notification, Message


@login_required
def notice_board_view(request):
    """Display notice board"""
    user = request.user
    
    # Filter notices based on user role
    if user.is_student:
        notices = Notice.objects.filter(
            is_active=True,
            target_audience__in=['ALL', 'STUDENTS']
        )
    elif user.is_teacher:
        notices = Notice.objects.filter(
            is_active=True,
            target_audience__in=['ALL', 'TEACHERS']
        )
    elif user.is_parent:
        notices = Notice.objects.filter(
            is_active=True,
            target_audience__in=['ALL', 'PARENTS']
        )
    else:
        notices = Notice.objects.filter(is_active=True)
    
    return render(request, 'notifications/notice_board.html', {'notices': notices})


@login_required
def notifications_view(request):
    """View user notifications"""
    notifications = Notification.objects.filter(user=request.user)
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/notifications.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.mark_as_read()
    
    if request.is_ajax():
        return JsonResponse({'success': True})
    return redirect('notifications:notifications')


@login_required
def messages_view(request):
    """View messages inbox"""
    messages = Message.objects.filter(recipient=request.user)
    unread_count = messages.filter(is_read=False).count()
    
    context = {
        'messages': messages,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/messages.html', context)
