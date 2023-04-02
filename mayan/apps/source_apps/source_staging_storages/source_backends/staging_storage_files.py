import logging

from django.utils.functional import cached_property

from mayan.apps.source_apps.source_staging_folders.source_backends.staging_source_files import StagingSourceFile

logger = logging.getLogger(name=__name__)


class StagingStorageFile(StagingSourceFile):
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

        self.storage_backend_instance.delete(
            name=self.get_full_path()
        )

    def get_full_path(self):
        return self.filename

    def open(self, file, mode):
        return self.storage_backend_instance.open(name=file, mode=mode)

    @cached_property
    def storage_backend_instance(self):
        return self.staging_source.get_storage_backend_instance()
