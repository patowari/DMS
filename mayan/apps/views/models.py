from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserViewSettings(models.Model):
    mode = models.CharField(
        max_length=4, verbose_name=_(message='Mode')
    )
    view_name = models.CharField(
        db_index=True, max_length=200, verbose_name=_(message='Name')
    )
    user = models.ForeignKey(
        on_delete=models.CASCADE, related_name='view_settings',
        to=settings.AUTH_USER_MODEL, verbose_name=_(message='User')
    )

    class Meta:
        ordering = ('user__username',)
        verbose_name = _(message='User view configuration')
        verbose_name_plural = _(message='User view configurations')
