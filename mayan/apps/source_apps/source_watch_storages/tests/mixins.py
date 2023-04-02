import shutil

from mayan.apps.documents.tests.literals import TEST_FILE_SMALL_PATH
from mayan.apps.storage.utils import fs_cleanup, mkdtemp
from mayan.apps.source_apps.sources.source_backends.literals import (
    DEFAULT_PERIOD_INTERVAL, SOURCE_UNCOMPRESS_CHOICE_NEVER
)
from mayan.apps.source_apps.sources.tests.mixins.base_mixins import SourceTestMixin

from ..source_backends import SourceBackendWatchStorage


class WatchStorageSourceTestMixin(SourceTestMixin):
    _create_source_method = '_create_test_watch_storage'

    def setUp(self):
        self._temporary_storages = []
        super().setUp()

    def tearDown(self):
        for temporary_storages in self._temporary_storages:
            fs_cleanup(filename=temporary_storages)

        super().tearDown()

    def _create_test_watch_storage(self, extra_data=None):
        temporary_folder = mkdtemp()
        self._temporary_storages.append(temporary_folder)
        backend_data = {
            'document_type_id': self._test_document_type.pk,
            'storage_backend': 'django.core.files.storage.FileSystemStorage',
            'storage_backend_arguments': '{{\'location\': \'{}\'}}'.format(
                temporary_folder
            ),
            'interval': DEFAULT_PERIOD_INTERVAL,
            'uncompress': SOURCE_UNCOMPRESS_CHOICE_NEVER
        }

        if extra_data:
            backend_data.update(extra_data)

        self._create_test_source(
            backend_path=SourceBackendWatchStorage.get_class_path(),
            backend_data=backend_data
        )

        self._test_source._test_temporary_folder = temporary_folder

    def _copy_test_watch_storage_document(self):
        shutil.copy(
            src=TEST_FILE_SMALL_PATH,
            dst=self._test_source._test_temporary_folder
        )
