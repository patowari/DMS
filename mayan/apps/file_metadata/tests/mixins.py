from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from mayan.apps.documents.tests.mixins.document_mixins import (
    DocumentTestMixin
)
from mayan.apps.documents.tests.mixins.document_type_mixins import (
    DocumentTypeTestMixin
)

from ..classes import FileMetadataDriver

from .literals import (
    TEST_DRIVER_CLASS_PATH, TEST_FILE_METADATA_KEY, TEST_FILE_METADATA_VALUE
)


class FileMetadataTestMixin:
    _test_document_file_metadata_driver_path = TEST_DRIVER_CLASS_PATH
    _test_document_file_metadata_driver_create_auto = False

    def setUp(self):
        super().setUp()

        if self._test_document_file_metadata_driver_create_auto:
            FileMetadataDriver.load_modules()

            self._test_document_file_metadata_driver = import_string(
                dotted_path=self._test_document_file_metadata_driver_path
            )
            self._test_document_file_metadata_driver.do_model_instance_populate()


class DocumentTypeMetadataTestMixin(
    DocumentTypeTestMixin, FileMetadataTestMixin
):
    _test_document_file_metadata_driver_enable_auto = False

    def setUp(self):
        super().setUp()

        if self._test_document_file_metadata_driver_enable_auto:
            self._test_file_metadata_driver_enable()
        else:
            self._test_file_metadata_driver_disable()

    def _test_file_metadata_driver_disable(self):
        self._test_document_file_metadata_driver.model_instance.document_type_configurations.filter(
            document_type=self._test_document_type
        ).update(enabled=False)

    def _test_file_metadata_driver_enable(self):
        self._test_document_file_metadata_driver.model_instance.document_type_configurations.filter(
            document_type=self._test_document_type
        ).update(enabled=True)


class DocumentFileMetadataTestMixin(
    DocumentTestMixin, DocumentTypeMetadataTestMixin
):
    _test_document_file_metadata_entry_create_auto = False

    def setUp(self):
        super().setUp()

        if self._test_document_file_metadata_entry_create_auto:
            if not self._test_document_file_metadata_driver_create_auto:
                raise ImproperlyConfigured(
                    'Must enable creation of the test file metadata driver '
                    'in order to create test file metadata entries.'
                )
            else:
                self._test_document_file_metadata_entry_create()

    def _test_document_file_metadata_entry_create(self):
        self._test_document_file_driver_entry, created = self._test_document_file.file_metadata_drivers.get_or_create(
            driver=self._test_document_file_metadata_driver.model_instance
        )

        self._test_document_file_metadata = self._test_document_file_driver_entry.entries.create(
            key=TEST_FILE_METADATA_KEY,
            value=TEST_FILE_METADATA_VALUE
        )

        self._test_document_file_metadata_path = '{}__{}'.format(
            self._test_document_file_driver_entry.driver.internal_name,
            self._test_document_file_metadata.key
        )


class DocumentFileMetadataViewTestMixin(DocumentFileMetadataTestMixin):
    def _request_document_file_metadata_driver_list_view(self):
        return self.get(
            viewname='file_metadata:document_file_metadata_driver_list',
            kwargs={'document_file_id': self._test_document_file.pk}
        )

    def _request_document_file_metadata_driver_attribute_list_view(self):
        return self.get(
            viewname='file_metadata:document_file_metadata_driver_attribute_list',
            kwargs={
                'document_file_driver_id': self._test_document_file_driver_entry.pk
            }
        )

    def _request_document_file_metadata_single_submit_view(self):
        return self.post(
            viewname='file_metadata:document_file_metadata_single_submit',
            kwargs={'document_file_id': self._test_document_file.pk}
        )

    def _request_document_file_multiple_submit_view(self):
        return self.post(
            viewname='file_metadata:document_file_metadata_multiple_submit',
            data={
                'id_list': self._test_document_file.pk
            }
        )


class DocumentTypeViewTestMixin(DocumentTypeMetadataTestMixin):
    def _request_document_type_file_metadata_driver_configuration_edit_view(self):
        return self.post(
            data={'enabled': False}, kwargs={
                'document_type_id': self._test_document_type.pk,
                'stored_driver_id': self._test_document_file_metadata_driver.model_instance.pk
            }, viewname='file_metadata:document_type_file_metadata_driver_configuration_edit'
        )

    def _request_document_type_file_metadata_driver_configuration_list_view(self):
        return self.get(
            kwargs={'document_type_id': self._test_document_type.pk},
            viewname='file_metadata:document_type_file_metadata_driver_configuration_list'
        )

    def _request_document_type_file_metadata_submit_view(self):
        return self.post(
            viewname='file_metadata:document_type_file_metadata_submit', data={
                'document_type': self._test_document_type.pk,
            }
        )


class FileMetadataDriverTestMixin(FileMetadataTestMixin):
    def _request_file_metadata_driver_list_view(self):
        return self.get(viewname='file_metadata:file_metadata_driver_list')
