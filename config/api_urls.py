"""
API URL Configuration for School Management System
Handles REST API endpoints for all modules
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Create router for API viewsets
router = DefaultRouter()

# Import viewsets will be added as apps are created
# from apps.students.api import StudentViewSet
# router.register(r'students', StudentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]
