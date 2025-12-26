from django.contrib import admin
from .models import Notice, Notification, Message


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'target_audience', 'priority', 'posted_by', 'is_active', 'created_at']
    list_filter = ['target_audience', 'priority', 'is_active', 'created_at']
    search_fields = ['title', 'message']
    autocomplete_fields = ['posted_by']
    
    fieldsets = (
        ('📢 Notice Information', {
            'fields': ('title', 'message'),
        }),
        ('🎯 Audience & Priority', {
            'fields': ('target_audience', 'priority'),
        }),
        ('✅ Status', {
            'fields': ('is_active', 'posted_by'),
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'title', 'message']
    autocomplete_fields = ['user']
    
    fieldsets = (
        ('👤 Recipient', {
            'fields': ('user',),
        }),
        ('📬 Notification Details', {
            'fields': ('title', 'message', 'notification_type'),
        }),
        ('✅ Status', {
            'fields': ('is_read',),
        }),
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'subject', 'is_read', 'sent_at']
    list_filter = ['is_read', 'sent_at']
    search_fields = ['sender__username', 'sender__first_name', 'recipient__username', 'recipient__first_name', 'subject']
    autocomplete_fields = ['sender', 'recipient']
    
    fieldsets = (
        ('📨 Message Details', {
            'fields': ('sender', 'recipient', 'subject'),
        }),
        ('📝 Content', {
            'fields': ('body',),
        }),
        ('✅ Status', {
            'fields': ('is_read',),
        }),
    )
