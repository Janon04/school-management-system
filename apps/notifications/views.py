"""
Views for Notifications and Notices
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from apps.accounts.decorators import admin_required, teacher_required
from apps.accounts.models import User
from .models import Notice, Notification, Message
from .forms import NoticeForm, NotificationForm


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
def notice_detail_view(request, pk):
    """Display single notice details"""
    notice = get_object_or_404(Notice, pk=pk)
    
    # Check if user has permission to view this notice
    user = request.user
    can_view = False
    
    if user.is_admin or user.is_staff:
        can_view = True
    elif notice.target_audience == 'ALL':
        can_view = True
    elif notice.target_audience == 'STUDENTS' and user.is_student:
        can_view = True
    elif notice.target_audience == 'TEACHERS' and user.is_teacher:
        can_view = True
    elif notice.target_audience == 'PARENTS' and user.is_parent:
        can_view = True
    
    if not can_view:
        messages.error(request, 'You do not have permission to view this notice')
        return redirect('notifications:notice_board')
    
    return render(request, 'notifications/notice_detail.html', {'notice': notice})


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
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('notifications:notifications')


@login_required
def messages_view(request):
    """View messages inbox"""
    inbox_messages = Message.objects.filter(recipient=request.user)
    unread_count = inbox_messages.filter(is_read=False).count()
    
    context = {
        'messages': inbox_messages,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/messages.html', context)


@login_required
@admin_required
def notice_create_view(request):
    """Create a new notice"""
    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.posted_by = request.user
            notice.save()
            messages.success(request, f'Notice "{notice.title}" created successfully!')
            return redirect('notifications:notice_board')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = NoticeForm(initial={'is_active': True})
    
    context = {
        'form': form,
        'action': 'Create',
        'submit_text': 'Create Notice'
    }
    return render(request, 'notifications/notice_form.html', context)


@login_required
@admin_required
def notice_update_view(request, pk):
    """Update an existing notice"""
    notice = get_object_or_404(Notice, pk=pk)
    
    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES, instance=notice)
        if form.is_valid():
            form.save()
            messages.success(request, f'Notice "{notice.title}" updated successfully!')
            return redirect('notifications:notice_board')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = NoticeForm(instance=notice)
    
    context = {
        'form': form,
        'notice': notice,
        'action': 'Update',
        'submit_text': 'Update Notice'
    }
    return render(request, 'notifications/notice_form.html', context)


@login_required
@admin_required
def notice_delete_view(request, pk):
    """Delete a notice"""
    notice = get_object_or_404(Notice, pk=pk)
    
    if request.method == 'POST':
        title = notice.title
        notice.delete()
        messages.success(request, f'Notice "{title}" deleted successfully!')
        return redirect('notifications:notice_board')
    
    context = {
        'notice': notice
    }
    return render(request, 'notifications/notice_confirm_delete.html', context)


@login_required
@admin_required
def notification_create_view(request):
    """Create notifications for users"""
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            recipient_type = form.cleaned_data['recipient_type']
            title = form.cleaned_data['title']
            message = form.cleaned_data['message']
            notification_type = form.cleaned_data['notification_type']
            link = form.cleaned_data.get('link', '')
            
            # Determine which users to notify based on recipient_type
            if recipient_type == 'ALL':
                users = User.objects.all()
            elif recipient_type == 'CUSTOM':
                users = form.cleaned_data['users']
                if not users:
                    messages.error(request, 'Please select at least one user for custom selection')
                    return render(request, 'notifications/notification_form.html', {
                        'form': form,
                        'action': 'Create',
                        'submit_text': 'Send Notification'
                    })
            else:
                # Filter by role (ADMIN, TEACHER, STUDENT, PARENT, STAFF)
                users = User.objects.filter(role=recipient_type)
            
            # Create notification and message for each selected user
            created_count = 0
            for user in users:
                Notification.objects.create(
                    user=user,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    link=link
                )
                # Save as Message as well
                Message.objects.create(
                    sender=request.user,
                    recipient=user,
                    subject=title,
                    body=message
                )
                created_count += 1
            
            messages.success(request, f'Successfully sent notification to {created_count} user(s)!')
            return redirect('notifications:notifications')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = NotificationForm()
    
    context = {
        'form': form,
        'action': 'Create',
        'submit_text': 'Send Notification'
    }
    return render(request, 'notifications/notification_form.html', context)
