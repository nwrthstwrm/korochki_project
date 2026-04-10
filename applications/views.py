from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.template.loader import render_to_string
from .forms import RegistrationForm, ApplicationForm
from .models import User, Application, ApplicationStatus, Review
from django.contrib.auth import logout

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('applications_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.full_name}!')
                return redirect('applications_list')
            else:
                messages.error(request, 'Неверный логин или пароль')
        else:
            messages.error(request, 'Неверный логин или пароль')
    
    form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('login')

@login_required
def create_application(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            
            new_status, created = ApplicationStatus.objects.get_or_create(name='Новая')
            application.status = new_status
            
            application.save()
            messages.success(request, 'Заявка успешно отправлена!')
            return redirect('applications_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ApplicationForm()
    
    return render(request, 'applications/create_application.html', {'form': form})

@login_required
def applications_list(request):
    applications = Application.objects.filter(user=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        review_text = request.POST.get('review_text')
        
        if application_id and review_text:
            try:
                application = Application.objects.get(id=application_id, user=request.user)
                if application.status.name == 'Обучение завершено':
                    if not hasattr(application, 'review'):
                        Review.objects.create(
                            user=request.user,
                            application=application,
                            text=review_text
                        )
                        messages.success(request, 'Спасибо за ваш отзыв!')
                    else:
                        messages.error(request, 'Отзыв для этой заявки уже оставлен')
                else:
                    messages.error(request, 'Отзыв можно оставить только после завершения обучения')
            except Application.DoesNotExist:
                messages.error(request, 'Заявка не найдена')
        
        return redirect('applications_list')
    
    return render(request, 'applications/applications_list.html', {'applications': applications})

def is_admin_user(user):
    return user.username == 'Admin' and user.is_authenticated

@user_passes_test(is_admin_user, login_url='/login/')
def admin_panel(request):
    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        new_status_name = request.POST.get('new_status')
        
        if application_id and new_status_name:
            try:
                application = Application.objects.get(id=application_id)
                new_status = ApplicationStatus.objects.get(name=new_status_name)
                application.status = new_status
                application.save()
                messages.success(request, f'Статус заявки #{application_id} изменён на "{new_status_name}"')
            except Application.DoesNotExist:
                messages.error(request, 'Заявка не найдена')
            except ApplicationStatus.DoesNotExist:
                messages.error(request, 'Статус не найден')
        
        return redirect('admin_panel')
    
    applications = Application.objects.all().order_by('-created_at')
    
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        applications = applications.filter(status__name=status_filter)
    
    paginator = Paginator(applications, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    statuses = ApplicationStatus.objects.all()
    
    return render(request, 'applications/admin_panel.html', {
        'applications': page_obj,
        'statuses': statuses
    })