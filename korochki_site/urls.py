from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from applications import views
from django.contrib.auth.views import LogoutView

def home(request):
    return render(request, 'home.html')

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('applications/', views.applications_list, name='applications_list'),
    path('create/', views.create_application, name='create_application'),
]
