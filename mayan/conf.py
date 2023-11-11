"""
This module should be called settings.py but is named conf.py to avoid a
clash with the mayan/settings/* module
"""
from django.utils.translation import gettext_lazy as _

from mayan.apps.smart_settings.classes import SettingNamespace

namespace = SettingNamespace(name='mayan', label=_(message='Mayan'))

setting_celery_class = namespace.add_setting(
    help_text=_(message='The class used to instantiate the main Celery app.'),
    global_name='MAYAN_CELERY_CLASS',
    default='celery.Celery'
)
