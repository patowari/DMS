from django.core.files.base import ContentFile

from mayan.apps.sources.classes import SourceBackend

from ..source_backend_actions.periodic_actions import SourceBackendActionPeriodicDocumentUpload
from ..source_backends.periodic_mixins import (
    SourceBackendMixinPeriodic
)


class SourceBackendTestPeriodic(SourceBackendMixinPeriodic, SourceBackend):
    action_class_list = (SourceBackendActionPeriodicDocumentUpload,)
    label = 'Test periodic source backend'

    def action_file_delete(self, encoded_filename):
        return

    def action_file_get(self, encoded_filename):
        yield ContentFile('')

    def get_file_identifier(self):
        return ''

    def get_stored_file_list(self):
        yield ''
