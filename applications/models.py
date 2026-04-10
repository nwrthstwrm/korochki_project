from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    full_name = models.CharField(
        max_length=255,
        verbose_name='ФИО',
        validators=[
            RegexValidator(
                regex=r'^[А-Яа-я\s]+$',
                message='ФИО должно содержать только буквы кириллицы и пробелы'
            )
        ]
    )
    
    phone = models.CharField(
        max_length=16,
        unique=True,
        verbose_name='Телефон',
        validators=[
            RegexValidator(
                regex=r'^8\([0-9]{3}\)[0-9]{3}-[0-9]{2}-[0-9]{2}$',
                message='Формат телефона: 8(XXX)XXX-XX-XX'
            )
        ]
    )
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True,
        verbose_name='user permissions'
    )
    
    def __str__(self):
        return self.full_name or self.username
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class ApplicationStatus(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Статус')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Статус заявки'
        verbose_name_plural = 'Статусы заявок'

class Application(models.Model):
    COURSE_CHOICES = [
        ('algorithms', 'Основы алгоритмизации и программирования'),
        ('web_design', 'Основы веб-дизайна'),
        ('database_design', 'Основы проектирования баз данных'),
    ]
    
    PAYMENT_METHODS = [
        ('cash', 'Наличными'),
        ('transfer', 'Перевод по номеру телефона'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='Пользователь'
    )
    
    course_name = models.CharField(
        max_length=100,
        choices=COURSE_CHOICES,
        verbose_name='Наименование курса'
    )
    
    desired_start_date = models.DateField(verbose_name='Желаемая дата начала')
    
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        verbose_name='Способ оплаты'
    )
    
    status = models.ForeignKey(
        ApplicationStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applications',
        verbose_name='Статус'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    def __str__(self):
        return f"Заявка #{self.id} - {self.get_course_name_display()}"
    
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']


class Review(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Пользователь'
    )
    
    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='Заявка'
    )
    
    text = models.TextField(verbose_name='Текст отзыва')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отзыва')
    
    def __str__(self):
        return f"Отзыв от {self.user.full_name} на заявку #{self.application.id}"
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'