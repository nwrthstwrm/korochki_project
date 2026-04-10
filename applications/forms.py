from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import User, Application

class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        label="Логин",
        min_length=5,
        max_length=150,
        help_text="Латинские буквы и цифры, не менее 5 символов",
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9]+$',
                message="Логин может содержать только латинские буквы и цифры"
            )
        ]
    )

    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
        min_length=8,
        help_text="Не менее 8 символов"
    )

    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput
    )

    full_name = forms.CharField(
        label='ФИО',
        max_length=255,
        validators=[
            RegexValidator(
                regex=r'^[А-Яа-я\s]+$',
                message='ФИО должно содержать только буквы кириллицы и пробелы'
            )
        ]
    )

    phone = forms.CharField(
        label='Телефон',
        max_length=16,
        validators=[
            RegexValidator(
                regex=r'^8\([0-9]{3}\)[0-9]{3}-[0-9]{2}-[0-9]{2}$',
                message='Формат: 8(XXX)XXX-XX-XX'
            )
        ]
    )

    email = forms.EmailField(label='Электронная почта')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'full_name', 'phone', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = self.cleaned_data['full_name']
        user.phone = self.cleaned_data['phone']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    
class ApplicationForm(forms.ModelForm):
    desired_start_date = forms.DateField(
        label='Желаемая дата начала обучения',
        input_formats=['%d.%m.%Y', '%Y-%m-%d'],
        widget=forms.TextInput(attrs={'placeholder': 'ДД.ММ.ГГГГ'})
    )
    
    class Meta:
        model = Application
        fields = ['course_name', 'desired_start_date', 'payment_method']
        widgets = {
            'payment_method': forms.RadioSelect(),
        }
        labels = {
            'course_name': 'Наименование курса',
            'payment_method': 'Способ оплаты',
        }
    
    def clean_desired_start_date(self):
        from datetime import date
        start_date = self.cleaned_data.get('desired_start_date')
        if start_date and start_date < date.today():
            raise forms.ValidationError('Дата начала не может быть в прошлом')
        return start_date