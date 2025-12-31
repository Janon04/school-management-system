"""
URL configuration for School Management System project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from apps.accounts import views as account_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication
    path('accounts/', include('apps.accounts.urls')),
    
    # Main dashboard
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('dashboard/', account_views.dashboard_view, name='dashboard'),
    
    # App URLs
    path('students/', include('apps.students.urls')),
    path('teachers/', include('apps.teachers.urls')),
    path('parents/', include('apps.parents.urls')),
    path('staff/', include('apps.staff.urls')),
    path('classes/', include('apps.classes.urls')),
    path('attendance/', include('apps.attendance.urls')),
    path('fees/', include('apps.fees.urls')),
    path('exams/', include('apps.exams.urls')),
    path('results/', include('apps.results.urls')),
    path('promotions/', include('apps.promotions.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('config/', include('apps.config.urls')),
    
    # API endpoints
    path('api/', include('config.api_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "School Management System"
admin.site.site_title = "SMS Admin"
admin.site.index_title = "Welcome to School Management System"
