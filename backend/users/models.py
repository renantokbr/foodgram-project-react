from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Length

models.CharField.register_lookup(Length)


class User(AbstractUser):
    """Модель пользователя."""
    email = models.EmailField(
        'Электронная почта',
        max_length=settings.USER_EMAIL_FIELD_LENG,
        unique=True)
    first_name = models.CharField(
        'Имя',
        max_length=settings.USER_CHAR_FIELD_LENG,
        blank=False)
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.USER_CHAR_FIELD_LENG,
        blank=False)
    username = models.CharField(
        'Уникальное имя',
        max_length=settings.USER_CHAR_FIELD_LENG, )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email', 'first_name', 'last_name')

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    """Модель пользовательских подписок."""
    author = models.ForeignKey(
        to=User,
        verbose_name='Автор рецепта',
        related_name='follower',
        on_delete=models.CASCADE,)
    user = models.ForeignKey(
        to=User,
        verbose_name='Подписчики',
        related_name='following',
        on_delete=models.CASCADE,)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'user'),
                name='\nУже подписаны на этого пользователя!\n',
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='\nНельзя подписываться на себя!\n'
            )
        )

    def __str__(self):
        return f'{self.author.username} -> {self.user.username}'
