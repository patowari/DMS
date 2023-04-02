from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.apps import MayanAppConfig


class SourceSaneScannersApp(MayanAppConfig):
    app_namespace = 'source_sane_scanners'
    app_url = 'source_sane_scanners'
    has_rest_api = False
    has_static_media = False
    has_tests = True
    name = 'mayan.apps.source_apps.source_sane_scanners'
    verbose_name = _('SANE scanners')
