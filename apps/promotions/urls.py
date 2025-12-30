from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    path('', views.promotion_list_view, name='promotion_list'),
    path('get-students-by-class/', views.get_students_by_class, name='get_students_by_class'),
    path('create/', views.promotion_create_view, name='promotion_create'),
    path('<int:pk>/edit/', views.promotion_update_view, name='promotion_update'),
    path('<int:pk>/delete/', views.promotion_delete_view, name='promotion_delete'),
    path('promote/', views.promote_students_view, name='promote_students'),
]
