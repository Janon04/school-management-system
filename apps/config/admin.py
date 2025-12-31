from django.contrib import admin
from .models import SchoolInfo

@admin.register(SchoolInfo)
class SchoolInfoAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "phone", "email", "headmaster", "updated_at")
    search_fields = ("name", "address", "phone", "email")
