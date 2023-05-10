from django import forms
from django.contrib import admin
from django.contrib.auth import admin as admin_auth
from django.contrib.auth import get_user_model, models
from django.core import exceptions

from .models import Subscriptions

User = get_user_model()


class UserCreationForm(forms.ModelForm):
    email = forms.EmailField(label='Почта')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля',
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise exceptions.ValidationError('Пароли не совпадают!')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get('password1'))
        if commit:
            user.save()
        return user


class UserAdmin(admin_auth.UserAdmin):
    add_form = UserCreationForm

    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_staff'
    )
    list_filter = ('email', 'username')
    fieldsets = (
        ('Данные профиля', {'fields': ('username', 'email', 'password',)}),
        ('Персональные данные', {'fields': ('first_name', 'last_name',)}),
        ('Права доступа', {'fields': ('is_staff',)}),
    )
    search_fields = ('^email', '^username')
    ordering = ('email',)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('author', 'subscriber')


admin.site.unregister(models.Group)
admin.site.register(User, UserAdmin)
admin.site.register(Subscriptions, SubscriptionAdmin)
