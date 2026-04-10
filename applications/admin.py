from django.contrib import admin
from .models import User, ApplicationStatus, Application, Review

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'full_name', 'phone', 'email']
    search_fields = ['username', 'full_name']

@admin.register(ApplicationStatus)
class ApplicationStatusAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'course_name', 'desired_start_date', 'status', 'created_at']
    list_filter = ['status', 'payment_method']
    search_fields = ['course_name', 'user__username']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'application', 'created_at']
