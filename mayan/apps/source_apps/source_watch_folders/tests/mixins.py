import shutil

from mayan.apps.documents.tests.literals import TEST_FILE_SMALL_PATH
from mayan.apps.storage.utils import fs_cleanup, mkdtemp
from mayan.apps.source_apps.sources.source_backends.literals import (
    DEFAULT_PERIOD_INTERVAL, SOURCE_UNCOMPRESS_CHOICE_NEVER
)
from mayan.apps.source_apps.sources.tests.mixins.base import SourceTestMixin
from mayan.apps.source_apps.sources.tests.mixins.source_view_mixins import SourceViewTestMixin

from ..source_backends import SourceBackendWatchFolder

from .literals import TEST_SOURCE_BACKEND_WATCH_FOLDER_PATH


class WatchFolderSourceBackendTestMixin(SourceTestMixin):
    _create_source_method = '_create_test_watch_folder'

    def setUp(self):
        self._temporary_folders = []
        super().setUp()
        self._test_staging_folder_files = []

    def tearDown(self):
        for temporary_folders in self._temporary_folders:
            fs_cleanup(filename=temporary_folders)

        super().tearDown()

    def _create_test_watch_folder(self, extra_data=None):
        temporary_folder = mkdtemp()
        self._temporary_folders.append(temporary_folder)
        backend_data = {
            'document_type_id': self._test_document_type.pk,
            'folder_path': temporary_folder,
            'include_subdirectories': False,
            'interval': DEFAULT_PERIOD_INTERVAL,
            'uncompress': SOURCE_UNCOMPRESS_CHOICE_NEVER
        }

        if extra_data:
            backend_data.update(extra_data)

        self._create_test_source(
            backend_data=backend_data,
            backend_path=SourceBackendWatchFolder.get_class_path()
        )

    def _copy_test_watch_folder_document(self):
        shutil.copy(
            src=TEST_FILE_SMALL_PATH,
            dst=self._test_source.get_backend_data()['folder_path']
        )


class WatchFolderSourceBackendViewTestMixin(SourceViewTestMixin):
    def _request_test_watch_folder_source_create_view(self):
        temporary_folder = mkdtemp()
        self._temporary_folders.append(temporary_folder)

        return self._request_test_source_create_view(
            backend_path=TEST_SOURCE_BACKEND_WATCH_FOLDER_PATH,
            extra_data={
                'document_type_id': self._test_document_type.pk,
                'folder_path': temporary_folder,
                'include_subdirectories': False,
                'interval': DEFAULT_PERIOD_INTERVAL,
                'uncompress': SOURCE_UNCOMPRESS_CHOICE_NEVER
            }
        )
