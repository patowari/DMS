from unittest.mock import patch

from mayan.apps.documents.models import Document
from mayan.apps.documents.tests.base import GenericDocumentTestCase
from mayan.apps.documents.tests.literals import (
    TEST_DOCUMENT_SMALL_CHECKSUM, TEST_FILE_SMALL_PATH
)
from mayan.apps.source_apps.sources.tests.mixins.interactive_source_mixins import InteractiveSourceBackendTestMixin

from .mixins import StagingStorageTestMixin


class StagingStorageSourceBackendTestCase(
    StagingStorageTestMixin, InteractiveSourceBackendTestMixin,
    GenericDocumentTestCase
):
    auto_create_test_source = False
    auto_upload_test_document = False

    def _process_test_document(self, test_file_path=TEST_FILE_SMALL_PATH):
        source_backend_instance = self._test_source.get_backend_instance()

        self.test_forms = {
            'document_form': self._test_document_form,
            'source_form': InteractiveSourceBackendTestMixin.MockSourceForm(
                staging_source_file_id=self.test_staging_storage_file.encoded_filename
            )
        }

        source_backend_instance.process_documents(
            document_type=self._test_document_type, forms=self.test_forms,
            request=self.get_test_request()
        )

    def test_upload_simple_file(self):
        self._create_test_staging_storage()

        self._copy_test_staging_storage_document()

        document_count = Document.objects.count()

        self._process_test_document()

        self.assertEqual(Document.objects.count(), document_count + 1)
        self.assertEqual(
            Document.objects.first().file_latest.checksum,
            TEST_DOCUMENT_SMALL_CHECKSUM
        )

    @patch('mayan.apps.source_apps.sources.source_backends.source_backend_mixins.SourceBackendMixinInteractive.callback')
    def test_super_class_callback(self, mocked_super):
        self._create_test_staging_storage()

        self._copy_test_staging_storage_document()

        document_count = Document.objects.count()

        self._process_test_document()

        self.assertEqual(Document.objects.count(), document_count + 1)
        self.assertEqual(
            Document.objects.first().file_latest.checksum,
            TEST_DOCUMENT_SMALL_CHECKSUM
        )

        self.assertTrue(mocked_super.called)

    def test_delete_after_upload(self):
        self._create_test_staging_storage(
            extra_data={'delete_after_upload': True}
        )

        self._copy_test_staging_storage_document()

        document_count = Document.objects.count()

        self._process_test_document()

        self.assertEqual(Document.objects.count(), document_count + 1)
        self.assertEqual(
            Document.objects.first().file_latest.checksum,
            TEST_DOCUMENT_SMALL_CHECKSUM
        )

        self.assertEqual(
            self._test_source.get_backend_instance().get_storage_backend_instance().listdir(''),
            ([], [])
        )
