import json

from mayan.apps.documents.document_file_actions import DocumentFileActionUseNewPages
from mayan.apps.documents.tests.literals import TEST_FILE_SMALL_PATH

from ...models import Source

from ..literals import TEST_SOURCE_BACKEND_PATH, TEST_SOURCE_LABEL


class DocumentFileUploadViewTestMixin:
    def _request_document_file_upload_get_view(self):
        return self.get(
            viewname='sources:document_file_upload', kwargs={
                'document_id': self._test_document.pk,
                'source_id': self._test_source.pk,
            }
        )

    def _request_document_file_upload_post_view(self):
        with open(file=TEST_FILE_SMALL_PATH, mode='rb') as file_object:
            return self.post(
                viewname='sources:document_file_upload', kwargs={
                    'document_id': self._test_document.pk,
                    'source_id': self._test_source.pk,
                }, data={
                    'document-action': DocumentFileActionUseNewPages.backend_id,
                    'source-file': file_object
                }
            )

    def _request_document_file_upload_no_source_view(self):
        with open(file=TEST_FILE_SMALL_PATH, mode='rb') as file_object:
            return self.post(
                viewname='sources:document_file_upload', kwargs={
                    'document_id': self._test_document.pk,
                }, data={
                    'document-action': DocumentFileActionUseNewPages.backend_id,
                    'source-file': file_object
                }
            )


class DocumentUploadWizardViewTestMixin:
    def _request_upload_interactive_view(self):
        return self.get(
            viewname='sources:document_upload_interactive', data={
                'document_type_id': self._test_document_type.pk,
            }
        )

    def _request_upload_wizard_view(self, document_path=TEST_FILE_SMALL_PATH):
        with open(file=document_path, mode='rb') as file_object:
            return self.post(
                viewname='sources:document_upload_interactive', kwargs={
                    'source_id': self._test_source.pk
                }, data={
                    'source-file': file_object,
                    'document_type_id': self._test_document_type.pk,
                }
            )


class SourceTestMixin:
    _create_source_method = '_create_test_source'
    _test_source_backend_model = Source
    auto_create_test_source = True

    def setUp(self):
        super().setUp()
        self._test_sources = []

        if self.auto_create_test_source:
            getattr(self, self._create_source_method)()

    def _create_test_source(self, backend_path=None, backend_data=None):
        total_test_sources = len(self._test_sources)
        label = '{}_{}'.format(TEST_SOURCE_LABEL, total_test_sources)

        self._test_source = self._test_source_backend_model.objects.create(
            backend_path=backend_path or TEST_SOURCE_BACKEND_PATH,
            backend_data=json.dumps(obj=backend_data or {}),
            label=label
        )
        self._test_sources.append(self._test_source)


class SourceDocumentUploadViewTestMixin:
    def _request_source_document_upload_view_via_get(self):
        return self.get(
            viewname='sources:document_upload_interactive', kwargs={
                'source_id': self._test_source.pk
            }, data={
                'document_type_id': self._test_document_type.pk,
            }
        )
