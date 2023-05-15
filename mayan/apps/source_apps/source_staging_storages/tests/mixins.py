import json
import shutil

from mayan.apps.documents.tests.literals import TEST_FILE_SMALL_PATH
from mayan.apps.source_apps.source_staging_folders.tests.literals import (
    TEST_STAGING_PREVIEW_HEIGHT, TEST_STAGING_PREVIEW_WIDTH
)
from mayan.apps.source_apps.sources.source_backends.literals import SOURCE_UNCOMPRESS_CHOICE_NEVER
from mayan.apps.source_apps.sources.tests.mixins.base import SourceTestMixin
from mayan.apps.storage.utils import fs_cleanup, mkdtemp

from ..source_backends.staging_storage_backends import SourceBackendStagingStorage


class StagingStorageActionAPIViewTestMixin:
    def _request_test_staging_storage_file_delete_action_api_view(self):
        return self.post(
            viewname='rest_api:source-action', kwargs={
                'action_name': 'file_delete',
                'source_id': self._test_source.pk
            }, data={
                'arguments': json.dumps(
                    obj={
                        'encoded_filename': self.test_staging_storage_file.encoded_filename
                    }
                )
            }
        )

    def _request_test_staging_storage_file_image_action_api_view(self):
        return self.get(
            viewname='rest_api:source-action', kwargs={
                'action_name': 'file_image',
                'source_id': self._test_source.pk
            }, query={
                'encoded_filename': self.test_staging_storage_file.encoded_filename
            }
        )

    def _request_test_staging_storage_file_list_action_api_view(self):
        return self.get(
            viewname='rest_api:source-action', kwargs={
                'action_name': 'file_list',
                'source_id': self._test_source.pk
            }
        )

    def _request_test_staging_storage_file_upload_action_api_view(
        self, extra_kwargs=None
    ):
        kwargs = {
            'document_type_id': self._test_document_type.pk,
            'encoded_filename': self.test_staging_storage_file.encoded_filename
        }

        if extra_kwargs is not None:
            kwargs.update(extra_kwargs)

        return self.post(
            viewname='rest_api:source-action', kwargs={
                'action_name': 'file_upload',
                'source_id': self._test_source.pk
            }, data={
                'arguments': json.dumps(obj=kwargs)
            }
        )


class StagingStorageTestMixin(SourceTestMixin):
    _create_source_method = '_create_test_staging_storage'

    def setUp(self):
        self._temporary_storages = []
        super().setUp()
        self.test_staging_storage_files = []

    def tearDown(self):
        for temporary_storages in self._temporary_storages:
            fs_cleanup(filename=temporary_storages)

        super().tearDown()

    def _create_test_staging_storage(self, extra_data=None):
        temporary_storage = mkdtemp()
        self._temporary_storages.append(temporary_storage)
        backend_data = {
            'preview_height': TEST_STAGING_PREVIEW_HEIGHT,
            'preview_width': TEST_STAGING_PREVIEW_WIDTH,
            'storage_backend': 'django.core.files.storage.FileSystemStorage',
            'storage_backend_arguments': '{{\'location\': \'{}\'}}'.format(
                temporary_storage
            ),
            'uncompress': SOURCE_UNCOMPRESS_CHOICE_NEVER
        }

        if extra_data:
            backend_data.update(extra_data)

        self._create_test_source(
            backend_path=SourceBackendStagingStorage.get_class_path(),
            backend_data=backend_data
        )
        self._test_source._test_temporary_storage = temporary_storage

    def _copy_test_staging_storage_document(self):
        shutil.copy(
            src=TEST_FILE_SMALL_PATH,
            dst=self._test_source._test_temporary_storage
        )
        self.test_staging_storage_file = list(
            self._test_source.get_backend_instance().get_files()
        )[0]
        self.test_staging_storage_files.append(
            self.test_staging_storage_file
        )


class StagingStorageViewTestMixin:
    def _request_staging_storage_action_file_delete_view_via_get(self):
        return self.get(
            viewname='sources:source_action', kwargs={
                'action_name': 'file_delete',
                'source_id': self._test_source.pk
            }, query={
                'encoded_filename': self.test_staging_storage_file.encoded_filename
            }
        )

    def _request_staging_storage_action_file_delete_view_via_post(self):
        return self.post(
            viewname='sources:source_action', kwargs={
                'action_name': 'file_delete',
                'source_id': self._test_source.pk
            }, query={
                'encoded_filename': self.test_staging_storage_file.encoded_filename
            }
        )
