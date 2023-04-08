import logging

from django.core.files import File
from django.utils.translation import ugettext_lazy as _

from mayan.apps.storage.models import SharedUploadedFile
from mayan.apps.source_apps.sources.classes import SourceBackend
from mayan.apps.source_apps.sources.source_backends.source_backend_mixins import (
    SourceBackendCompressedPeriodicMixin,
    SourceBackendRegularExpressionMixin, SourceBackendStorageBackendMixin
)

__all__ = ('SourceBackendWatchStorage',)
logger = logging.getLogger(name=__name__)


class SourceBackendWatchStorage(
    SourceBackendCompressedPeriodicMixin,
    SourceBackendRegularExpressionMixin, SourceBackendStorageBackendMixin,
    SourceBackend
):
    label = _('Watch storage')

    def get_shared_uploaded_files(self):
        dry_run = self.process_kwargs.get('dry_run', False)

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
                    with storage_backend_instance.open(name=entry, mode='rb') as file_object:
                        shared_uploaded_file = SharedUploadedFile.objects.create(
                            file=File(file=file_object), filename=entry
                        )
                        if not dry_run:
                            storage_backend_instance.delete(
                                name=entry
                            )

                        return (shared_uploaded_file,)
        except Exception as exception:
            message = 'Unable get list of files from source: {}; {}'.format(
                self, exception
            )

            logger.error(message)
            raise ValueError(message) from exception
