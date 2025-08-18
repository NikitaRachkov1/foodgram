from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    avatar = models.URLField(blank=True, null=True, verbose_name='Аватар')
    subscriptions = models.ManyToManyField(
        'self',
        through='Subscription',
        symmetrical=False,
        related_name='subscribers',
        verbose_name='Подписки',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions_made',
        verbose_name='подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions_followers',
        verbose_name='автор',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания',
    )

    class Meta:
        unique_together = ('user', 'author')
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
