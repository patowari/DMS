from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.apps import MayanAppConfig


class SourceCompressedApp(MayanAppConfig):
    app_namespace = 'source_compressed'
    app_url = 'source_compressed'
    name = 'mayan.apps.source_compressed'
    verbose_name = _('Source compressed')
