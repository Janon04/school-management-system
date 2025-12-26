from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    path('', views.promotion_list_view, name='promotion_list'),
    path('promote/', views.promote_students_view, name='promote_students'),
]
