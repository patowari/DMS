from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.apps import MayanAppConfig


class SourceWebFormsApp(MayanAppConfig):
    app_namespace = 'source_web_forms'
    app_url = 'source_web_forms'
    has_rest_api = False
    has_static_media = False
    has_tests = True
    name = 'mayan.apps.source_apps.source_web_forms'
    verbose_name = _('Web form sources')
