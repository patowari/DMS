from django.utils.translation import gettext_lazy as _

from mayan.apps.app_manager.apps import MayanAppConfig


class ViewsApp(MayanAppConfig):
    app_namespace = 'views'
    app_url = 'views'
    has_tests = True
    name = 'mayan.apps.views'
    verbose_name = _(message='Views')
