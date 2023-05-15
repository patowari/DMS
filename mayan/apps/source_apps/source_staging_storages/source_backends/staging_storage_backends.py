import logging

from django.utils.translation import ugettext_lazy as _

from mayan.apps.appearance.classes import Icon
from mayan.apps.source_apps.source_staging_folders.source_backends.staging_source_mixins import SourceBackendMixinFileList
from mayan.apps.source_apps.sources.classes import SourceBackend
from mayan.apps.source_apps.sources.source_backends.source_backend_mixins import (
    SourceBackendMixinCompressed, SourceBackendMixinInteractive,
    SourceBackendMixinRegularExpression, SourceBackendMixinStorageBackend
)

from .staging_storage_files import StagingStorageFile

__all__ = ('SourceBackendStagingStorage',)
logger = logging.getLogger(name=__name__)


class SourceBackendStagingStorage(
    SourceBackendMixinCompressed, SourceBackendMixinInteractive,
    SourceBackendMixinRegularExpression, SourceBackendMixinFileList,
    SourceBackendMixinStorageBackend, SourceBackend
):
    icon = Icon(
        driver_name='fontawesome', symbol='file'
    )
    label = _('Staging storage')
    staging_source_file_class = StagingStorageFile

    def get_files(self):
        exclude_regex = self.get_regex_exclude()
        include_regex = self.get_regex_include()

        storage_backend_instance = self.get_storage_backend_instance()

        try:
            # Specify '' with no argument name for compatibility. Django
            # requires a `path` argument while boto3 requires a `name`
            # argument.
            folders, entries = storage_backend_instance.listdir('')

            for entry in entries:
                if include_regex.match(string=str(entry)) and not exclude_regex.match(string=str(entry)):
                    yield self.get_file(filename=entry)
        except Exception as exception:
            message = 'Unable get list of staging files from source: {}; {}'.format(
                self, exception
            )

            logger.error(message)
            raise ValueError(message) from exception
