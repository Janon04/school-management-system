from django.urls import path
from . import views

urlpatterns = [
    path('school-info/', views.school_info_update_view, name='school_info_update'),
]
